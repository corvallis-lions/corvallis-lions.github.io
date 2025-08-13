#!/usr/bin/env python3
import os
import json
from PIL import Image
from PIL.ExifTags import TAGS

gallery_dir = os.path.dirname(__file__)
image_files = [f for f in os.listdir(gallery_dir) if f.lower().endswith('.jpg') or f.lower().endswith('.mp4')]

images = []
for fname in sorted(image_files):
    path = os.path.join(gallery_dir, fname)
    if fname.lower().endswith('.jpg'):
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
                'caption': caption.replace('_', ' ')
            })
        except Exception as e:
            images.append({
                'src': fname,
                'w': 1600,
                'h': 1067,
                'caption': ''
            })
    elif fname.lower().endswith('.mp4'):
        # Try to get video metadata (width/height) using ffprobe if available
        width = 0
        height = 0
        caption = ''
        try:
            import subprocess
            import shlex
            # Get width and height using ffprobe
            cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json {shlex.quote(path)}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                import json as _json
                info = _json.loads(result.stdout)
                streams = info.get('streams', [])
                if streams:
                    width = streams[0].get('width', 0)
                    height = streams[0].get('height', 0)
            # Attempt to extract a title/description (not common in mp4)
            cmd_caption = f"ffprobe -v error -show_entries format_tags=title,comment -of default=noprint_wrappers=1:nokey=1 {shlex.quote(path)}"
            result_caption = subprocess.run(cmd_caption, shell=True, capture_output=True, text=True)
            if result_caption.returncode == 0:
                lines = [line.strip() for line in result_caption.stdout.splitlines() if line.strip()]
                if lines:
                    caption = lines[0]
        except Exception:
            pass
        images.append({
            'src': fname,
            'w': width,
            'h': height,
            'caption': caption.replace('_', ' ')
        })

with open('images.json', 'w', encoding='utf-8') as f:
    json.dump(images, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(images)} images with captions to images.json")
