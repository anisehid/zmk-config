"""Render the keymap browser to docs/index.html.

Usage (from repo root):  python3 tools/pagegen/build.py
"""
import json
import pathlib
import subprocess

import parse as parser  # noqa: E402  (same directory)

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'docs' / 'index.html'


def git(*args, default='unknown'):
    try:
        return subprocess.run(['git', *args], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return default


def main():
    data = parser.main()
    build = {'commit': git('rev-parse', '--short', 'HEAD')}

    html = (HERE / 'template.html').read_text()
    html = html.replace('/*__DATA__*/', json.dumps(data, separators=(',', ':')))
    html = html.replace('/*__BUILD__*/', json.dumps(build))
    if '__DATA__' in html or '__BUILD__' in html:
        raise SystemExit('placeholder substitution failed')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    (OUT.parent / '.nojekyll').write_text('')

    stock = [k for k, v in data.items() if not v.get('preset')]
    preset = [k for k, v in data.items() if v.get('preset')]
    print(f'\nwrote {OUT.relative_to(ROOT)}  ({len(html):,} bytes)')
    print(f'  stock   : {", ".join(stock)}')
    print(f'  presets : {", ".join(preset)}')


if __name__ == '__main__':
    main()
