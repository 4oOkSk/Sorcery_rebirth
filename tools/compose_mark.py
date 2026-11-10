#!/usr/bin/env python3
"""Compose a reviewed transparent mark as Sorcery paper.

Input is a foreground alpha mask, with background and old shadows removed.
This tool does not infer which parts of an application icon are its mark.
"""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

SIZE = 384
FACE = 304
MAX_SPAN = 352


def convex_hull(points):
    points = sorted(set(points))

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    lower, upper = [], []
    for chain, sequence in ((lower, points), (upper, reversed(points))):
        for point in sequence:
            while len(chain) >= 2 and cross(chain[-2], chain[-1], point) <= 0:
                chain.pop()
            chain.append(point)
    return lower[:-1] + upper[:-1]


def fit(mask):
    """Balance silhouette area against a 304 px tile; cap freeforms at 352 px."""
    mask = mask.convert('L')
    bounds = mask.point(lambda value: 255 if value >= 128 else 0).getbbox()
    if bounds is None:
        raise ValueError('The mark has no visible foreground')
    mask = mask.crop(bounds)
    width, height = mask.size
    points = []
    for y in range(height):
        row = mask.crop((0, y, width, y + 1)).point(lambda v: 255 if v >= 128 else 0).getbbox()
        if row:
            points.extend(((row[0], y), (row[2], y)))
    hull = convex_hull(points)
    area = abs(sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(hull, hull[1:] + hull[:1]))) / 2
    scale = min(MAX_SPAN / max(width, height), FACE / math.sqrt(max(area, 1)))
    resized = mask.resize((round(width * scale), round(height * scale)), Image.Resampling.LANCZOS)
    result = Image.new('L', (SIZE, SIZE))
    result.paste(resized, ((SIZE - resized.width) // 2, (SIZE - resized.height) // 2))
    return result


def shifted(image, x, y):
    result = Image.new(image.mode, image.size)
    result.paste(image, (x, y))
    return result


def compose(mask, color):
    """Use one silhouette for the paper, thin edge, highlights and shadows."""
    mask = fit(mask)
    result = Image.new('RGBA', (SIZE, SIZE))
    for offset, blur, strength in ((4, 4, .22), (2, 1.1, .19)):
        alpha = shifted(mask, 0, offset).filter(ImageFilter.GaussianBlur(blur))
        layer = Image.new('RGBA', mask.size)
        layer.putalpha(alpha.point(lambda value: round(value * strength)))
        result.alpha_composite(layer)
    edge = Image.new('RGBA', mask.size, tuple(round(c * .65) for c in color) + (255,))
    edge.putalpha(shifted(mask, 0, 3))
    result.alpha_composite(edge)
    face = Image.new('RGBA', mask.size)
    pixels = face.load()
    for y in range(SIZE):
        for x in range(SIZE):
            light = .025 - (x + y - SIZE) / (2 * SIZE) * .035
            if x > y:
                light -= .035
            rgb = tuple(round(c + (255 - c) * light) if light >= 0 else round(c * (1 + light)) for c in color)
            pixels[x, y] = rgb + (255,)
    face.putalpha(mask)
    result.alpha_composite(face)
    highlight = ImageChops.subtract(mask, shifted(mask, 0, 1)).point(lambda value: round(value * .32))
    layer = Image.new('RGBA', mask.size, 'white')
    layer.putalpha(highlight)
    result.alpha_composite(layer)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mask', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--color', required=True, help='Six hexadecimal RGB digits')
    args = parser.parse_args()
    try:
        color = tuple(bytes.fromhex(args.color.removeprefix('#')))
        if len(color) != 3:
            raise ValueError
    except ValueError:
        parser.error('--color must contain six hexadecimal RGB digits')
    source = Image.open(args.mask).convert('RGBA')
    compose(source.getchannel('A'), color).save(args.output)


if __name__ == '__main__':
    main()
