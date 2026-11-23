"""Component names and package defaults shared by generation and validation."""

import re
from collections import defaultdict


PACKAGE_DEFAULTS = {'com.google.android.googlequicksearchbox': 'rebirth_google'}
COMPONENT_PREFIX = 'ComponentInfo{'
PACKAGE = r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*'
# Android activity aliases also use names such as .Main-01 and .1.
ALIAS_SEGMENT = r'[A-Za-z0-9_$][A-Za-z0-9_$-]*'
ACTIVITY = rf'\.?{ALIAS_SEGMENT}(?:\.{ALIAS_SEGMENT})*'
COMPONENT = re.compile(f'({PACKAGE})/({ACTIVITY})')
LEGACY_ACTION = re.compile(r':[A-Z][A-Z0-9_]*')


def normalize_component(value, *, from_xml=False, allow_action=False):
    if allow_action and LEGACY_ACTION.fullmatch(value):
        return value
    text = value
    if from_xml:
        if not value.startswith(COMPONENT_PREFIX) or not value.endswith('}'):
            raise ValueError(f'Invalid appfilter component {value!r}')
        text = value[len(COMPONENT_PREFIX):-1]
    match = COMPONENT.fullmatch(text)
    if not match:
        raise ValueError(f'Invalid component {value!r}')
    package, activity = match.groups()
    if activity.startswith('.'):
        activity = package + activity
    return f'{package}/{activity}'


def catalog_mappings(catalog):
    components = {}
    package_icons = defaultdict(set)
    for item in catalog:
        drawable = item['id']
        packages = set()
        for raw in item['components']:
            component = normalize_component(raw)
            if component in components:
                raise ValueError(f'Duplicate component {component}: {components[component]}, {drawable}')
            components[component] = drawable
            package = component.split('/')[0]
            packages.add(package)
            package_icons[package].add(drawable)
        if not packages or sorted(packages) != sorted(item['packages']):
            raise ValueError(f'Component packages do not match the package list for {drawable}')

    for package, drawables in package_icons.items():
        if len(drawables) > 1 and PACKAGE_DEFAULTS.get(package) not in drawables:
            raise ValueError(f'Choose a package default for {package}: {sorted(drawables)}')
    for package, drawable in PACKAGE_DEFAULTS.items():
        if drawable not in package_icons.get(package, ()):
            raise ValueError(f'Package default {drawable} has no component for {package}')
    return components, package_icons
