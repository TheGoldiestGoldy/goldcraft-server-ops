# Log evidence summary

Files scanned: **160**

> Counts are string matches, not unique incidents or confirmed root causes. Repeated startup warnings inflate totals.

## Totals

| Pattern | Matches |
|---|---:|
| error | 1,265,893 |
| warn | 44,565 |
| chunky_activity | 5,564 |
| dh_activity | 3,246 |
| vss_activity | 1,721 |
| tick_stall | 1,370 |
| connection_problem | 1,279 |
| cant_keep_up | 1,227 |
| join_event | 285 |
| leave_event | 243 |
| out_of_memory | 4 |

## Daily evidence

| Date | Warnings | Errors | Can't keep up | Tick stalls | DH | VSS | Chunky | Connections |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-10-17 | 4921 | 196133 | 8 | 14 | 39 | 248 | 33 | 10 |
| 2026-10-18 | 519 | 916 | 4 | 11 | 36 | 85 | 35 | 14 |
| 2026-10-19 | 935 | 777 | 33 | 40 | 52 | 321 | 49 | 34 |
| 2026-10-20 | 5312 | 321619 | 61 | 70 | 40 | 378 | 120 | 14 |
| 2026-10-21 | 8571 | 484715 | 131 | 139 | 548 | 79 | 5098 | 44 |
| 2026-10-22 | 2349 | 123765 | 22 | 29 | 158 | 28 | 76 | 20 |
| 2026-10-23 | 404 | 1259 | 8 | 17 | 171 | 28 | 66 | 17 |
| 2026-10-24 | 12328 | 1212 | 4 | 11 | 226 | 23 | 7 | 19 |
| 2026-10-25 | 2398 | 107573 | 19 | 26 | 76 | 118 | 3 | 34 |
| 2026-10-26 | 126 | 82 | 15 | 16 | 39 | 78 | 1 | 51 |
| 2026-10-27 | 716 | 18289 | 35 | 40 | 122 | 80 | 5 | 84 |
| 2026-10-28 | 221 | 168 | 22 | 24 | 48 | 26 | 2 | 25 |
| 2026-10-29 | 27 | 270 | 4 | 4 | 2 | 11 | 0 | 135 |
| 2026-10-30 | 449 | 513 | 70 | 77 | 146 | 60 | 6 | 60 |
| 2026-10-31 | 803 | 1626 | 147 | 153 | 125 | 71 | 5 | 84 |
| 2026-11-01 | 301 | 578 | 1 | 9 | 140 | 12 | 8 | 27 |
| 2026-11-02 | 89 | 138 | 2 | 3 | 25 | 0 | 1 | 112 |
| 2026-11-03 | 124 | 152 | 13 | 15 | 46 | 13 | 2 | 36 |
| 2026-11-04 | 459 | 141 | 320 | 321 | 31 | 21 | 1 | 136 |
| 2026-11-05 | 730 | 518 | 161 | 163 | 52 | 18 | 2 | 77 |
| 2026-11-06 | 840 | 961 | 136 | 141 | 107 | 18 | 5 | 25 |
| 2026-11-07 | 321 | 547 | 1 | 5 | 93 | 0 | 4 | 35 |
| 2026-11-08 | 219 | 1108 | 3 | 6 | 54 | 0 | 3 | 37 |
| 2026-11-09 | 138 | 395 | 0 | 3 | 54 | 0 | 3 | 93 |
| 2026-11-10 | 70 | 143 | 5 | 5 | 10 | 0 | 1 | 4 |
| 2026-11-11 | 249 | 497 | 0 | 6 | 129 | 0 | 6 | 8 |
| 2026-11-12 | 128 | 250 | 1 | 4 | 76 | 0 | 3 | 5 |
| 2026-11-13 | 295 | 578 | 0 | 7 | 176 | 0 | 7 | 13 |
| 2026-11-14 | 155 | 249 | 0 | 3 | 113 | 0 | 3 | 6 |
| 2026-11-15 | 54 | 83 | 1 | 2 | 46 | 0 | 1 | 9 |
| 2026-11-16 | 314 | 638 | 0 | 6 | 266 | 5 | 8 | 11 |

## Crash reports

| File | Description | First captured cause |
|---|---|---|
| crash-2026-10-18_04.10.34-server.txt | Ticking block entity |  |
| crash-2026-10-18_04.15.30-server.txt | Ticking block entity |  |
| crash-2026-10-18_04.18.56-server.txt | Ticking block entity |  |
| crash-2026-10-20_17.18.15-server.txt | Watching Server |  |
| crash-2026-10-20_19.21.41-server.txt | Exception in server tick loop |  |
| crash-2026-10-20_19.33.30-server.txt | Watching Server |  |
| crash-2026-10-21_06.06.01-server.txt | Watching Server |  |
| crash-2026-10-21_23.36.46-server.txt | Watching Server |  |
| crash-2026-10-23_19.13.58-server.txt | Watching Server |  |
| crash-2026-10-23_22.06.18-server.txt | Watching Server |  |
| crash-2026-10-24_04.06.43-server.txt | Exception chunk generation/loading |  |
| crash-2026-10-25_02.46.42-server.txt | Exception chunk generation/loading |  |
| crash-2026-10-25_02.48.21-server.txt | Exception chunk generation/loading |  |
| crash-2026-10-25_02.50.13-server.txt | Exception chunk generation/loading |  |
| crash-2026-10-27_02.07.05-server.txt | Sending packet | java.io.IOException: An established connection was aborted by the software in your host machine |
| crash-2026-10-30_23.55.11-server.txt | Watching Server |  |
| crash-2026-10-31_00.11.28-server.txt | Watching Server |  |
| crash-2026-11-01_02.32.05-server.txt | Watching Server |  |
| crash-2026-11-01_21.58.00-server.txt | Watching Server |  |
| crash-2026-11-01_22.03.02-server.txt | Watching Server |  |
| crash-2026-11-01_22.16.14-server.txt | Watching Server |  |
