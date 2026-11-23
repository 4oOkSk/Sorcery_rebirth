#!/usr/bin/env python3
"""Generate launcher metadata and a gallery for the catalog's source artwork."""
import copy
import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from appfilter import COMPONENT_PREFIX, PACKAGE_DEFAULTS, catalog_mappings, normalize_component

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
CATALOG = json.loads((ROOT / 'catalog/icons.json').read_text(encoding='utf-8'))
OVERRIDES, PACKAGE_ICONS = catalog_mappings(CATALOG)
CUSTOM = ET.parse(ROOT / 'artwork/custom.svg').getroot() if (ROOT / 'artwork/custom.svg').exists() else ET.Element('svg')
for generated in (ROOT / 'artwork/icons').glob('rebirth_*.svg'):
    if generated.stem not in {item['id'] for item in CATALOG if item.get('format', 'svg') == 'svg'}:
        generated.unlink()


def luminance(color):
    values = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    return sum(a*b for a, b in zip(values, [.2126, .7152, .0722]))


def markup(item):
    glyph = item['glyph']
    if glyph.startswith('custom_'):
        source = next(x for x in CUSTOM if x.get('id') == glyph)
    else:
        source = ET.parse(ROOT / 'artwork/glyphs' / (glyph + '.svg')).getroot()
    # Metadata and invisible placeholder rectangles are not part of the mark.
    body = []
    for node in source:
        if node.tag.split('}')[-1] in ('title', 'desc', 'metadata'):
            continue
        node = copy.deepcopy(node)
        if node.get('stroke') == 'none' and node.get('fill') == 'none':
            continue
        body.append(ET.tostring(node, encoding='unicode'))
    content = ''.join(body).replace('ns0:', '').replace(':ns0', '')
    if glyph.startswith('ti_'):
        return '<g fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round">' + content + '</g>'
    return '<g fill="currentColor">' + content + '</g>'


for item in CATALOG:
    if item.get('format', 'svg') == 'png':
        continue
    color = item['background']
    foreground = '#303334' if luminance(color) > .67 else '#fffdf8'
    glyph = markup(item)
    label = html.escape(item['label'])
    # 202.67/256 matches Sorcery's 152/192 paper face. The edge and shadow
    # use vector geometry so SVG exports remain sharp at every size.
    svg = f'''<svg xmlns="{NS}" width="256" height="256" viewBox="0 0 256 256" role="img" aria-labelledby="title">
<title id="title">{label}</title>
<desc>Sorcery_rebirth. {html.escape(item['license'])}. Source: {html.escape(item['source'])}</desc>
<defs><linearGradient id="paper" x1="0" y1="0" x2="0.25" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#fff" stop-opacity=".12"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".08"/></linearGradient></defs>
<rect x="28" y="33" width="202" height="202" rx="12" fill="#17212a" opacity=".08"/>
<rect x="27" y="30" width="202" height="202" rx="12" fill="#17212a" opacity=".13"/>
<rect x="27" y="27" width="202" height="202" rx="12" fill="{color}"/>
<rect x="27" y="27" width="202" height="202" rx="12" fill="url(#paper)"/>
<path d="M39 28h178q10 0 11 11" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="1.4"/>
<g transform="translate(67 70) scale(5.083333)" color="#13252b" opacity=".13">{glyph}</g>
<g transform="translate(67 67) scale(5.083333)" color="{foreground}">{glyph}</g>
</svg>
'''
    (ROOT / 'artwork/icons' / (item['id'] + '.svg')).write_text(svg)


# Compatibility fixes for the preserved Sorcery source XML.
ORIGINAL_COMPONENT_FIXES = {
    'ComponentInfo{com.Latour.Maestria/com.unity3d.player.UnityPlayerNativeActivity}'
    'com.Latour.Maestria/com.unity3d.player.UnityPlayerNativeActivit}':
        'ComponentInfo{com.Latour.Maestria/com.unity3d.player.UnityPlayerNativeActivity}',
}
ORIGINAL_DRAWABLE_FIXES = {
    'com.android.contacts/com.oneplus.contacts.activities.OPDialtactsActivity': 'oneplus_dialer',
}
ORIGINAL_PACKAGE_DEFAULTS = {
    'com.android.gallery3d': 'gallery',
    'com.android.providers.downloads': 'download',
    'com.android.soundrecorder': 'sound_recorder',
}
ORIGINAL_ALIASES = {
    'cn.wps.moffice_eng/cn.wps.moffice.documentmanager.ab.proxy.main': 'wps',
    'com.android.providers.downloads.ui/com.android.providers.downloads.ui.TrampolineActivity': 'download',
    'com.google.android.documentsui/com.android.documentsui.LauncherActivity': 'download',
    'com.google.android.documentsui/com.android.documentsui.files.FilesActivity': 'download',
    'com.google.android.music/com.google.android.music.tombstone.LauncherActivity': 'google_play_music',
    'com.tencent.androidqqmail/com.tencent.qqmail.launcher.desktop.LauncherActivity': 'tencent_qq_mail',
    'jp.dominos.android.orderapp/com.arizona.MainActivity': 'domino_pizza',
    'org.zwanoo.android.speedtest/com.ookla.mobile4.screens.main.MainActivity': 'ookla_speedtest',
}


def add_mapping(root, tag, component, attribute, drawable):
    if not component.startswith(':'):
        component = f'{COMPONENT_PREFIX}{component}}}'
    ET.SubElement(root, tag, {'component': component, attribute: drawable})


def appfilter(original, original_names):
    root = ET.Element('resources')
    for tag, attributes in [
        ('iconback', {'img1': 'rebirth_fallback_back'}),
        ('iconmask', {'img1': 'rebirth_fallback_mask'}),
        ('iconupon', {'img1': 'rebirth_fallback_upon'}),
        ('scale', {'factor': '0.70'}),
    ]:
        ET.SubElement(root, tag, attributes)

    # Global Icon Pack protects calendar entries and uses the first entry for
    # each package as its default. Keep the first prefix for identical OEM keys.
    calendars = set()
    for item in original.findall('calendar'):
        component = normalize_component(item.attrib['component'], from_xml=True)
        prefix = item.attrib['prefix']
        if not prefix or not all(f'{prefix}{day}' in original_names for day in range(1, 32)):
            raise ValueError(f'Missing calendar resources for {component}: {prefix!r}')
        if component not in calendars:
            add_mapping(root, 'calendar', component, 'prefix', prefix)
            calendars.add(component)

    def rebirth_order(component):
        package = component.split('/')[0]
        return package, OVERRIDES[component] != PACKAGE_DEFAULTS.get(package), component

    for component in sorted(OVERRIDES, key=rebirth_order):
        add_mapping(root, 'item', component, 'drawable', OVERRIDES[component])

    legacy = {}
    for item in original.findall('item'):
        raw = item.attrib['component']
        component = normalize_component(ORIGINAL_COMPONENT_FIXES.get(raw, raw), from_xml=True, allow_action=True)
        drawable = item.attrib['drawable']
        if drawable == 'contracts':
            drawable = 'contacts'
        legacy.setdefault(component, ORIGINAL_DRAWABLE_FIXES.get(component, drawable))
    legacy.update({normalize_component(component): drawable for component, drawable in ORIGINAL_ALIASES.items()})

    def legacy_order(component):
        package = component.split('/')[0]
        return legacy[component] != ORIGINAL_PACKAGE_DEFAULTS.get(package)

    for component in sorted(legacy, key=legacy_order):
        if component in OVERRIDES:
            continue
        drawable = legacy[component]
        if drawable not in original_names:
            raise ValueError(f'Missing original drawable for {component}: {drawable!r}')
        package = component.split('/')[0]
        owners = PACKAGE_ICONS.get(package, ())
        if len(owners) == 1:
            drawable = next(iter(owners))
        add_mapping(root, 'item', component, 'drawable', drawable)
    return root


all_png = {x.stem for x in (ROOT / 'artwork/original').glob('*.png')}
new_names = {x['id'] for x in CATALOG}
root = appfilter(ET.parse(ROOT / 'catalog/original-appfilter.xml').getroot(), all_png)
ET.indent(root)
filter_data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
(ROOT / 'app/res/xml/appfilter.xml').write_bytes(filter_data)

drawable_root = ET.Element('resources')
for category, items in [('Rebirth', sorted(new_names)), ('Sorcery · Original', sorted(all_png))]:
    ET.SubElement(drawable_root, 'category', dict(title=category))
    for name in items:
        ET.SubElement(drawable_root, 'item', dict(drawable=name))
ET.indent(drawable_root)
(ROOT / 'app/res/xml/drawable.xml').write_bytes(ET.tostring(drawable_root, encoding='utf-8', xml_declaration=True))

# Public gallery data uses relative paths and works from the repository or an
# extracted release archive without a server or a third-party CDN.
gallery = []
for item in CATALOG:
    gallery.append(dict(label=item['label'], region=item['region'], collection=item['collection'],
                        id=item['id'], packages=item['packages'],
                        source='../artwork/icons/' + item['id'] + '.' + item.get('format', 'svg')))
for name in sorted(all_png):
    gallery.append(dict(label=name.replace('_', ' '), region='Original', collection='original',
                        id=name, packages=[], source='../artwork/original/' + name + '.png'))
data = json.dumps(gallery, ensure_ascii=False).replace('</', '<\\/')
template = (ROOT / 'docs/gallery.template.html').read_text(encoding='utf-8')
(ROOT / 'docs/gallery.html').write_text(template.replace('/*CATALOG*/[]', data), encoding='utf-8')

# Dashboard list is a simple TSV, allowing Android's standard resource loader
# to discover the same generated PNGs used by launchers.
assets = ROOT / 'app/assets'
assets.mkdir(exist_ok=True)
rows = [(x['id'], x['label'].replace('\t', ' '), x['region'], ' '.join(x['packages'])) for x in CATALOG]
rows.extend((name, name.replace('_', ' '), 'Original', '') for name in sorted(all_png))
(assets / 'catalog.tsv').write_text('\n'.join('\t'.join(row) for row in rows) + '\n', encoding='utf-8')
for name in ['appfilter.xml', 'drawable.xml']:
    (assets / name).write_bytes((ROOT / 'app/res/xml' / name).read_bytes())

stats = dict(svg_icons=sum(x.get('format', 'svg') == 'svg' for x in CATALOG),
             png_icons=sum(x.get('format', 'svg') == 'png' for x in CATALOG),
             rebirth_icons=len(CATALOG), original_icons=len(all_png),
             total_icons=len(CATALOG) + len(all_png), component_mappings=len(root.findall('item')),
             packages=len({p for x in CATALOG for p in x['packages']}),
             regions={region: sum(x['region'] == region for x in CATALOG) for region in ['CN', 'JP', 'Global']})
(ROOT / 'catalog/stats.json').write_text(json.dumps(stats, indent=2) + '\n')
print(json.dumps(stats, indent=2))
