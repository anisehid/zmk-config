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
`#include` and replace only the keymap. Built for both controllers.

Physical layouts (`<shield>-layouts.dtsi`, needed by Studio) exist for
`anise60b`, `anise60bn` and `anise85a`, generated from `anisehid/anise-kbd`
`desc-gen/desc/{anise60b,anise60bnav,anise85a}.json`. `anise85n` has none: its
transform rows (13 top, 13 bottom) disagree with `anise85n.json` (15, 12).

## Matrix pins

All shields drive rows on `anise_ctl` 11–15 (85-series adds 16). Columns are
21–27 for the 60-series, 22–28 for the 85-series.

The nexus maps those to entirely different GPIOs per controller:

| `anise_ctl` | `anisectlp` | `anisectlc` |
|---|---|---|
| 11 (row 0) | P0.04 | P1.06 |
| 12 (row 1) | P1.13 | P0.20 |
| 13 (row 2) | P0.05 | P0.31 |
| 14 (row 3) | P1.11 | P0.02 |
| 15 (row 4) | P0.06 | **P0.09 — NFC** |
| 21 (col 0) | P0.07 | P0.08 |
| 22 (col 1) | **P0.09 — NFC** | P0.28 |

Full maps live in `boards/anisehid/anisectl{p,c}/anisectl_pins.dtsi`, copied
unchanged from the old `anisehid/zmk` fork. Both controllers route `anise_ctl`
31 (85-series column 15) to P0.12, and `anise_ctl` 2 (RGB data) to P0.26.

Peripherals on `anisectlc`: LED P1.10, ext-power P1.09 (active low), battery
AIN2. On `anisectlp`: LED P0.15, ext-power P0.13 (active high, 50 ms init delay),
battery AIN1. RGB is SPI MOSI P0.26 only, via pinctrl, on both. The fork's
`pinmux.c` (P0.05 as input) was not ported — the matrix configures that pin
itself. The `anisectlp` port is untested on hardware.

## Layers

| Layer | Node | Reached by |
|---|---|---|
| 0 | `default_layer` | — |
| 1 | `fn_layer` | hold `&mo 1` at `(4,9)`, right half |
| 2 | `fn2_layer` | hold `&mo 2` at `(4,6)`, left half |
| 3 | `kbd_func_layer` | 60-series: hold layer 2, then `&mo 3` at `(4,0)`. 85-series: `&mo 3` at `(5,1)` on the base layer |

Layers carry `display-name`s (Base/Fn1/Fn2/Fn3) for Studio.

On the 60-series layer 3 is a three-key chord. Its Bluetooth controls: `Q`–`T` select profiles 0–4
via the `bt_s0`–`bt_s4` macros (which also switch output to BLE), `S` switches to
USB, `D` clears the current pairing.

## ZMK Studio

Enabled on every left half except `anise85n`, via `snippet: studio-rpc-usb-uart`
and `cmake-args: -DCONFIG_ZMK_STUDIO=y` in `build.yaml`. `&studio_unlock` sits on
layer 3: position `(0,0)` (Esc) on the 85-series, `(0,14)` (Backspace) on the
60-series, whose layer-3 Esc slot is the RGB toggle. Presets inherit it from
`anise60b`.

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
boards/anisehid/anisectl{c,p}/    controller boards (hardware model v2)
zephyr/module.yml                 registers boards/ with the ZMK build
build.yaml                        board + shield matrix for CI
config/west.yml                   upstream zmkfirmware/zmk, main
config/boards/shields/<shield>/
  <shield>.dtsi                   matrix transform; chooses the physical layout
  <shield>-layouts.dtsi           physical layout for Studio (generated)
  <shield>.keymap                 layers
  <shield>_{left,right}.overlay   kscan pins
  <shield>.conf                   Kconfig; the _left/_right ones are symlinks
  boards/<board>_nrf52840_zmk.overlay  per-controller RGB wiring
                                  (the *_10 / *_01 overlays are dead leftovers)
tools/make_layouts.py             physical layouts from AniseHID descs
tools/pagegen/
  parse.py                        shields -> JSON, validates binding counts
  make_presets.py                 generates the preset shields
  build.py                        renders docs/index.html
  template.html                   page markup and styles
.github/workflows/build.yml       calls upstream build-user-config.yml; 32 combos
.github/workflows/pages.yml       keymap page, main only
```

## Page generator

`parse.py` is the single source of truth for "what does this keymap say" — both
the page and any verification should go through it rather than re-parsing by
hand. It returns per-shield positions, layers, and any binding-count warnings.

Adding a preset means editing `PRESETS` in `make_presets.py`, running it, and
adding the two shield entries to `build.yaml`. The generator writes the Kconfig
files, overlays, conf symlinks, `boards/` copies, keymap, and `preset.json`.

## anise85a knob

The top-right knob's **press** is an ordinary matrix key at keymap position
`(0,15)`. Its **rotation** was probed on 2026-09-26 (anisectlc, right half,
USB-logging probe build): nothing on the matrix, and nothing on any
non-matrix `anise_ctl` pin (1–5, 32–38) with either pull-ups or pull-downs.
The encoder's A/B contacts do not reach the controller on that board, so no
firmware change can bind rotation. Recover the probe with
`git log --all --oneline -- config/boards/shields/anise85aprobe`.
