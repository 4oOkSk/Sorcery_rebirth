#!/usr/bin/env python3
"""Render a shareable contact sheet from the catalog artwork."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
POPULAR = ['ChatGPT', 'DeepSeek', 'Telegram', 'OpenChamber', 'HTTP Injector', 'AndroMeld',
           'Files', 'Agoda', 'PayPay', 'LocalSend', 'WeChat', 'BiliBili', 'Alipay', 'GitHub',
           'Spotify', 'Discord', 'Signal', 'Firefox', 'Google Maps', 'F-Droid', 'KernelSU']


def font(size):
    for name in ('DejaVuSans.ttf', 'LiberationSans-Regular.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except (OSError, ImportError):
            continue
    try:
        return ImageFont.load_default(size=size)
    except (TypeError, ImportError):
        return ImageFont.load_default()


def render_preview():
    catalog = json.loads((ROOT / 'catalog/icons.json').read_text(encoding='utf-8'))
    icons = [item for label in POPULAR for item in catalog if item['label'] == label]
    chosen = {item['id'] for item in icons}
    icons.extend(item for item in sorted(catalog, key=lambda item: item['label'].casefold()) if item['id'] not in chosen)
    icons = icons[:96]
    columns = 12
    rows = (len(icons) + columns - 1) // columns
    image = Image.new('RGB', (1440, 178 + rows * 120), '#f4f0e8')
    draw = ImageDraw.Draw(image)
    draw.text((40, 28), 'Sorcery_rebirth', fill='#26352f', font=font(48))
    draw.text((42, 100), f'{len(catalog)} Rebirth icons · Recognizable app marks, Sorcery paper style', fill='#597062', font=font(20))
    for index, item in enumerate(icons):
        directory = 'artwork/icons' if item.get('format') == 'png' else 'build/res/drawable-nodpi'
        with Image.open(ROOT / directory / f"{item['id']}.png") as source:
            icon = source.convert('RGBA').resize((112, 112), Image.Resampling.LANCZOS)
        image.paste(icon, (index % columns * 120 + 4, index // columns * 120 + 156), icon)
    return image


if __name__ == '__main__':
    image = render_preview()
    image.save(ROOT / 'docs/preview.png', optimize=True)
    print('Preview:', image.size)
