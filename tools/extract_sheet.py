#!/usr/bin/env python3
"""Extract transparent artwork from a 3×3 sheet and match Sorcery optical sizes."""
import argparse
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter


def extract(sheet, index, size=384):
    row, column = divmod(index, 3)
    image = sheet.crop((round(column*sheet.width/3), round(row*sheet.height/3),
                        round((column+1)*sheet.width/3), round((row+1)*sheet.height/3))).convert('RGBA')
    # Preserve disconnected logo elements while excluding tiny isolated specks.
    mask = image.getchannel('A').resize((128, 128)).point(lambda x: 255 if x >= 100 else 0)
    pixels = bytearray(mask.tobytes())
    components = []
    for start in range(len(pixels)):
        if not pixels[start]:
            continue
        queue, component = [start], []
        pixels[start] = 0
        while queue:
            index = queue.pop()
            component.append(index)
            x, y = index % 128, index // 128
            neighbors = ([index-1] if x else []) + ([index+1] if x < 127 else [])
            neighbors += ([index-128] if y else []) + ([index+128] if y < 127 else [])
            for neighbor in neighbors:
                if pixels[neighbor]:
                    pixels[neighbor] = 0
                    queue.append(neighbor)
        components.append(component)
    assert components, 'Empty cell'
    largest = max(map(len, components))
    clean = bytearray(128*128)
    for component in components:
        if len(component) >= max(6, largest*.006):
            for index in component:
                clean[index] = 255
    mask = Image.frombytes('L', (128, 128), bytes(clean)).filter(ImageFilter.MaxFilter(5)).resize(image.size)
    image.putalpha(ImageChops.multiply(image.getchannel('A'), mask))
    solid = image.getchannel('A').point(lambda x: 255 if x >= 230 else 0)
    bounds = solid.getbbox()
    assert bounds, 'No opaque artwork'
    width, height = bounds[2]-bounds[0], bounds[3]-bounds[1]
    assert min(width, height) > image.width*.2, 'Artwork too small'
    filled = sum(solid.histogram()[1:]) / (width*height)
    # Match original Sorcery optical weight across squares (304 px), folded/hex
    # badges (~320-336 px), and discs/freeform objects (up to 348 px).
    solid_area = sum(solid.histogram()[1:])
    target_side = (152.5 if filled > .84 else 155.0) * size / 192
    max_span = (152 if filled > .94 and .93 <= width / height <= 1.07 else 174) * size / 192
    scale = min(max_span / max(width, height), target_side / (solid_area ** .5))
    padding = max(8, round(image.width*.025))
    padded = (max(0, bounds[0]-padding), max(0, bounds[1]-padding),
              min(image.width, bounds[2]+padding), min(image.height, bounds[3]+padding))
    image = image.crop(padded)
    image = image.resize((round(image.width*scale), round(image.height*scale)), Image.Resampling.LANCZOS)
    output = Image.new('RGBA', (size, size))
    output.alpha_composite(image, ((size-image.width)//2, (size-image.height)//2))
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
