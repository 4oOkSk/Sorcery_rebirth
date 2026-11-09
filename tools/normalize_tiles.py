#!/usr/bin/env python3
"""Normalize explicitly reviewed square paper tiles and update their source hashes."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import median

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FACE = (40, 40, 344, 344)


def measure_face(image):
    """Measure straight edges through the central fifth, excluding corner shadows."""
    if image.size != (384, 384):
        raise ValueError('Expected a 384 px source')
    alpha = image.convert('RGBA').getchannel('A')
    rows, columns = [], []
    for position in range(154, 230):
        row = alpha.crop((0, position, 384, position + 1)).point(lambda a: 255 if a >= 230 else 0).getbbox()
        column = alpha.crop((position, 0, position + 1, 384)).point(lambda a: 255 if a >= 230 else 0).getbbox()
        if row:
            rows.append((row[0], row[2]))
        if column:
            columns.append((column[1], column[3]))
    if len(rows) != 76 or len(columns) != 76:
        raise ValueError('No solid square paper face')
    return tuple(median(values) for values in (
        [r[0] for r in rows], [c[0] for c in columns],
        [r[1] for r in rows], [c[1] for c in columns]))


def normalize(image):
    image = image.convert('RGBA')
    left, top, right, bottom = measure_face(image)
    width, height = right - left, bottom - top
    if not all(270 <= side <= 320 for side in (width, height)):
        raise ValueError('Face requires individual artwork review')
    if max(abs(a - b) for a, b in zip((left, top, right, bottom), FACE)) <= 1:
        return image
    sx, sy = width / 304, height / 304
    # Transform the full source, including its shadow, in premultiplied alpha.
    # Small independent axis corrections make a generated rectangle square.
    result = image.convert('RGBa').transform(
        image.size, Image.Transform.AFFINE,
        (sx, 0, left - 40 * sx, 0, sy, top - 40 * sy),
        Image.Resampling.BICUBIC).convert('RGBA')
    alpha = result.getchannel('A')
    for edge in ((0, 0, 384, 1), (0, 383, 384, 384),
                 (0, 0, 1, 384), (383, 0, 384, 384)):
        if alpha.crop(edge).getextrema()[1] > 1:
            raise ValueError('Transform clips the outer shadow')
    if max(abs(a - b) for a, b in zip(measure_face(result), FACE)) > 1:
        raise ValueError('Face did not reach the standard bounds')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ids', nargs='+', help='Reviewed ordinary square tiles; exclude intentional shapes')
    parser.add_argument('--write', action='store_true', help='Write PNGs and catalog hashes after validation')
    args = parser.parse_args()
    catalog_path = ROOT / 'catalog/icons.json'
    catalog = json.loads(catalog_path.read_text())
    entries = {item['id']: item for item in catalog}
    prepared = []
    for name in dict.fromkeys(args.ids):
        entry = entries[name]
        if entry['format'] != 'png':
            raise ValueError(f'{name}: expected PNG artwork')
        path = ROOT / 'artwork/icons' / (name + '.png')
        with Image.open(path) as image:
            before = measure_face(image)
            result = normalize(image)
        prepared.append((entry, path, result))
        print(f'{name}: {before} -> {measure_face(result)}')
    if args.write:
        for entry, path, result in prepared:
            result.save(path)
            entry['generation']['source_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            entry['generation']['square_face'] = list(FACE)
        catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
