"""Generate the preset keymap shields from anise60b.

Each preset is a real ZMK shield: it reuses anise60b's matrix transform and
kscan via #include, and only replaces the keymap. That keeps them buildable
through the normal shield mechanism with no cmake or preprocessor tricks.

Run from the repo root:  python3 tools/pagegen/make_presets.py
"""
import re
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SHIELDS = ROOT / 'config' / 'boards' / 'shields'
BASE = 'anise60b'

# Each preset overrides bindings at specific (row, col) positions of a layer.
PRESETS = {
    'anise60b_win': {
        'title': 'Windows standard',
        'name': 'ANISE60B-WIN',
        'blurb': 'What almost every keyboard ships with: Ctrl at the far left, '
                 'then Win and Alt. Backslash stays backslash.',
        'default_layer': {
            (0, 0): '&gresc',
            (2, 0): '&kp CAPS',
            (4, 0): '&kp LCTRL', (4, 1): '&kp LGUI', (4, 2): '&kp LALT',
            (1, 14): '&kp BSLH',
        },
    },
    'anise60b_mac': {
        'title': 'macOS',
        'name': 'ANISE60B-MAC',
        'blurb': 'Modifiers in macOS order — Control, Option, Command — with '
                 'Command mirrored on the right thumb.',
        'default_layer': {
            (0, 0): '&gresc',
            (2, 0): '&kp CAPS',
            (4, 0): '&kp LCTRL', (4, 1): '&kp LALT', (4, 2): '&kp LGUI',
            (4, 11): '&kp RGUI', (4, 12): '&kp RALT', (4, 13): '&kp RCTRL',
            (1, 14): '&kp BSLH',
        },
        'fn_layer': {
            (0, 11): '&kp C_BRI_DN', (0, 12): '&kp C_BRI_UP',
            (0, 13): '&kp C_VOL_DN',
        },
    },
    'anise60b_vim': {
        'title': 'Vim navigation',
        'name': 'ANISE60B-VIM',
        'blurb': 'Caps Lock becomes Escape, and the Fn layer keeps HJKL as '
                 'arrows so you never leave the home row.',
        'default_layer': {
            (0, 0): '&gresc',
            (2, 0): '&kp ESC',
            (4, 0): '&kp LCTRL', (4, 1): '&kp LGUI', (4, 2): '&kp LALT',
            (1, 14): '&kp BSLH',
        },
        'fn_layer': {
            (2, 7): '&kp LEFT', (2, 8): '&kp DOWN',
            (2, 9): '&kp UP', (2, 10): '&kp RIGHT',
            (1, 7): '&kp HOME', (1, 10): '&kp END',
        },
    },
    'anise60b_hhkb': {
        'title': 'HHKB style',
        'name': 'ANISE60B-HHKB',
        'blurb': 'Control on Caps Lock and Backspace on the backslash key — '
                 'the classic Happy Hacking arrangement.',
        'default_layer': {
            (0, 0): '&gresc',
            (2, 0): '&kp LCTRL',
            (1, 14): '&kp BSPC',
            (4, 0): '&kp LCTRL', (4, 1): '&kp LALT', (4, 2): '&kp LGUI',
        },
    },
}


def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', ' ', s, flags=re.S)
    return re.sub(r'//[^\n]*', ' ', s)


def load_base():
    dtsi = (SHIELDS / BASE / f'{BASE}.dtsi').read_text()
    raw = dtsi.split('map = <')[1].split('>;')[0]
    positions = [(int(r), int(c))
                 for r, c in re.findall(r'RC\((\d+),\s*(\d+)\)', strip_comments(raw))]

    km = strip_comments((SHIELDS / BASE / f'{BASE}.keymap').read_text())
    body = km.split('compatible = "zmk,keymap"')[1]
    layers = {}
    order = []
    for lname, binds in re.findall(r'(\w+)\s*\{\s*bindings\s*=\s*<(.*?)>\s*;',
                                   body, flags=re.S):
        toks = [' '.join(t.split()) for t in
                re.findall(r'&\s*[\w-]+(?:\s+[A-Za-z0-9_()]+)*', binds)]
        layers[lname] = toks
        order.append(lname)
    return positions, layers, order


def emit(shield, spec, positions, base_layers, order):
    d = SHIELDS / shield
    d.mkdir(exist_ok=True)
    upper = shield.upper()

    (d / 'Kconfig.shield').write_text(
        f'config SHIELD_{upper}_LEFT\n'
        f'\tdef_bool $(shields_list_contains,{shield}_left)\n\n'
        f'config SHIELD_{upper}_RIGHT\n'
        f'\tdef_bool $(shields_list_contains,{shield}_right)\n')

    (d / 'Kconfig.defconfig').write_text(
        f'if SHIELD_{upper}_LEFT\n\n'
        f'config ZMK_KEYBOARD_NAME\n\tdefault "{spec["name"]}"\n\n'
        f'config ZMK_SPLIT_ROLE_CENTRAL\n\tdefault y\n\n'
        f'endif\n\n'
        f'if SHIELD_{upper}_LEFT || SHIELD_{upper}_RIGHT\n\n'
        f'config ZMK_SPLIT\n\tdefault y\n\n'
        f'endif\n')

    for side in ('left', 'right'):
        (d / f'{shield}_{side}.overlay').write_text(
            f'/* {spec["title"]} preset: same matrix and kscan as {BASE},\n'
            f' * only the keymap differs. */\n\n'
            f'#include "../{BASE}/{BASE}_{side}.overlay"\n')
        link = d / f'{shield}_{side}.conf'
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(f'{shield}.conf')

    conf = d / f'{shield}.conf'
    if conf.is_symlink() or conf.exists():
        conf.unlink()
    conf.symlink_to(f'../{BASE}/{BASE}.conf')

    # Zephyr only looks for boards/<board>.overlay inside the shield being
    # built, so a preset must carry its own copies or the RGB led_strip node
    # (and therefore chosen zmk,underglow) goes missing.
    boards = d / 'boards'
    boards.mkdir(exist_ok=True)
    for ov in sorted((SHIELDS / BASE / 'boards').glob('*.overlay')):
        (boards / ov.name).write_text(
            f'#include "../../{BASE}/boards/{ov.name}"\n')

    idx = {pos: i for i, pos in enumerate(positions)}
    rows = sorted({r for r, _ in positions})
    out = []
    for lname in order:
        binds = list(base_layers[lname])
        for pos, val in spec.get(lname, {}).items():
            if pos not in idx:
                raise SystemExit(f'{shield}/{lname}: position {pos} not in transform')
            binds[idx[pos]] = val
        lines = []
        for r in rows:
            cells = [binds[idx[(r, c)]] for c in range(16) if (r, c) in idx]
            lines.append('    ' + '  '.join(f'{b:<12}' for b in cells).rstrip())
        out.append(f'        {lname} {{\n            bindings = <\n'
                   + '\n'.join(lines) + '\n            >;\n        };')

    (d / f'{shield}.keymap').write_text(
        '#include <behaviors.dtsi>\n'
        '#include <dt-bindings/zmk/bt.h>\n'
        '#include <dt-bindings/zmk/rgb.h>\n'
        '#include <dt-bindings/zmk/outputs.h>\n'
        '#include <dt-bindings/zmk/keys.h>\n\n'
        f'/* {spec["title"]} — {spec["blurb"]}\n'
        f' * Generated by tools/pagegen/make_presets.py from {BASE}. */\n\n'
        '/ {\n'
        '    behaviors {\n'
        '        gresc: grave_escape {\n'
        '            compatible = "zmk,behavior-mod-morph";\n'
        '            label = "GRAVE_ESCAPE";\n'
        '            #binding-cells = <0>;\n'
        '            bindings = <&kp ESC>, <&kp GRAVE>;\n'
        '            mods = <(MOD_LGUI|MOD_LSFT|MOD_RGUI|MOD_RSFT)>;\n'
        '        };\n'
        '    };\n'
        '    macros {\n'
        + ''.join(
            f'        bt_s{i}: bt_s{i} {{\n'
            f'            label = "bt_s{i}";\n'
            f'            compatible = "zmk,behavior-macro";\n'
            f'            #binding-cells = <0>;\n'
            f'            bindings = <&macro_tap &out OUT_BLE &bt BT_SEL {i}>;\n'
            f'        }};\n' for i in range(5))
        + '    };\n'
        '    keymap {\n'
        '        compatible = "zmk,keymap";\n\n'
        + '\n\n'.join(out)
        + '\n    };\n};\n')

    (d / 'preset.json').write_text(json.dumps({
        'base': BASE,
        'preset': True,
        'title': spec['title'],
        'blurb': spec['blurb'],
        'artifact': f'{shield}_left / {shield}_right',
    }, indent=2) + '\n')
    return shield


if __name__ == '__main__':
    positions, base_layers, order = load_base()
    print(f'base {BASE}: {len(positions)} positions, layers {order}')
    for shield, spec in PRESETS.items():
        emit(shield, spec, positions, base_layers, order)
        touched = sum(len(v) for k, v in spec.items() if isinstance(v, dict))
        print(f'  {shield:<18} {spec["title"]:<20} {touched} keys overridden')
