# Emergency fast path eval

- must fire: 44/44 fired (before consent, phrase list only: 44/44)
- must not fire: 44/44 quiet (before consent: 39/44)
- decided by: phrase list 44, classifier 7, neither 37
- classifier time: median 2.22 s, max 2.80 s
- fast path end to end (handler, PostGIS, no ORS): median 0.048 s, max 0.072 s over 10 runs

## Wrong

- none

## Before consent (phrase list only): wrong

- n20: "How much is budgeted for snakebite antivenom?": fired
- n21: "What rate of postpartum haemorrhage does the EmONC report give?": fired
- n32: "Hatsarin mota nawa aka samu a Sokoto a 2025?": fired
- n40: "Nawa aka ware don maganin saran maciji?": fired
- n41: "Menene yawan zubar da jini bayan haihuwa a rahoton EmONC?": fired

## Timing

| place | case | seconds | facility pinned |
|---|---|---|---|
| Sokoto city | maternal | 0.072 | Godiya Hospital |
| Sokoto city | general | 0.032 | Godiya Hospital |
| Goronyo | maternal | 0.046 | Goronyo General Hospital |
| Goronyo | general | 0.046 | Goronyo General Hospital |
| Tureta | maternal | 0.05 | Tureta General Hospital |
| Tureta | general | 0.049 | Tureta General Hospital |
| Kebbe | maternal | 0.033 | Kebbe General Hospital |
| Kebbe | general | 0.031 | Kebbe General Hospital |
| Illela | maternal | 0.065 | Illela General Hospital |
| Illela | general | 0.061 | Illela General Hospital |
