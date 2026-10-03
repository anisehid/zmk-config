"""Generate the preset keymap shields from a stock shield (anise60b by default).

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
# 'base' picks another stock shield; 'extra_layers' appends layers
# (node name, display name, overrides) that are &trans everywhere else.
# An extra layer named like a base layer replaces it in place instead.
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
    'anise60b_keyd': {
        'title': 'keyd',
        'name': 'ANISE60B-KEYD',
        'blurb': 'The Linux keyd remap in firmware: Caps is Escape, Ctrl and '
                 'Alt swapped, Fn1 holds '
                 'symbols and arrows, Fn2 holds F-keys (plus Ctrl for Fn3).',
        'default_layer': {
            (0, 0): '&kp ESC',
            (4, 0): '&kp LALT', (4, 2): '&kp LCTRL',
            (4, 11): '&kp RALT', (4, 13): '&kp RCTRL',
        },
        'extra_layers': [
            ('fn_layer', 'Sym', {
                (0, 0): '&kp CAPS',
                (1, 0): '&kp EQUAL', (1, 1): '&kp EXCL', (1, 2): '&kp N1',
                (1, 3): '&kp N2', (1, 4): '&kp N3', (1, 5): '&kp PRCNT',
                (1, 7): '&kp AMPS', (1, 8): '&kp STAR', (1, 9): '&kp LPAR',
                (1, 10): '&kp RPAR', (1, 11): '&kp PLUS', (1, 12): '&kp BSLH',
                (1, 13): '&kp PIPE', (1, 14): '&kp DEL',
                (2, 1): '&kp N0', (2, 2): '&kp N4', (2, 3): '&kp N5',
                (2, 4): '&kp N6', (2, 5): '&kp DLLR',
                (2, 7): '&kp LEFT', (2, 8): '&kp DOWN', (2, 9): '&kp UP',
                (2, 10): '&kp RIGHT', (2, 11): '&kp CARET', (2, 12): '&kp GRAVE',
                (3, 2): '&kp AT', (3, 3): '&kp N7', (3, 4): '&kp N8',
                (3, 5): '&kp N9', (3, 6): '&kp HASH',
                (3, 8): '&kp MINUS', (3, 9): '&kp HOME', (3, 10): '&kp PG_UP',
                (3, 11): '&kp PG_DN', (3, 12): '&kp END',
            }),
            ('fn2_layer', 'FKeys', {
                (4, 0): '&mo 3',
                (1, 2): '&kp F1', (1, 3): '&kp F2', (1, 4): '&kp F3',
                (2, 1): '&kp F10', (2, 2): '&kp F4', (2, 3): '&kp F5',
                (2, 4): '&kp F6',
                (3, 3): '&kp F7', (3, 4): '&kp F8', (3, 5): '&kp F9',
                (1, 12): '&kp F11', (1, 13): '&kp F12',
            }),
        ],
    },
}


def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', ' ', s, flags=re.S)
    return re.sub(r'//[^\n]*', ' ', s)


DISPLAY_NAMES = {}  # layer node -> display-name, filled by load_base()


def load_base(base):
    dtsi = (SHIELDS / base / f'{base}.dtsi').read_text()
    raw = dtsi.split('map = <')[1].split('>;')[0]
    positions = [(int(r), int(c))
                 for r, c in re.findall(r'RC\((\d+),\s*(\d+)\)', strip_comments(raw))]

    km = strip_comments((SHIELDS / base / f'{base}.keymap').read_text())
    body = km.split('compatible = "zmk,keymap"')[1]
    layers = {}
    order = []
    for lname, props, binds in re.findall(
            r'(\w+)\s*\{([^{}]*?)\bbindings\s*=\s*<(.*?)>\s*;', body, flags=re.S):
        name = re.search(r'display-name\s*=\s*"([^"]*)"', props)
        if name:
            DISPLAY_NAMES[lname] = name.group(1)
        toks = [' '.join(t.split()) for t in
                re.findall(r'&\s*[\w-]+(?:\s+[A-Za-z0-9_()]+)*', binds)]
        layers[lname] = toks
        order.append(lname)
    return positions, layers, order


def emit(shield, spec, positions, base_layers, order):
    BASE = spec.get('base', 'anise60b')
    base_layers, order, spec = dict(base_layers), list(order), dict(spec)
    for lname, display, overrides in spec.get('extra_layers', []):
        base_layers[lname] = ['&trans'] * len(positions)
        DISPLAY_NAMES[lname] = display
        if lname not in order:
            order.append(lname)
        spec[lname] = overrides
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
        name = (f'            display-name = "{DISPLAY_NAMES[lname]}";\n'
                if lname in DISPLAY_NAMES else '')
        out.append(f'        {lname} {{\n{name}            bindings = <\n'
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
    for shield, spec in PRESETS.items():
        emit(shield, spec, *load_base(spec.get('base', BASE)))
        touched = sum(len(v) for k, v in spec.items() if isinstance(v, dict)) + \
            sum(len(l[2]) for l in spec.get('extra_layers', []))
        print(f'  {shield:<18} {spec["title"]:<20} {touched} keys overridden')
