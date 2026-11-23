#!/usr/bin/env python3
"""Check source artwork and actual launcher references before packaging."""

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

from appfilter import PACKAGE_DEFAULTS, catalog_mappings, normalize_component

ROOT = Path(__file__).resolve().parents[1]
REGIONS = ('CN', 'JP', 'Global')
FALLBACKS = {
    'iconback': 'rebirth_fallback_back',
    'iconmask': 'rebirth_fallback_mask',
    'iconupon': 'rebirth_fallback_upon',
}
GOOGLE = 'com.google.android.googlequicksearchbox'
GOOGLE_CALENDAR = 'com.google.android.calendar'
ALIPAY = 'com.eg.android.AlipayGphone'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_artwork(catalog):
    require(sum(item['collection'] == 'new' for item in catalog) >= 500, 'Catalog has fewer than 500 new icons')
    ids = set()
    sources = set()
    for item in catalog:
        name = item['id']
        require(re.fullmatch(r'rebirth_[a-z0-9_]+', name), f'Invalid resource name: {name}')
        require(name not in ids, f'Duplicate artwork id: {name}')
        require(item['region'] in REGIONS, f'Invalid region for {name}')
        ids.add(name)
        artwork_format = item.get('format', 'svg')
        require(artwork_format in ('svg', 'png'), f'Invalid artwork format for {name}')
        source = ROOT / 'artwork/icons' / f'{name}.{artwork_format}'
        sources.add(source)

        if artwork_format == 'png':
            generation = item['generation']
            with Image.open(source) as image:
                require(image.format == 'PNG' and image.mode == 'RGBA', f'Expected an RGBA PNG: {source.name}')
                require(image.size == (384, 384) and image.size == tuple(generation['source_size']),
                        f'Unexpected source size: {source.name}')
                alpha = image.getchannel('A')
                require(alpha.getextrema() == (0, 255), f'Expected transparent and opaque pixels: {source.name}')
                left, top, right, bottom = alpha.getbbox()
                require(left > 0 and top > 0 and right < image.width and bottom < image.height,
                        f'Artwork touches the canvas edge: {source.name}')
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            require(digest == generation['source_sha256'], f'Artwork hash mismatch: {source.name}')
        else:
            require(re.fullmatch(r'#[A-Fa-f0-9]{6}', item['background']), f'Invalid background: {source.name}')
            svg = ET.parse(source).getroot()
            require(svg.get('viewBox') == '0 0 256 256', f'Invalid viewBox: {source.name}')
            for node in svg.iter():
                tag = node.tag.split('}')[-1]
                require(tag not in ('image', 'script', 'foreignObject', 'text'), f'Unsupported SVG element {tag}: {source.name}')
                require(not any('href' in key or key.lower().startswith('on') for key in node.attrib),
                        f'Unsupported SVG attributes: {source.name}')

    actual = {path for path in (ROOT / 'artwork/icons').iterdir() if path.suffix in {'.svg', '.png'}}
    require(actual == sources, f'Uncataloged or missing artwork: {sorted(actual ^ sources)}')
    return ids


def load_appfilter(root, drawables):
    require(root.tag == 'resources', 'appfilter.xml must have a resources root')
    items, calendars = {}, {}
    exact, defaults = {}, {}
    fallback_tags = set()
    for element in root:
        tag = element.tag
        if tag in FALLBACKS:
            require(tag not in fallback_tags, f'Duplicate fallback tag {tag}')
            require(element.attrib == {'img1': FALLBACKS[tag]}, f'Unexpected {tag} fallback resource')
            fallback_tags.add(tag)
            continue
        if tag == 'scale':
            require(tag not in fallback_tags, 'Duplicate fallback scale')
            require(0 < float(element.attrib['factor']) <= 1, 'Invalid fallback scale')
            fallback_tags.add(tag)
            continue

        require(tag in {'item', 'calendar'} and not list(element), f'Unexpected appfilter element {tag}')
        component = normalize_component(element.get('component', ''), from_xml=True, allow_action=tag == 'item')
        if tag == 'calendar':
            name = element.attrib['prefix']
            require(component not in calendars, f'Duplicate calendar component {component}')
            require(not items, f'Calendar follows a static item: {component}')
            require(name and all(f'{name}{day}' in drawables for day in range(1, 32)),
                    f'Missing days for calendar {component}: {name!r}')
            calendars[component] = name
        else:
            name = element.attrib['drawable']
            require(component not in items, f'Duplicate item component {component}')
            require(name in drawables, f'Missing drawable {name!r} for {component}')
            items[component] = name

        # LocalSource.loadIconPack skips action-only keys. An existing calendar
        # protects its exact key, and the first accepted entry sets the package icon.
        if component.startswith(':') or (component in exact and exact[component][0] == 'calendar'):
            continue
        exact[component] = tag, name
        defaults.setdefault(component.split('/')[0], (tag, name))

    require(fallback_tags == FALLBACKS.keys() | {'scale'}, 'Missing fallback entries in appfilter.xml')
    return items, exact, defaults


def validate_resolution(rebirth, package_icons, items, exact, defaults):
    original = ET.parse(ROOT / 'catalog/original-appfilter.xml').getroot()
    expected_calendars = {}
    calendar_defaults = {}
    for element in original.findall('calendar'):
        component = normalize_component(element.attrib['component'], from_xml=True)
        entry = 'calendar', element.attrib['prefix']
        expected_calendars.setdefault(component, entry)
        calendar_defaults.setdefault(component.split('/')[0], entry)
    require({component: entry for component, entry in exact.items() if entry[0] == 'calendar'} == expected_calendars,
            'Generated calendar mappings differ from the original daily icon mappings')
    for package, expected in calendar_defaults.items():
        require(defaults.get(package) == expected, f'Incorrect calendar package default for {package}: {defaults.get(package)}')

    for component, drawable in rebirth.items():
        require(items.get(component) == drawable, f'Catalog component is missing or mismapped: {component} → {drawable}')

    for package, icons in package_icons.items():
        if package in calendar_defaults:
            continue
        drawable = PACKAGE_DEFAULTS[package] if package in PACKAGE_DEFAULTS else next(iter(icons))
        expected = 'item', drawable
        require(defaults.get(package) == expected,
                f'Incorrect package default for {package}: {defaults.get(package)} instead of {expected}')

    for component, drawable in items.items():
        icons = package_icons.get(component.split('/')[0], ())
        require(len(icons) != 1 or drawable in icons, f'Legacy drawable overrides the Rebirth icon for {component}')

    # These checks also catch deletions from the catalog itself.
    required = {
        'rebirth_alipay': (
            f'{ALIPAY}/com.alipay.mobile.quinox.LauncherActivity',
            f'{ALIPAY}/com.alipay.mobile.quinox.LauncherActivity.alias',
        ),
        'rebirth_com_google_android_apps_bard': (
            'com.google.android.apps.bard/com.google.android.apps.bard.shellapp.BardEntryPointActivity',
            'com.google.android.apps.bard/com.google.android.apps.bard.shellapp.VisualInterpreterShortcutActivity',
            f'{GOOGLE}/com.google.android.apps.search.assistant.surfaces.voice.deeplinks.handlers.gateway.impl.GeminiGatewayActivity',
            f'{GOOGLE}/com.google.android.apps.search.assistant.surfaces.voice.deeplinks.handlers.gateway.impl.SharedConversationDeeplinkGateway',
            f'{GOOGLE}/com.google.android.apps.search.assistant.surfaces.voice.robin.launcher.NotebooksShortcutGatewayActivity',
            f'{GOOGLE}/com.google.android.apps.search.assistant.surfaces.voice.robin.launcher.ProcessTextGatewayActivity',
            f'{GOOGLE}/com.google.android.apps.search.assistant.surfaces.voice.robin.launcher.RobinEntryPointActivity',
            f'{GOOGLE}/com.google.android.apps.search.assistant.surfaces.voice.robin.main.MainActivity',
            f'{GOOGLE}/com.google.android.apps.search.assistant.surfaces.voice.robin.ui.floaty.activity.FloatyActivity',
            f'{GOOGLE}/com.google.android.libraries.search.integrations.notifications.gemini.entrypoints.GeminiSystemTrayActivity',
        ),
        'rebirth_googlelens': (
            'com.google.ar.lens/com.google.vr.apps.ornament.app.lens.LensLauncherActivity',
            f'{GOOGLE}/com.google.android.apps.lens.MainActivity',
            f'{GOOGLE}/com.google.android.apps.lens.SearchImageActivity',
            f'{GOOGLE}/com.google.android.apps.search.lens.LensActivity',
            f'{GOOGLE}/com.google.android.apps.search.lens.LensShareEntryPointActivity',
            f'{GOOGLE}/com.google.android.apps.search.lens.live.deeplink.LiveActivity',
        ),
        'rebirth_com_google_android_apps_weather': (
            'com.google.android.apps.weather/com.google.android.apps.weather.home.HomeActivity',
            f'{GOOGLE}/com.google.android.apps.search.weather.WeatherActivity',
            f'{GOOGLE}/com.google.android.apps.search.weather.entrypoints.appicon.WeatherAppIconActivity',
        ),
        'rebirth_googleassistant': (
            f'{GOOGLE}/com.google.android.apps.gsa.staticplugins.opa.EnterOpaActivityFromLauncher',
            f'{GOOGLE}/com.google.android.apps.gsa.staticplugins.opa.OpaActivity',
        ),
        'rebirth_com_baidu_netdisk': (
            'com.baidu.netdisk.samsung/com.baidu.netdisk.ui.DefaultMainActivity',
            'com.baidu.netdisk.samsung/com.baidu.netdisk.ui.Navigate',
            'com.baidu.netdisk.samsung/com.baidu.netdisk.ui.OPLauncherActivity',
            'com.baidu.netdisk.samsung/com.baidu.netdisk.ui.SvipLauncherActivity',
        ),
        'camera': ('com.android.gallery3d/com.android.camera.CameraLauncher',),
        'gallery': ('com.android.gallery3d/com.android.gallery3d.app.GalleryActivity',),
        'download': (
            'com.android.providers.downloads/com.android.providers.downloads.ui.DownloadList',
            'com.android.providers.downloads.ui/com.android.providers.downloads.ui.TrampolineActivity',
            'com.google.android.documentsui/com.android.documentsui.LauncherActivity',
            'com.google.android.documentsui/com.android.documentsui.files.FilesActivity',
        ),
        'xiaomi_download': (
            'com.android.providers.downloads/xiaomi',
            'com.android.providers.downloads.ui/xiaomi',
        ),
        'sound_recorder': ('com.android.soundrecorder/com.android.soundrecorder.SoundRecorder',),
        'flyme_soundrecorder': ('com.android.soundrecorder/com.android.soundrecorder.MzRecorderActivity',),
        'google_play_music': (
            'com.google.android.music/com.android.music.activitymanagement.TopLevelActivity',
            'com.google.android.music/com.google.android.music.tombstone.LauncherActivity',
        ),
        'ookla_speedtest': ('org.zwanoo.android.speedtest/com.ookla.mobile4.screens.main.MainActivity',),
    }
    for drawable, components in required.items():
        for component in components:
            require(exact.get(component) == ('item', drawable), f'{component} must resolve to {drawable}')
    require(defaults.get(ALIPAY) == ('item', 'rebirth_alipay'), 'Alipay package default changed')
    require(defaults.get(GOOGLE) == ('item', 'rebirth_google'), 'Google package default changed')
    for package, drawable in (
        ('com.android.gallery3d', 'gallery'),
        ('com.android.providers.downloads', 'download'),
        ('com.android.providers.downloads.ui', 'download'),
        ('com.android.soundrecorder', 'sound_recorder'),
        ('com.google.android.documentsui', 'download'),
        ('com.google.android.music', 'google_play_music'),
        ('org.zwanoo.android.speedtest', 'ookla_speedtest'),
    ):
        require(defaults.get(package) == ('item', drawable),
                f'Original package default changed for {package}: {defaults.get(package)} instead of {drawable}')
    calendar = 'calendar', 'google_calendar_'
    require(defaults.get(GOOGLE_CALENDAR) == calendar, 'Google Calendar package default must stay dynamic')
    require(exact.get(f'{GOOGLE_CALENDAR}/com.android.calendar.AllInOneActivity') == calendar,
            'Google Calendar main activity must stay dynamic')


def validate_metadata(catalog, original, drawables, items):
    resources = ROOT / 'app/res/xml'
    assets = ROOT / 'app/assets'
    for name in ('appfilter.xml', 'drawable.xml'):
        require((assets / name).read_bytes() == (resources / name).read_bytes(), f'Asset and resource {name} differ')
    listed = [element.attrib['drawable'] for element in ET.parse(resources / 'drawable.xml').getroot().findall('item')]
    require(len(listed) == len(drawables) and set(listed) == drawables, 'drawable.xml inventory differs from the artwork')

    rows = [(item['id'], item['label'].replace('\t', ' '), item['region'], ' '.join(item['packages'])) for item in catalog]
    rows.extend((name, name.replace('_', ' '), 'Original', '') for name in sorted(original))
    actual = [tuple(line.split('\t')) for line in (assets / 'catalog.tsv').read_text(encoding='utf-8').splitlines()]
    require(actual == rows, 'catalog.tsv differs from the artwork catalog')

    stats = json.loads((ROOT / 'catalog/stats.json').read_text(encoding='utf-8'))
    png_count = sum(item.get('format') == 'png' for item in catalog)
    expected = dict(svg_icons=len(catalog) - png_count, png_icons=png_count, rebirth_icons=len(catalog),
                    original_icons=len(original), total_icons=len(drawables), component_mappings=len(items),
                    packages=len({package for item in catalog for package in item['packages']}),
                    regions={region: sum(item['region'] == region for item in catalog) for region in REGIONS})
    require(stats == expected, f'catalog/stats.json differs from generated metadata. Expected {expected}')


def main():
    catalog = json.loads((ROOT / 'catalog/icons.json').read_text(encoding='utf-8'))
    ids = validate_artwork(catalog)
    rebirth, package_icons = catalog_mappings(catalog)
    original = {path.stem for path in (ROOT / 'artwork/original').glob('*.png')}
    require(ids.isdisjoint(original), 'Original and Rebirth resource names collide')
    drawables = ids | original
    for name in FALLBACKS.values():
        svg = ET.parse(ROOT / 'artwork/fallback' / f'{name}.svg').getroot()
        require(svg.tag == '{http://www.w3.org/2000/svg}svg' and svg.get('viewBox') == '0 0 256 256',
                f'Invalid fallback artwork {name}')

    root = ET.parse(ROOT / 'app/res/xml/appfilter.xml').getroot()
    items, exact, defaults = load_appfilter(root, drawables)
    validate_resolution(rebirth, package_icons, items, exact, defaults)
    validate_metadata(catalog, original, drawables, items)
    print(f'Validated {len(catalog)} Rebirth icons, {len(rebirth)} catalog components, '
          f'{len(items)} appfilter items, {len(drawables)} total icon resources, and Global Icon Pack defaults.')


if __name__ == '__main__':
    main()
