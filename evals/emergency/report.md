# Emergency fast path eval

- must fire: 64/64 fired (before consent, phrase list only: 44/64)
- must not fire: 64/64 quiet (before consent: 58/64)
- decided by: phrase list 44, classifier 33, neither 51
- fired by (must fire): phrase 44, classifier 19, understanding 1, none 0
- off-list set (x/y): must fire 20/20, false alarms 0/20
- classifier time: median 1.75 s, max 2.43 s
- fast path end to end (handler, PostGIS, no ORS): median 0.119 s, max 0.147 s over 10 runs

## Wrong

- none

## Caught only by the understanding step

- x16: "Yarinyata ta sha maganin feshi na gona": child drank farm pesticide and needs emergency care now

## Before consent (phrase list only): wrong

- x01: "Since she gave birth this morning the blood has not stopped coming": did not fire
- x02: "My wife's water broke and the pains are coming fast": did not fire
- x03: "Our neighbour's baby came out blue and is very quiet": did not fire
- x04: "Mama went down while cooking and her mouth is crooked now": did not fire
- x05: "My boy drank something from the farm chemical bottle": did not fire
- x06: "The child has had diarrhoea all day and now his eyes are sunken and he can't drink": did not fire
- x07: "My sister is 8 months pregnant and has a terrible headache and a swollen face": did not fire
- x08: "My husband cut his leg with a cutlass and it won't stop": did not fire
- x09: "Grandpa talks strangely all of a sudden and cannot lift his arm": did not fire
- x10: "The newborn is not feeding and feels cold": did not fire
- x11: "Matata na naƙuda": did not fire
- x12: "Yaro na yana ta zazzaɓi baya farkawa": did not fire
- x13: "Bayan matata ta haihu tana ta rasa jini sosai": did not fire
- x14: "Ruwan haihuwar matata ya fashe tun safe": did not fire
- x15: "Mahaifiyata ta kwanta a ƙasa ba ta amsawa": did not fire
- x16: "Yarinyata ta sha maganin feshi na gona": did not fire
- x17: "Jaririn bai sha nono ba tun jiya kuma ya yi sanyi": did not fire
- x18: "Ɗan'uwana ya yanke ƙafarsa da adda, ba ya tsayawa": did not fire
- x19: "Matata mai ciki tana ciwon kai sosai kuma fuskarta ta kumbura": did not fire
- x20: "Yarona yana ta amai da gudawa, ya rame ba ya iya tashi": did not fire
- n20: "How much is budgeted for snakebite antivenom?": fired
- n21: "What rate of postpartum haemorrhage does the EmONC report give?": fired
- n32: "Hatsarin mota nawa aka samu a Sokoto a 2025?": fired
- n40: "Nawa aka ware don maganin saran maciji?": fired
- n41: "Menene yawan zubar da jini bayan haihuwa a rahoton EmONC?": fired
- y06: "Is there a budget line for snakebite treatment?": fired

## Timing

| place | case | seconds | facility pinned |
|---|---|---|---|
| Sokoto city | maternal | 0.129 | Godiya Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=13.059569,5.232887 |
| Sokoto city | general | 0.111 | Godiya Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=13.059569,5.232887 |
| Goronyo | maternal | 0.108 | Goronyo General Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=13.442181,5.675731 |
| Goronyo | general | 0.129 | Goronyo General Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=13.442181,5.675731 |
| Tureta | maternal | 0.147 | Tureta General Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=12.593355,5.549949 |
| Tureta | general | 0.126 | Tureta General Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=12.593355,5.549949 |
| Kebbe | maternal | 0.111 | Kebbe General Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=12.121262,4.732168 |
| Kebbe | general | 0.114 | Kebbe General Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=12.121262,4.732168 |
| Illela | maternal | 0.124 | Illela General Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=13.729902,5.307693 |
| Illela | general | 0.11 | Illela General Hospital*: open the exact spot on the map: https://www.google.com/maps/search/?api=1&query=13.729902,5.307693 |
