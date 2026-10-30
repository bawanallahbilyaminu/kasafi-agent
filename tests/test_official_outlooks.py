"""The official outlook loader's table reader (scripts/official_outlooks.py) on the two ways OCR prints a table:
the server's OCR of NiMet SCP p91 put a pipe before the state and kept an empty state cell under it."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("official_outlooks",
                                              Path(__file__).parents[1] / "scripts" / "official_outlooks.py")
oo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oo)

LOCAL = """Port Harcourt | 21.8 | 23.0 | 23.7 | 23.5 | 23.7
Sokoto | Gudu North | 16.6 | 19.1 | 22.2 | 27.0 | 28.3
| Illela | 16.2 | 18.7 | 21.9 | 26.6 | 27.8
| Sokoto | 17.0 | 20.0 | 24.0 | 27.4 | 27.7
Taraba | Bali | 19.7 | 21.8 | 23.8 | 24.9 | 23.9"""
SERVER = """| | Port Harcourt | 21.8 | 23.0 | 23.7 | 23.5 | 23.7 |
| Sokoto | Gudu North | 16.6 | 19.1 | 22.2 | 27.0 | 28.3 |
| | Illela | 16.2 | 18.7 | 21.9 | 26.6 | 27.8 |
| | Sokoto | 17.0 | 20.0 | 24.0 | 27.4 | 27.7 |
| Taraba | Bali | 19.7 | 21.8 | 23.8 | 24.9 | 23.9 |"""
WANT = [("Gudu North", ["16.6", "19.1", "22.2", "27.0", "28.3"]), ("Illela", ["16.2", "18.7", "21.9", "26.6", "27.8"]),
        ("Sokoto", ["17.0", "20.0", "24.0", "27.4", "27.7"])]


def test_both_ocr_layouts_give_the_same_rows() -> None:
    assert oo.table_rows([LOCAL], "Sokoto", 5) == WANT
    assert oo.table_rows([SERVER], "Sokoto", 5) == WANT


def test_a_block_runs_across_pages_and_stops_at_the_next_state() -> None:
    first = "Rivers | Tai | 05-Mar | 16-Dec | 286 | 2736\nSokoto | Binji | 09-Jul | 17-Sept | 70 | 601"
    second = "| Bodinga | 04-Jul | 20-Sept | 78 | 586\nTaraba | Bali | 30-Apr | 29-Oct | 182 | 1241"
    assert oo.table_rows([first, second], "Sokoto", 4) == [("Binji", ["09-Jul", "17-Sept", "70", "601"]),
                                                           ("Bodinga", ["04-Jul", "20-Sept", "78", "586"])]
