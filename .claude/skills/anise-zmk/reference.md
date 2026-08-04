# Reference

## Shields

| Shield | Keys | Transform |
|---|---|---|
| `anise60b` | 63 | 15 cols × 5 rows |
| `anise60bn` | 65 | 15 × 5, adds `RC(3,13)` and `RC(4,14)` |
| `anise85a` | 86 | 16 × 6 |
| `anise85n` | 84 | 16 × 6 |

`anise60b` and `anise60bn` differ by **two keys only** — the nav pair. If someone
is unsure which they have, a wrong choice kills those two keys, not the board.

Presets `anise60b_{win,mac,vim,hhkb}` reuse `anise60b`'s transform and kscan via
`#include` and replace only the keymap. Built for `anisectlc_10` only.

## Matrix pins

All shields drive rows on `anise_ctl` 11–15 (85-series adds 16). Columns are
21–27 for the 60-series, 22–28 for the 85-series.

The nexus maps those to entirely different GPIOs per controller:

| `anise_ctl` | `anisectlp_01` | `anisectlc_10` |
|---|---|---|
| 11 (row 0) | P0.04 | P1.06 |
| 12 (row 1) | P1.13 | P0.20 |
| 13 (row 2) | P0.05 | P0.31 |
| 14 (row 3) | P1.11 | P0.02 |
| 15 (row 4) | P0.06 | **P0.09 — NFC** |
| 21 (col 0) | P0.07 | P0.08 |
| 22 (col 1) | **P0.09 — NFC** | P0.28 |

Full maps live in `app/boards/arm/anisectl{p,c}/anisectl_pins.dtsi` in the
`anisehid/zmk` fork, not in this repo.

Peripherals on `anisectlc`: LED P1.10, ext-power P1.09, I²C P0.15/P0.17,
UART P0.06/P0.08 (disabled), RGB SPI P0.26/P0.12/P0.22, `pinmux.c` forces P0.05
to input.

## Layers

| Layer | Node | Reached by |
|---|---|---|
| 0 | `default_layer` | — |
| 1 | `fn_layer` | hold `&mo 1` at `(4,9)`, right half |
| 2 | `fn2_layer` | hold `&mo 2` at `(4,6)`, left half |
| 3 | `kbd_func_layer` | hold layer 2, then `&mo 3` at `(4,0)` |

Layer 3 is a three-key chord. Its Bluetooth controls: `Q`–`T` select profiles 0–4
via the `bt_s0`–`bt_s4` macros (which also switch output to BLE), `S` switches to
USB, `D` clears the current pairing.

## Bootloader

Adafruit nRF52, SoftDevice S140 6.1.1, app at `0x26000`, UF2 family
`0xADA52840`. The volume mounts as `NRF52BOOT`. Verify a `.uf2` before blaming a
flash:

```bash
python3 tools/uf2/utils/uf2conv.py -i <file>.uf2
```

`Target Address is 0x00026000` is correct. `0x27000` means someone upgraded the
bootloader and every firmware here needs its flash layout updated to match.

## Repo layout

```
build.yaml                        board + shield matrix for CI
config/west.yml                   pins ZMK to anisehid/zmk (Zephyr 3.0 fork)
config/boards/shields/<shield>/
  <shield>.dtsi                   matrix transform
  <shield>.keymap                 layers
  <shield>_{left,right}.overlay   kscan pins
  <shield>.conf                   Kconfig; the _left/_right ones are symlinks
  boards/<board>.overlay          per-controller RGB wiring
tools/pagegen/
  parse.py                        shields -> JSON, validates binding counts
  make_presets.py                 generates the preset shields
  build.py                        renders docs/index.html
  template.html                   page markup and styles
.github/workflows/build.yml       firmware, 24 combos
.github/workflows/pages.yml       keymap page, main only
```

## Page generator

`parse.py` is the single source of truth for "what does this keymap say" — both
the page and any verification should go through it rather than re-parsing by
hand. It returns per-shield positions, layers, and any binding-count warnings.

Adding a preset means editing `PRESETS` in `make_presets.py`, running it, and
adding the two shield entries to `build.yaml`. The generator writes the Kconfig
files, overlays, conf symlinks, `boards/` copies, keymap, and `preset.json`.
