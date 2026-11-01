"""The water-body layer (app/place/water.py): bodies from an occurrence raster, names from OSM points and the yaml
overrides, the lookups the answers and maps use. No network."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from rasterio.transform import from_origin

from app.place import answer as A
from app.place import water as W


def _occ() -> tuple[np.ndarray, object]:
    """A 40x40 occurrence raster at ~30 m: a permanent pond (80%), a seasonal lake (20%) with a permanent core
    (60%), a one-pixel speck, and no-data (255) in a corner."""
    occ = np.zeros((40, 40), dtype="uint8")
    occ[5:10, 5:10] = 80                       # the pond: 25 px ~ 2 ha
    occ[20:35, 20:35] = 20                     # the seasonal lake
    occ[26:29, 26:29] = 60                     # its permanent core
    occ[2, 30] = 90                            # a speck
    occ[36:, 36:] = 255
    tr = from_origin(5.0, 13.0, 0.00027, 0.00027)
    return occ, tr


def test_bodies_come_from_connected_pixels_over_the_threshold() -> None:
    occ, tr = _occ()
    bodies = W.bodies_from(occ, tr)
    assert len(bodies) == 2                                       # the speck (0.09 ha) is dropped
    pond, core = sorted(bodies, key=lambda b: -b.area_ha)
    assert 1.8 < pond.area_ha < 2.4 and pond.occurrence == 80.0 and not pond.seasonal
    assert 0.6 < core.area_ha < 0.9 and core.occurrence == 60.0
    seasonal = W.bodies_from(occ, tr, min_ha=1.0, threshold=W.SEASONAL_OCCURRENCE, seasonal=True, first_id=3)
    assert len(seasonal) == 2 and seasonal[0].id == 3 and all(b.seasonal for b in seasonal)
    lake = max(seasonal, key=lambda b: b.area_ha)
    assert 15 < lake.area_ha < 22 and 20 < lake.occurrence < 30        # the core's pixels raise the mean a little


def test_names_from_osm_and_the_yaml_overrides_and_the_lookups(tmp_path: Path) -> None:
    occ, tr = _occ()
    bodies = W.bodies_from(occ, tr) + W.bodies_from(occ, tr, min_ha=1.0, threshold=W.SEASONAL_OCCURRENCE, seasonal=True,
                                                    first_id=3)
    lay = W.WaterLayer(bodies)
    pond = lay.at(5.0 + 7.5 * 0.00027, 13.0 - 7.5 * 0.00027)
    assert pond is not None and not pond.seasonal and pond.occurrence == 80.0
    core_lon, core_lat = 5.0 + 27.5 * 0.00027, 13.0 - 27.5 * 0.00027
    assert lay.at(core_lon, core_lat).occurrence == 60.0             # the permanent core before the lake around it
    assert lay.at(core_lon, core_lat, seasonal=False).occurrence == 60.0
    edge_lon, edge_lat = 5.0 + 22 * 0.00027, 13.0 - 22 * 0.00027     # in the lake, outside the core
    assert lay.at(edge_lon, edge_lat).seasonal and lay.at(edge_lon, edge_lat, seasonal=False) is None
    hit = lay.nearest(5.0 + 12 * 0.00027, 13.0 - 7 * 0.00027, 500)   # 2 px east of the pond
    assert hit[0] is pond and 40 < hit[1] < 80
    assert lay.nearest(5.0 + 12 * 0.00027, 13.0 - 7 * 0.00027, 30) is None
    osm = [{"name": "Lake Big", "name_ha": "Tafkin Big", "kind": "lake", "lat": edge_lat, "lon": edge_lon},
           {"name": "Far Pond", "name_ha": "", "kind": "pond", "lat": 13.0 - 2 * 0.00027, "lon": 5.0 + 38 * 0.00027}]
    counts = W.name_bodies(bodies, osm, [{"name": "Our Pond", "name_ha": "Tafkinmu", "lat": 13.0 - 7.5 * 0.00027,
                                           "lon": 5.0 + 7.5 * 0.00027, "radius_km": 1}])
    assert counts == {"osm": 1, "yaml": 1}                            # Far Pond is beyond NAME_REACH_M of anything
    assert pond.name == "Our Pond" and pond.source == "yaml"
    assert lay.name_near(core_lon, core_lat, "en") == "Lake Big"     # the unnamed core takes its lake's name
    assert lay.name_near(core_lon, core_lat, "ha") == "Tafkin Big"
    assert lay.name_near(5.0 + 7.5 * 0.00027, 13.0 - 7.5 * 0.00027, "ha") == "Tafkinmu"
    assert lay.name_near(5.0 + 2 * 0.00027, 13.0 - 38 * 0.00027, "en") == ""
    out = tmp_path / "w.geojson"
    W.write(bodies, out)
    again = W.load(out)
    assert len(again) == 4 and again.named == 2 and again.at(core_lon, core_lat).occurrence == 60.0
    assert json.loads(out.read_text(encoding="utf-8"))["features"][0]["properties"]["seasonal"] is False
    assert len(W.load(tmp_path / "missing.geojson")) == 0


def test_the_yaml_rule_on_its_own_and_the_answer_wording(tmp_path: Path) -> None:
    y = tmp_path / "wb.yaml"
    y.write_text("- name: Kware Lake\n  name_ha: tafkin Kware\n  lat: 13.228\n  lon: 5.274\n  radius_km: 2\n", encoding="utf-8")
    assert W.override_name(13.229, 5.275, "ha", y) == "tafkin Kware" and W.override_name(13.3, 5.4, "en", y) == ""
    assert A.water_body_name(13.229, 5.275, "en", y) == "Kware Lake"
    from tests.test_place_answer import _history
    h = _history(nearest={"distance_m": 1200, "area_ha": 3.4, "occurrence": 70, "lat": 13.1, "lon": 5.2, "name": "Toidi Lake",
                          "name_ha": ""})
    s = A.nearest_sentence(h, "en")
    assert s.startswith(" The nearest water body is Toidi Lake, 1.2 km from your pin (3.4 ha")
    assert "Tafkin ruwa mafi kusa shi ne Toidi Lake, kilomita 1.2" in A.nearest_sentence(h, "ha")
    h.nearest_water["name"] = ""
    assert A.nearest_sentence(h, "en").startswith(" The nearest water body is 1.2 km from your pin")
