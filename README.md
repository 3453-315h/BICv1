# BICv1
Batch Image Compression v1

Key Features Comparison

| Feature               | Simple Version  | Advanced Version |
| --------------------- | --------------   | ---------------- |
| **Compression**       | ✅ JPEG quality | ✅ JPEG/PNG/WebP  |
| **Resize (max)**      | ✅              | ✅                |
| **Resize (exact)**    | ❌              | ✅                |
| **Aspect ratio**      | ✅ (always)     | ✅ (toggle)       |
| **Format conversion** | ❌              | ✅ (jpg/png/webp) |
| **Recursive folders** | ❌              | ✅                |
| **Progress stats**    | ✅              | ✅ + detailed     |
| **Error handling**    | ✅              | ✅ + retries      |

Important Notes
1. Backup First: Always test on a copy of your images
2. WebP Support: WebP format requires Pillow with appropriate libraries:
     pip install Pillow
3. PNG Compression: PNG uses compression level 0-9, mapped from quality 1-100
4. Memory: Processing large images may require significant RAM

Usage Examples:
# Install dependency
pip install Pillow

# 1. Compress only (quality 70)
python batch_image_processor.py ./input ./output -q 70

# 2. Resize to max 2048px width/height, keep aspect ratio
python batch_image_processor.py ./input ./output -s 2048

# 3. Convert PNG to JPEG with compression
python batch_image_processor.py ./input ./output -f jpg -q 80

# 4. Resize to exact 800x600 (stretch if needed)
python batch_image_processor.py ./input ./output -e 800 600 --no-aspect

# 5. Process all subdirectories, convert to WebP
python batch_image_processor.py ./input ./output -r -f webp -q 85

