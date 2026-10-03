# Anise ZMK config

ZMK firmware configuration for the Anise split keyboards.

**[Browse the keymaps →](https://anisehid.github.io/zmk-config/)**

The keymap browser is regenerated from the `.keymap` source files on every push,
so it can never drift from what the firmware actually does. Every key sits at its
real matrix position, and you can toggle matrix coordinates and raw ZMK bindings.

> **Want your own layout?** Change keys live from the browser with
> [ZMK Studio](#zmk-studio) — no build, no flash. Or fork this repo, edit a
> `.keymap` file, and download the firmware Actions builds for you — see
> [Fork it to make your own keymap](#fork-it-to-make-your-own-keymap).

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

| Controller | Board name | Built for |
|---|---|---|
| AniseCTL Pro | `anisectlp` | all four shields, plus the presets |
| AniseCTL community | `anisectlc` | all four shields, plus the presets |

Firmware is built on upstream [ZMK](https://zmk.dev), with both controller
definitions living in this repo (`boards/anisehid/`). Only `anise85a` on
`anisectlc` has been verified on real hardware so far — everything else
compiles but is untested, and the `anisectlp` board port is new.

Flashing the wrong one gives you a keyboard that enumerates over USB and
advertises over Bluetooth but where **no key works** — the matrix scans pins that
aren't wired to anything. Check the silkscreen on the controller if unsure.

---

## Getting firmware

Firmware is built by GitHub Actions. There is no toolchain to install — you never
need to compile anything on your own machine.

### Just want the stock firmware

Download the `firmware` artifact from the latest green run on the
[Actions tab](https://github.com/anisehid/zmk-config/actions), or:

```bash
gh run download --name firmware --dir zmk
```

You need to be signed in to GitHub either way — artifacts can't be downloaded
anonymously. They also expire after 90 days, so rebuild rather than hunting for an
old run.

### Fork it to make your own keymap

This is the normal path if you want to change anything. You can do the whole thing
in the browser.

**1. Fork this repository** — the Fork button, top right.

**2. Enable Actions on your fork.** GitHub disables workflows on new forks. Open the
**Actions** tab and click *"I understand my workflows, go ahead and enable them"*.
Nothing builds until you do this, and there's no warning if you skip it.

**3. Edit a keymap.** In your fork, open
`config/boards/shields/<shield>/<shield>.keymap`, click the pencil icon, make your
change, and **Commit changes**. That push triggers a build on its own.

**4. Or trigger a build without changing anything** — **Actions** → **Build** →
**Run workflow** → pick your branch → **Run workflow**.

**5. Wait ~10 minutes**, then download the `firmware` artifact from the finished run
and flash as below.

With the `gh` CLI, point it at your fork:

```bash
gh workflow run build.yml --repo <you>/zmk-config
gh run download --repo <you>/zmk-config --name firmware --dir zmk
```

Forking doesn't change where the firmware comes from — `config/west.yml` pulls
upstream ZMK, and the controller definitions come from this repo's `boards/`, so
you get the same source with your keymap on top.

### Flashing

Each half is flashed separately.

1. Double-tap the reset button — a USB drive named `NRF52BOOT` appears
2. Copy the matching `.uf2` onto it
3. It reboots itself and the drive disappears
4. Power-cycle the **right** half after flashing either side — until you do, it
   may not reconnect to the left, and its keys stay dead

```bash
cp -X zmk/anise60b_left-anisectlc_nrf52840_zmk-zmk.uf2  /Volumes/NRF52BOOT/
cp -X zmk/anise60b_right-anisectlc_nrf52840_zmk-zmk.uf2 /Volumes/NRF52BOOT/
```

Filenames are `<shield>_<side>-<controller>_nrf52840_zmk-zmk.uf2`. Don't cross
left and right, and flash **both halves from the same build** — firmware from
before the upstream-ZMK move (`…-anisectlc_10-zmk.uf2`) can't pair with the new
firmware. On Linux the drive mounts under `/run/media/$USER/NRF52BOOT/`.

**On macOS, use `cp -X` rather than dragging in Finder.** Finder writes AppleDouble
metadata that the bootloader's small FAT volume can't handle. Either way you'll see
`Error -36` or `fcopyfile failed: Input/output error` — that is the board rebooting
the moment it has the full image, not a failure. **The volume disappearing is the
success signal.** If the copy were rejected, the drive would still be mounted.

If Bluetooth pairing misbehaves, flash [`tools/settings_reset.uf2`](tools/settings_reset.uf2)
first, let it reboot, then flash the real firmware.

### Your own keymap page (optional)

To get the keymap browser on your fork: **Settings** → **Pages** → **Source:
GitHub Actions**, then push once. It publishes to
`https://<you>.github.io/zmk-config/` and regenerates itself on every push.

---

## Preset layouts

Ready-to-flash variants of `anise60b` and `anise85a`. Same hardware, different
keymap — each is a real shield that reuses its base's matrix and kscan and only
replaces the keymap.

| Preset | What changes |
|---|---|
| `anise60b_win` | Ctrl / Win / Alt — what most keyboards ship with |
| `anise60b_mac` | Ctrl / Option / Command, Command mirrored on the right |
| `anise60b_vim` | Caps → Esc, Fn layer keeps HJKL as arrows |
| `anise60b_hhkb` | Ctrl on Caps, Backspace on the backslash key |
| `anise60b_keyd` | The Linux keyd remap in firmware: Caps → Esc, LCtrl ↔ LAlt, Fn1 holds symbols/arrows/F1–F12, Fn2 holds F-keys, Fn1 + Fn2 → Fn3 (BT, RGB, Studio unlock) |

```bash
cp -X zmk/anise60b_mac_left-anisectlc_nrf52840_zmk-zmk.uf2 /Volumes/NRF52BOOT/
```

Preview any of them, with changes against the base layout highlighted, in the
[keymap browser](https://anisehid.github.io/zmk-config/).

Presets are built for both controllers.

---

## ZMK Studio

Every keyboard except `anise85n` supports [ZMK Studio](https://zmk.studio): change
keys from a browser or desktop app over USB, and they apply instantly — no build,
no flash. It's ZMK's answer to VIA.

1. **Open Studio** — <https://zmk.studio> in Chrome, Edge or Chromium, or the
   desktop app from <https://zmk.studio/download>. **Firefox can't** — it has no
   Web Serial.
2. **Connect the left half over USB** and pick your keyboard from the list.
3. **Unlock** when asked, by pressing the unlock key on the keyboard:

   | Keyboard | Unlock |
   |---|---|
   | `anise85a` | hold `Fn3` (bottom row, 2nd from left), press `Esc` |
   | `anise60b`, presets, `anise60bn` | hold `Fn2` + bottom-left key (layer 3), press `Backspace` |

4. Pick a layer, click a key, choose its new function. Changes apply at once but
   are temporary until you click **Save**; **Restore Stock Settings** returns to
   the keymap built into the firmware.

Things to know:

- **Once you use Studio, the keyboard ignores later `.keymap` edits** until you
  run *Restore Stock Settings* — the keymap now lives in the keyboard's memory.
- **Studio can't export yet.** There is no way to save your Studio keymap to a
  file; if you want it in git, copy the changes into the `.keymap` by hand.
- **Linux: Chromium from Snap can't see the keyboard** until you run
  `sudo snap connect chromium:raw-usb` and restart it. You also need access to
  `/dev/ttyACM*`, usually via the `dialout` group.
- `anise85n` has no Studio support yet — see [Known issues](#known-issues).

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
| 3 — Keyboard | 60-series: hold `Fn2` **and** the bottom-left key. 85-series: hold `Fn3` (bottom row, 2nd from left) |

Layer 3 holds the Bluetooth, RGB and output controls:

| Key | Action |
|---|---|
| `Q` `W` `E` `R` `T` | select Bluetooth profile 0–4 |
| `S` | switch output to USB |
| `D` | clear the current profile's pairing |
| number row | RGB toggle, hue, saturation, brightness |
| `Tab` | cycle RGB effect |

The layer nodes carry a `display-name`, which is what Studio shows.

### Physical layouts are generated

Studio draws the keyboard from `<shield>-layouts.dtsi`, one entry per matrix
position in transform order. They're generated from AniseHID's layout
descriptions — don't hand-edit them:

```bash
PYTHONPATH=tools/pagegen python3 tools/make_layouts.py
```

The script checks every row against the transform and refuses to write a layout
that doesn't match. If you change a transform, regenerate.

### Presets are generated

Preset keymaps are produced by a script — don't hand-edit them:

```bash
python3 tools/pagegen/make_presets.py
```

Each preset declares only its differences from its base (`anise60b` unless it
sets `base`) in `PRESETS` at the top of that file; `extra_layers` adds layers. A change to the base layout flows into every preset unless the
preset pins that position explicitly.

---

## Repository layout

```
.claude/skills/anise-zmk/       Claude Code skill (see below)
boards/anisehid/anisectl{c,p}/  controller definitions (pin maps, flash layout)
zephyr/module.yml               makes this repo a Zephyr module, so boards/ is found
build.yaml                      board + shield combinations CI builds
config/west.yml                 pulls upstream ZMK
config/boards/shields/          shield definitions
  <shield>.dtsi                 matrix transform
  <shield>-layouts.dtsi         physical layout for Studio (generated)
  <shield>.keymap               layers
  <shield>_{left,right}.overlay kscan pin assignment
  boards/<board>_nrf52840_zmk.overlay  per-controller RGB wiring
tools/make_layouts.py           physical layout generator
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

### Using Claude Code

The repo ships a skill at `.claude/skills/anise-zmk/`. Clone or fork, open Claude
Code here, and it activates on its own when you edit a keymap, add a preset, build
firmware, or chase a key that won't respond. It carries the traps that cost real
debugging time — the controller mismatch that looks like a dead board, why a failed
copy on macOS means the flash worked, and why zero scan events rules out the keymap
entirely.

---

## Known issues

**`anise85a` and `anise85n` have one binding too many** on their `fn`, `fn2` and
`kbd_func` layers. ZMK drops the surplus entry, so nothing shifts — only the last
key of the bottom row is dead on those layers. Fixing it means deciding whether
the transform is missing a position or the keymap has a stray binding.

**Don't upgrade the bootloader.** The boards ship an Adafruit nRF52 bootloader with
SoftDevice S140 6.1.1, which places the application at `0x26000`. A newer bootloader
moves it to `0x27000` and every `.uf2` here silently stops working.

**`anise85n` has no Studio support, and its matrix may be wrong.** Its transform
has 13 keys in the top row and 13 in the bottom, but AniseHID's layout
description for it has 15 and 12 — the same top row as `anise85a`, including the
knob. Someone with an `anise85n` needs to check which is right before it gets a
physical layout. If your 85-key board's F-row types one key off, it is probably
an `anise85a`: count the top row (Esc, F1–F12, Del and the knob = 15).

**The `anise85a` knob only presses.** Its press is a normal key (Play/Pause by
default); turning it sends no signal to any controller pin, so rotation can't be
bound in firmware.

**The old `boards/*_10.overlay` and `*_01.overlay` files are unused.** They
belong to the pre-upstream build; the live RGB wiring is in
`boards/<board>_nrf52840_zmk.overlay`.

**`CONFIG_NFCT_PINS_AS_GPIOS=y` is required** and set in both controllers'
defconfigs and the shield `.conf` files. P0.09 and P0.10 are NFC antenna pins at
reset and cannot drive the matrix until freed — both controllers route a matrix
line through P0.09.
