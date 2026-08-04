# Anise ZMK config

ZMK firmware configuration for the Anise split keyboards.

**[Browse the keymaps →](https://anisehid.github.io/zmk-config/)**

The keymap browser is regenerated from the `.keymap` source files on every push,
so it can never drift from what the firmware actually does. Every key sits at its
real matrix position, and you can toggle matrix coordinates and raw ZMK bindings.

---

## Hardware

| Shield | Keys | Notes |
|---|---|---|
| `anise60b` | 63 | 60% split |
| `anise60bn` | 65 | 60% split with nav cluster |
| `anise85a` | 86 | 85-key |
| `anise85n` | 84 | 85-key with nav cluster |

Two controllers, and **they are not interchangeable** — each maps the `anise_ctl`
connector to completely different GPIOs:

| Controller | Built for |
|---|---|
| `anisectlp_01` | all four shields |
| `anisectlc_10` | all four shields, plus the presets |

Flashing the wrong one gives you a keyboard that enumerates over USB and
advertises over Bluetooth but where **no key works** — the matrix scans pins that
aren't wired to anything. Check the silkscreen on the controller if unsure.

---

## Getting firmware

Firmware is built by GitHub Actions on every push. There is nothing to install
locally.

```bash
gh run download --name firmware --dir zmk
```

Or grab the `firmware` artifact from the [Actions tab](https://github.com/anisehid/zmk-config/actions).
Artifacts expire after 90 days — rebuild rather than hunting for an old run.

### Flashing

Each half is flashed separately.

1. Double-tap the reset button — a USB drive named `NRF52BOOT` appears
2. Copy the matching `.uf2` onto it
3. It reboots itself and the drive disappears

```bash
cp -X zmk/anise60b_left-anisectlc_10-zmk.uf2  /Volumes/NRF52BOOT/
cp -X zmk/anise60b_right-anisectlc_10-zmk.uf2 /Volumes/NRF52BOOT/
```

Filenames are `<shield>_<side>-<controller>-zmk.uf2`. Don't cross left and right.

**On macOS, use `cp -X` rather than dragging in Finder.** Finder writes AppleDouble
metadata that the bootloader's small FAT volume can't handle. Either way you'll see
`Error -36` or `fcopyfile failed: Input/output error` — that is the board rebooting
the moment it has the full image, not a failure. **The volume disappearing is the
success signal.** If the copy were rejected, the drive would still be mounted.

If Bluetooth pairing misbehaves, flash [`tools/settings_reset.uf2`](tools/settings_reset.uf2)
first, let it reboot, then flash the real firmware.

---

## Preset layouts

Four ready-to-flash variants of `anise60b`. Same hardware, different keymap — each
is a real shield that reuses `anise60b`'s matrix and kscan and only replaces the
keymap.

| Preset | What changes |
|---|---|
| `anise60b_win` | Ctrl / Win / Alt — what most keyboards ship with |
| `anise60b_mac` | Ctrl / Option / Command, Command mirrored on the right |
| `anise60b_vim` | Caps → Esc, Fn layer keeps HJKL as arrows |
| `anise60b_hhkb` | Ctrl on Caps, Backspace on the backslash key |

```bash
cp -X zmk/anise60b_mac_left-anisectlc_10-zmk.uf2 /Volumes/NRF52BOOT/
```

Preview any of them, with changes against the base layout highlighted, in the
[keymap browser](https://anisehid.github.io/zmk-config/).

Presets are built for `anisectlc_10` only. To add `anisectlp_01`, append the pairs
to `build.yaml`.

---

## Changing the keymap

Edit `config/boards/shields/<shield>/<shield>.keymap`, then commit and push. CI
builds the firmware and updates the keymap page.

```bash
git add config && git commit -m "keymap: ..." && git push
gh run download --name firmware --dir zmk
```

Bindings are a flat array indexed against the `matrix-transform` in the shield's
`.dtsi`. **The counts must match** — ZMK indexes positionally, so an extra binding
is silently dropped and a missing one leaves the tail unbound, with no build error.
The parser checks this and reports mismatches on the page.

### Layers

| Layer | Reached by |
|---|---|
| 0 — base | default |
| 1 — Fn | hold `Fn1` (right half, next to Space) |
| 2 — Fn2 | hold `Fn2` (left half, right of Space) |
| 3 — Keyboard | hold `Fn2` **and** the bottom-left key |

Layer 3 holds the Bluetooth, RGB and output controls:

| Key | Action |
|---|---|
| `Q` `W` `E` `R` `T` | select Bluetooth profile 0–4 |
| `S` | switch output to USB |
| `D` | clear the current profile's pairing |
| number row | RGB toggle, hue, saturation, brightness |
| `Tab` | cycle RGB effect |

### Presets are generated

Preset keymaps are produced by a script — don't hand-edit them:

```bash
python3 tools/pagegen/make_presets.py
```

Each preset declares only its differences from `anise60b` in `PRESETS` at the top
of that file. A change to the base layout flows into every preset unless the
preset pins that position explicitly.

---

## Repository layout

```
build.yaml                      board + shield combinations CI builds
config/west.yml                 pins ZMK to anisehid/zmk
config/boards/shields/          shield definitions
  <shield>.dtsi                 matrix transform
  <shield>.keymap               layers
  <shield>_{left,right}.overlay kscan pin assignment
  boards/<board>.overlay        per-controller RGB wiring
tools/pagegen/                  keymap page + preset generator
tools/settings_reset.uf2        clears Bluetooth pairings
```

### Building the page locally

```bash
PYTHONPATH=tools/pagegen python3 tools/pagegen/build.py
open docs/index.html
```

`docs/` is generated and git-ignored — CI rebuilds it on every push so the
published page always matches the source.

---

## Known issues

**`anise85a` and `anise85n` have one binding too many** on their `fn`, `fn2` and
`kbd_func` layers. ZMK drops the surplus entry, so nothing shifts — only the last
key of the bottom row is dead on those layers. Fixing it means deciding whether
the transform is missing a position or the keymap has a stray binding.

**Don't upgrade the bootloader.** The boards ship an Adafruit nRF52 bootloader with
SoftDevice S140 6.1.1, which places the application at `0x26000`. A newer bootloader
moves it to `0x27000` and every `.uf2` here silently stops working.

**`CONFIG_NFCT_PINS_AS_GPIOS=y` is required** and set in the shield `.conf` files.
P0.09 and P0.10 are NFC antenna pins at reset and cannot drive the matrix until
freed — both controllers route a matrix line through P0.09. The upstream board
defconfigs are missing this.
