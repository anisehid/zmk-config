# Diagnosing keys that don't respond

Work in this order. Each step eliminates a whole class of cause, and the early
steps are free.

## 1. Read the symptom precisely

The failure pattern narrows the cause more than anything else:

| Symptom | Most likely cause |
|---|---|
| Detected over USB and visible over Bluetooth, but **no key at all** works | Wrong controller firmware — `anisectlp_01` vs `anisectlc_10` |
| One **whole row or column** dead, rest fine | Pin-level: NFC pins, a peripheral claiming the pin, or wiring |
| **Scattered** keys dead | Hardware — switches, sockets, diodes |
| Keys type the **wrong character** | Keymap or transform |
| Nothing at all, no USB device | Bad flash, or wrong app address |

"Detected but nothing types" is the single most common report, and it is almost
always the controller mismatch. Ask which controller before anything else — the
silkscreen says `anisectlp` or `anisectlc`.

## 2. Check the keymap is internally consistent

Free, and rules out the entire class of transform/binding bugs:

```bash
PYTHONPATH=tools/pagegen python3 tools/pagegen/parse.py > /dev/null
```

Any mismatch is reported per shield and layer. Silence means every layer's
binding count equals its transform position count.

## 3. Check nothing else claims the pin

Map the dead row or column to its `anise_ctl` pin via the shield's
`_left.overlay`, then to a GPIO via the board's `anisectl_pins.dtsi` in the ZMK
fork. Then check that GPIO against the board `.dts` — LED, ext-power, I²C, UART,
`pinmux.c`, and the RGB SPI pins in `boards/<board>.overlay`.

Two specific traps:

- **P0.09 / P0.10 are NFC antenna pins** at reset. Without
  `CONFIG_NFCT_PINS_AS_GPIOS=y` they cannot drive the matrix. Both controllers
  route a matrix line through P0.09.
- **UART0 sits on P0.06 / P0.08** on `anisectlc`, which are matrix columns. It is
  disabled in the board `.dts`, so this only bites if something enables it.

## 4. Get scan-level evidence

This is the step that separates software from hardware, and it is decisive.
Enable logging in the shield's `.conf`:

```
CONFIG_ZMK_USB_LOGGING=y
CONFIG_ZMK_LOG_LEVEL_DBG=y
```

Build, flash the **left** half (it's the central and owns USB), then:

```bash
ls /dev/cu.usbmodem*
screen $(ls /dev/cu.usbmodem* | head -1) 115200    # ctrl-a k to quit
```

Press a suspect key, then a known-good one.

- **Known-good logs, suspect logs nothing** → the matrix never saw it. Hardware or
  pin mapping. No keymap change will help. Stop looking at the keymap.
- **Both log, but at unexpected `r,c`** → pin mapping is wrong. Fix the overlay.
- **Correct `r,c` but nothing types** → keymap or layer behaviour.

Remember the log line comes from the kscan driver, before the transform and
keymap. Its absence is meaningful; its presence exonerates the wiring.

## 5. Probe for a wrong pin map

If step 4 shows nothing and you suspect the board file rather than the hardware,
build a probe shield: same known-good columns, but every other connector pin
scanned as a row, all positions bound to `&none` so probing doesn't type into the
terminal you're reading. Press a dead key and see which row index fires.

Include the known-good rows as a control — if they don't report their expected
index, the probe itself is wrong and its result means nothing.

This was done once and removed after; recover it with
`git log --all --oneline -- config/boards/shields/aniseprobe`.

## 6. Isolate with a controller swap

Each half has its own controller. Move the right half's controller to the left
PCB and flash it with the left firmware.

- Keys work → the original controller is faulty.
- Still dead → the PCB or its connector.

Zero builds, and it separates the two remaining candidates cleanly.

## Bisecting a suspected regression

If someone reports a fault that appeared "after a change", don't argue from the
diff — download the actual pre-change binary and let them flash it:

```bash
gh run list --limit 20 --json databaseId,headSha,createdAt
gh run download <old-run-id> --name firmware --dir zmk-before
```

Artifacts last 90 days. This settles it in one flash instead of a debate, and has
already caught one case where the correlation was with handling the board during
flashing, not with the code.
