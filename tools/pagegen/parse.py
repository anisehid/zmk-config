"""Parse every anise shield's matrix transform + keymap into one JSON blob.

Used by tools/pagegen/build.py to generate the GitHub Pages keymap browser,
so the published layouts can never drift from the firmware source.
"""
import re
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SHIELDS_DIR = ROOT / 'config' / 'boards' / 'shields'


def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', ' ', s, flags=re.S)
    return re.sub(r'//[^\n]*', ' ', s)


def read_positions(shield_dir, name, base=None):
    """Return [(row, col), ...] in keymap-binding order."""
    # Preset shields carry no transform of their own; they declare the shield
    # they inherit it from in preset.json.
    dtsi = (SHIELDS_DIR / base / f'{base}.dtsi') if base else (shield_dir / f'{name}.dtsi')
    if not dtsi.exists():
        raise SystemExit(f'{name}: no matrix transform at {dtsi}')
    raw = dtsi.read_text().split('map = <')[1].split('>;')[0]
    return [(int(r), int(c))
            for r, c in re.findall(r'RC\((\d+),\s*(\d+)\)', strip_comments(raw))]


def read_geometry(name):
    """Physical key rects [w, h, x, y] (1u = 100) from <name>-layouts.dtsi, or None."""
    f = SHIELDS_DIR / name / f'{name}-layouts.dtsi'
    if not f.exists():
        return None
    return [[int(v) for v in m] for m in re.findall(
        r'&key_physical_attrs\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', strip_comments(f.read_text()))]


def read_layers(shield_dir, name):
    km = strip_comments((shield_dir / f'{name}.keymap').read_text())
    body = km.split('compatible = "zmk,keymap"')[1]
    layers = []
    for lname, props, binds in re.findall(
            r'(\w+)\s*\{([^{}]*?)\bbindings\s*=\s*<(.*?)>\s*;', body, flags=re.S):
        label = re.search(r'display-name\s*=\s*"([^"]*)"', props)
        toks = [' '.join(t.split()) for t in
                re.findall(r'&\s*[\w-]+(?:\s+[A-Za-z0-9_()]+)*', binds)]
        layers.append({'name': lname, 'label': label and label.group(1), 'bindings': toks})
    return layers


def parse_shield(shield_dir):
    name = shield_dir.name
    meta_file = shield_dir / 'preset.json'
    meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}
    positions = read_positions(shield_dir, name, meta.get('base'))
    layers = read_layers(shield_dir, name)
    warnings = []
    for layer in layers:
        extra = len(layer['bindings']) - len(positions)
        if extra:
            warnings.append(
                f"{layer['name']}: {len(layer['bindings'])} bindings vs "
                f"{len(positions)} matrix positions "
                f"({'+' if extra > 0 else ''}{extra})")
            print(f'  ! {name}/{warnings[-1]}', file=sys.stderr)
        # ZMK indexes bindings positionally, so surplus entries are dropped
        # and missing ones leave the tail unbound. Mirror that here.
        layer['bindings'] = (layer['bindings'] + ['&none'] * max(0, -extra))[:len(positions)]
    geom = read_geometry(meta.get('base', name))
    if geom and len(geom) != len(positions):
        print(f'  ! {name}: layout has {len(geom)} keys, transform {len(positions)}; '
              'drawing a grid instead', file=sys.stderr)
        geom = None
    return {'positions': positions, 'geom': geom, 'layers': layers,
            'warnings': warnings, **meta}


def main():
    out = {}
    for d in sorted(SHIELDS_DIR.iterdir()):
        if not d.is_dir() or not (d / f'{d.name}.keymap').exists():
            continue
        out[d.name] = parse_shield(d)
        print(f'  {d.name}: {len(out[d.name]["positions"])} keys, '
              f'{len(out[d.name]["layers"])} layers', file=sys.stderr)
    if not out:
        raise SystemExit('no shields found')
    return out


if __name__ == '__main__':
    print(json.dumps(main(), separators=(',', ':')))
