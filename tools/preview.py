#!/usr/bin/env python3
"""Render a shareable contact sheet from the PNGs produced by the build."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'catalog/icons.json').read_text())
popular = ['ChatGPT', 'DeepSeek', 'Telegram', 'OpenChamber', 'HTTP Injector', 'AndroMeld',
           'Files', 'Agoda', 'PayPay', 'LocalSend', 'WeChat', 'BiliBili', 'Alipay', 'GitHub',
           'Spotify', 'Discord', 'Signal', 'Firefox', 'Google Maps', 'F-Droid', 'KernelSU']
icons = [x for label in popular for x in catalog if x['label'] == label]
chosen = {x['id'] for x in icons}
icons.extend(x for x in sorted(catalog, key=lambda x: x['label'].casefold()) if x['id'] not in chosen)
icons = icons[:96]
columns = 12
rows = (len(icons) + columns - 1) // columns
image = Image.new('RGB', (1440, 178 + rows * 120), '#f4f0e8')
draw = ImageDraw.Draw(image)
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title = ImageFont.truetype(font_path, 48)
small = ImageFont.truetype(font_path, 20)
draw.text((40, 28), 'Sorcery_rebirth', fill='#26352f', font=title)
draw.text((42, 100), f'{len(catalog)} Rebirth icons · Recognizable app marks, Sorcery paper style', fill='#597062', font=small)
for index, item in enumerate(icons):
    icon = Image.open(ROOT / 'build/res/drawable-nodpi' / (item['id'] + '.png')).convert('RGBA')
    icon = icon.resize((112, 112), Image.Resampling.LANCZOS)
    image.paste(icon, (index % columns * 120 + 4, index // columns * 120 + 156), icon)
image.save(ROOT / 'docs/preview.png', optimize=True)
print('Preview:', image.size)
