#!/usr/bin/env python3
"""Extract transparent artwork from a 3×3 sheet and match Sorcery optical sizes."""
import argparse
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter


def _box_distance(a, b):
    dx = max(0, a[0] - b[2], b[0] - a[2])
    dy = max(0, a[1] - b[3], b[1] - a[3])
    return (dx * dx + dy * dy) ** .5


def extract(sheet, index, size=384):
    row, column = divmod(index, 3)
    sheet = sheet.convert('RGBA')
    grid = 384
    mask = sheet.getchannel('A').resize((grid, grid), Image.Resampling.BILINEAR).point(lambda x: 255 if x >= 80 else 0)
    pixels = bytearray(mask.tobytes())
    components = []
    for start in range(len(pixels)):
        if not pixels[start]:
            continue
        queue, component = [start], []
        pixels[start] = 0
        min_x = max_x = start % grid
        min_y = max_y = start // grid
        sum_x = sum_y = 0
        while queue:
            cur = queue.pop()
            component.append(cur)
            x, y = cur % grid, cur // grid
            sum_x += x
            sum_y += y
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
            if x and pixels[cur - 1]:
                pixels[cur - 1] = 0
                queue.append(cur - 1)
            if x < grid - 1 and pixels[cur + 1]:
                pixels[cur + 1] = 0
                queue.append(cur + 1)
            if y and pixels[cur - grid]:
                pixels[cur - grid] = 0
                queue.append(cur - grid)
            if y < grid - 1 and pixels[cur + grid]:
                pixels[cur + grid] = 0
                queue.append(cur + grid)
        if len(component) >= 6:
            components.append({
                'pixels': component,
                'len': len(component),
                'cx': sum_x / len(component),
                'cy': sum_y / len(component),
                'box': (min_x, min_y, max_x + 1, max_y + 1),
            })
    mains = {}
    for comp in components:
        key = (min(2, max(0, int(comp['cy'] / 128))), min(2, max(0, int(comp['cx'] / 128))))
        if key not in mains or comp['len'] > mains[key]['len']:
            mains[key] = comp
    main = mains.get((row, column))
    assert main, 'Empty cell'
    selected = [main]
    for comp in components:
        if comp is main or comp['len'] < max(6, main['len'] * .006):
            continue
        nearest = min(mains, key=lambda key: _box_distance(comp['box'], mains[key]['box']))
        if nearest == (row, column) and _box_distance(comp['box'], main['box']) <= 18:
            selected.append(comp)
    clean = bytearray(grid * grid)
    for comp in selected:
        for pos in comp['pixels']:
            clean[pos] = 255
    clean_mask = Image.frombytes('L', (grid, grid), bytes(clean)).filter(ImageFilter.MaxFilter(5))
    bx0 = min(comp['box'][0] for comp in selected)
    by0 = min(comp['box'][1] for comp in selected)
    bx1 = max(comp['box'][2] for comp in selected)
    by1 = max(comp['box'][3] for comp in selected)
    sx0 = max(0, int((bx0 - 6) * sheet.width / grid))
    sy0 = max(0, int((by0 - 6) * sheet.height / grid))
    sx1 = min(sheet.width, int((bx1 + 6) * sheet.width / grid))
    sy1 = min(sheet.height, int((by1 + 6) * sheet.height / grid))
    image = sheet.crop((sx0, sy0, sx1, sy1))
    sub_mask = clean_mask.resize(sheet.size, Image.Resampling.BILINEAR).crop((sx0, sy0, sx1, sy1))
    image.putalpha(ImageChops.multiply(image.getchannel('A'), sub_mask))
    solid = image.getchannel('A').point(lambda x: 255 if x >= 230 else 0)
    bounds = solid.getbbox()
    assert bounds, 'No opaque artwork'
    width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
    assert min(width, height) > sheet.width / 3 * .2, 'Artwork too small'
    filled = sum(solid.histogram()[1:]) / (width * height)
    solid_area = sum(solid.histogram()[1:])
    target_side = (152.0 if filled > .88 else 155.0) * size / 192
    max_span = (152 if filled > .94 and .95 <= width / height <= 1.05 else 166) * size / 192
    scale = min(max_span / max(width, height), target_side / (solid_area ** .5))
    padding = max(8, round(sheet.width / 3 * .025))
    padded = (max(0, bounds[0] - padding), max(0, bounds[1] - padding),
              min(image.width, bounds[2] + padding), min(image.height, bounds[3] + padding))
    image = image.crop(padded)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    output = Image.new('RGBA', (size, size))
    output.alpha_composite(image, ((size - image.width) // 2, (size - image.height) // 2))
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sheet', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('ids', nargs='+', help='Resource names in row-major order (up to nine)')
    args = parser.parse_args()
    assert 1 <= len(args.ids) <= 9
    args.output.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(args.sheet)
    for index, name in enumerate(args.ids):
        assert name.replace('_', '').isalnum()
        extract(sheet, index).save(args.output / (name+'.png'))
