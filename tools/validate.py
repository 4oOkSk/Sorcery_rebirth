#!/usr/bin/env python3
"""Check source artwork and actual launcher references before packaging."""
import json
import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'catalog/icons.json').read_text())
assert len([x for x in catalog if x['collection'] == 'new']) >= 500
ids = set()
components = {}
for item in catalog:
    assert re.fullmatch('[a-z][a-z0-9_]*', item['id']), item['id']
    assert item['id'] not in ids, item['id']
    ids.add(item['id'])
    assert item['packages'] and item['components'], item['id']
    artwork_format = item.get('format', 'svg')
    assert artwork_format in ('svg', 'png'), item['id']
    source = ROOT / 'artwork/icons' / (item['id'] + '.' + artwork_format)
    if artwork_format == 'png':
        from PIL import Image
        with Image.open(source) as image:
            image.load()
            assert image.format == 'PNG' and image.mode == 'RGBA', source
            assert image.width == image.height and image.width >= 192, source
            assert image.getchannel('A').getextrema() == (0, 255), source
            assert image.getchannel('A').getpixel((0, 0)) == 0, source
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item['generation']['source_sha256'], source
    else:
        assert re.fullmatch('#[A-Fa-f0-9]{6}', item['background'])
        svg = ET.parse(source).getroot()
        assert svg.get('viewBox') == '0 0 256 256'
        for node in svg.iter():
            tag = node.tag.split('}')[-1]
            assert tag not in ('image', 'script', 'foreignObject', 'text'), (source, tag)
            assert not any('href' in k for k in node.attrib), source
            assert not any(k.lower().startswith('on') for k in node.attrib), source
    for component in item['components']:
        package, activity = component.split('/', 1)
        assert package in item['packages'], component
        assert activity and component not in components, ('Duplicate component', component, item['id'], components.get(component))
        components[component] = item['id']
drawables = ids | {x.stem for x in (ROOT / 'artwork/original').glob('*.png')}
seen = set()
for item in ET.parse(ROOT / 'app/res/xml/appfilter.xml').getroot():
    if item.get('drawable'):
        assert item.get('drawable') in drawables, item.attrib
        component = item.get('component')
        assert component not in seen, component
        seen.add(component)
stats = json.loads((ROOT / 'catalog/stats.json').read_text())
assert stats['svg_icons'] == sum(x.get('format', 'svg') == 'svg' for x in catalog)
assert stats.get('png_icons', 0) == sum(x.get('format', 'svg') == 'png' for x in catalog)
assert stats['total_icons'] == len(drawables)
print(f"Validated {len(catalog)} icons, {len(components)} component mappings, {len(drawables)} total icon resources.")
