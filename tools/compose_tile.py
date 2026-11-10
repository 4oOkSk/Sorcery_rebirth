#!/usr/bin/env python3
"""Compose a reviewed, unmasked paper face with a shadow following its contour.

Input is the original face, including its alpha, edge shading, mark and internal
shadows. Do not pass an icon with flattened corners or an existing outer shadow.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


def compose(material, background=None):
    material = material.convert('RGBA').resize((304, 304), Image.Resampling.LANCZOS)
    if background is not None:
        paper = Image.new('RGBA', material.size, tuple(background) + (255,))
        paper.alpha_composite(material)
        material = paper
    # Generated opaque faces can have alpha 252/253. Separate their contour
    # from faint sheet shadows; keep the RGB edge shading and all interior RGB.
    alpha = material.getchannel('A').point(
        lambda a: round(max(0, min(1, (a - 128) / 120)) * 255))
    limit = Image.new('L', (1216, 1216))
    ImageDraw.Draw(limit).rounded_rectangle((0, 0, 1215, 1215), radius=64, fill=255)
    # A minimum paper radius trims only sharp source corners. Larger native
    # corners and disconnected paper layers retain their existing silhouette.
    alpha = ImageChops.multiply(alpha, limit.resize((304, 304), Image.Resampling.LANCZOS))
    material.putalpha(alpha)
    result = Image.new('RGBA', (384, 384))
    for offset, blur, strength in ((5, 5, .20), (2, 1.5, .19)):
        shadow_alpha = Image.new('L', result.size)
        shadow_alpha.paste(alpha, (40, 40 + offset))
        shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(blur)).point(
            lambda a: round(a * strength))
        layer = Image.new('RGBA', result.size)
        layer.putalpha(shadow_alpha)
        result.alpha_composite(layer)
    result.alpha_composite(material, (40, 40))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('material', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--background', nargs=3, type=int, metavar=('R', 'G', 'B'))
    args = parser.parse_args()
    if args.background and not all(0 <= value <= 255 for value in args.background):
        parser.error('Background components must be between 0 and 255')
    with Image.open(args.material) as image:
        compose(image, args.background).save(args.output)


if __name__ == '__main__':
    main()
