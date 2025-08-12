#!/usr/bin/env python3
import os
import json
from PIL import Image
from PIL.ExifTags import TAGS

gallery_dir = os.path.dirname(__file__)
image_files = [f for f in os.listdir(gallery_dir) if f.lower().endswith('.jpg')]

images = []
for fname in sorted(image_files):
    path = os.path.join(gallery_dir, fname)
    try:
        img = Image.open(path)
        exif = img.getexif()
        caption = ''
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag in ('ImageDescription', 'UserComment', 'XPComment', 'XPTitle', 'XPSubject'):
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-16' if tag.startswith('XP') else 'utf-8', errors='ignore')
                    except Exception:
                        value = value.decode(errors='ignore')
                caption = str(value).strip()
                if caption:
                    break
        width, height = img.size
        images.append({
            'src': fname,
            'w': width,
            'h': height,
            'caption': caption
        })
    except Exception as e:
        images.append({
            'src': fname,
            'w': 1600,
            'h': 1067,
            'caption': ''
        })

with open('images.json', 'w', encoding='utf-8') as f:
    json.dump(images, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(images)} images with captions to images.json")
