#!/usr/bin/env python3
"""Unify reviewed ordinary tiles without repainting their edge shading."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from normalize_tiles import ROOT, normalize


def standardize(image):
    face = normalize(image).crop((40, 40, 344, 344))
    alpha = face.getchannel('A')
    pixels = alpha.load()
    count = 1440
    boundaries = []
    for index in range(count):
        angle = index * math.tau / count
        dx, dy = math.cos(angle), math.sin(angle)
        low, high = 0., 216.
        for _ in range(12):
            radius = (low + high) / 2
            x, y = round(151.5 + dx * radius), round(151.5 + dy * radius)
            if 0 <= x < 304 and 0 <= y < 304 and pixels[x, y] >= 245:
                low = radius
            else:
                high = radius
        boundaries.append(low)

    def coordinate(x, y):
        dx, dy = x - 152, y - 152
        distance = math.hypot(dx, dy)
        if not distance:
            return x, y
        ux, uy = dx / distance, dy / distance
        edge = 152 / max(abs(ux), abs(uy))
        if min(abs(ux * edge), abs(uy * edge)) > 129:
            dot = 129 * (abs(ux) + abs(uy))
            edge = dot + math.sqrt(max(0, dot * dot - (2 * 129 ** 2 - 23 ** 2)))
        phase = (math.atan2(dy, dx) % math.tau) * count / math.tau
        index = int(phase)
        previous = boundaries[index % count]
        following = boundaries[(index + 1) % count]
        old_edge = previous + (following - previous) * (phase - index)
        shift = old_edge - edge
        if abs(shift) > 35:
            raise ValueError('Contour needs individual review')
        # Leave the interior intact; carry the original rim's colour and shading
        # to its new boundary. The smooth transition has no hard triangle seam.
        weight = max(0, min(1, (distance - edge + 64) / 64))
        weight = weight * weight * (3 - 2 * weight)
        return x + ux * shift * weight, y + uy * shift * weight

    mesh = []
    for y in range(0, 304, 4):
        for x in range(0, 304, 4):
            corners = [coordinate(x, y), coordinate(x, y + 4),
                       coordinate(x + 4, y + 4), coordinate(x + 4, y)]
            mesh.append(((x, y, x + 4, y + 4), tuple(v for point in corners for v in point)))
    rgb = face.convert('RGB').transform((304, 304), Image.Transform.MESH,
                                       mesh, Image.Resampling.BICUBIC)
    outline = Image.new('L', (1216, 1216))
    ImageDraw.Draw(outline).rounded_rectangle((0, 0, 1215, 1215), radius=92, fill=255)
    outline = outline.resize((304, 304), Image.Resampling.LANCZOS)
    rgb.putalpha(outline)
    result = Image.new('RGBA', (384, 384))
    for offset, blur, strength in ((5, 5, .20), (2, 1.5, .19)):
        shadow = Image.new('L', result.size)
        shadow.paste(outline, (40, 40 + offset))
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur)).point(lambda a: round(a * strength))
        layer = Image.new('RGBA', result.size)
        layer.putalpha(shadow)
        result.alpha_composite(layer)
    result.alpha_composite(rgb, (40, 40))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ids', nargs='+', help='Individually reviewed ordinary square tiles')
    parser.add_argument('--output', type=Path, required=True, help='Review directory, outside artwork/icons')
    args = parser.parse_args()
    if args.output.resolve() == (ROOT / 'artwork/icons').resolve():
        parser.error('Review output before applying it to the catalog')
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    for name in dict.fromkeys(args.ids):
        path = ROOT / 'artwork/icons' / (name + '.png')
        with Image.open(path) as image:
            result = standardize(image.convert('RGBA'))
        output = args.output / path.name
        result.save(output)
        results.append({'id': name, 'source_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                        'square_face': [40, 40, 344, 344], 'corner_radius': 23})
    (args.output / 'manifest.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
