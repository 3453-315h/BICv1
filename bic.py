#!/usr/bin/env python3
import os
from pathlib import Path
from PIL import Image
import argparse
from collections import defaultdict

# Supported formats
SUPPORTED_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}

class ImageBatchProcessor:
    def __init__(self, input_dir, output_dir, quality=85, max_dimension=None, 
                 exact_size=None, maintain_aspect=True, convert_to=None, recursive=False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.max_dimension = max_dimension
        self.exact_size = exact_size
        self.maintain_aspect = maintain_aspect
        self.convert_to = convert_to.lower() if convert_to else None
        self.recursive = recursive
        self.stats = defaultdict(int)
        
    def _resize_image(self, img):
        """Resize image based on parameters"""
        if self.exact_size:
            if self.maintain_aspect:
                img.thumbnail(self.exact_size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(self.exact_size, Image.Resampling.LANCZOS)
        elif self.max_dimension:
            img.thumbnail((self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS)
        return img

    def _get_output_format(self, input_path):
        """Determine output format"""
        if self.convert_to:
            return self.convert_to
        return input_path.suffix.lower().lstrip('.')

    def _needs_conversion(self, img, output_path):
        """Check if image needs mode conversion"""
        is_jpeg = output_path.suffix.lower() in ('.jpg', '.jpeg')
        has_alpha = img.mode in ('RGBA', 'P', 'LA')
        return is_jpeg and has_alpha

    def process_image(self, img_path):
        """Process a single image"""
        try:
            with Image.open(img_path) as img:
                # Ensure image is in correct mode
                original_mode = img.mode
                
                # Resize
                img = self._resize_image(img)
                
                # Determine output path and format
                rel_path = img_path.relative_to(self.input_dir)
                output_path = self.output_dir / rel_path
                output_path = output_path.with_suffix(f".{self._get_output_format(img_path)}")
                
                # Create output directory
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert mode if necessary
                if self._needs_conversion(img, output_path):
                    img = img.convert('RGB')
                
                # Save parameters
                save_kwargs = {'optimize': True}
                
                # Format-specific settings
                if output_path.suffix.lower() in ('.jpg', '.jpeg'):
                    save_kwargs['quality'] = self.quality
                elif output_path.suffix.lower() == '.png':
                    save_kwargs['compress_level'] = 9 - (self.quality // 10)  # 0-9 compression
                
                # Save image
                img.save(output_path, **save_kwargs)
                
                # Update stats
                self.stats['processed'] += 1
                original_size = img_path.stat().st_size
                new_size = output_path.stat().st_size
                saved = (1 - new_size / original_size) * 100
                
                print(f"✓ {rel_path} | {original_size//1024}KB → {new_size//1024}KB ({saved:.1f}% saved)")
                return True
                
        except Exception as e:
            self.stats['failed'] += 1
            print(f"✗ Failed: {img_path} - {e}")
            return False

    def find_images(self):
        """Find all images in input directory"""
        if self.recursive:
            return list(self.input_dir.rglob('*.*'))
        else:
            return list(self.input_dir.glob('*.*'))

    def run(self):
        """Main processing loop"""
        print(f"🔍 Scanning for images in: {self.input_dir}")
        
        image_files = [
            f for f in self.find_images() 
            if f.suffix.lower() in SUPPORTED_EXTS and f.is_file()
        ]
        
        if not image_files:
            print("No supported images found!")
            return
        
        print(f"📸 Found {len(image_files)} images to process")
        
        # Process each image
        for img_path in image_files:
            self.process_image(img_path)
        
        # Print summary
        print("\n" + "="*50)
        print("🚀 BIC - Batch Image Compression v1.0")
        print("\n" + "="*50)
        print("📊 PROCESSING COMPLETE")
        print(f"✓ Successfully processed: {self.stats['processed']}")
        print(f"✗ Failed: {self.stats['failed']}")
        print(f"📁 Output directory: {self.output_dir}")
        print("-" * 50 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="Advanced batch image processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compress JPEGs to quality 75
  python batch_image_processor.py ./photos ./output -q 75

  # Resize to max 1920px, convert to WebP
  python batch_image_processor.py ./photos ./output -s 1920 -f webp

  # Resize to exact 800x600, no aspect ratio preservation
  python batch_image_processor.py ./photos ./output -e 800 600 --no-aspect

  # Process recursively with 85% quality
  python batch_image_processor.py ./photos ./output -r -q 85
        """
    )
    
    parser.add_argument("input_dir", help="Input directory containing images")
    parser.add_argument("output_dir", help="Output directory for processed images")
    
    parser.add_argument("-q", "--quality", type=int, default=85,
                       help="Quality: 1-100 (JPEG/WebP) or compression level indicator (PNG)")
    
    size_group = parser.add_mutually_exclusive_group()
    size_group.add_argument("-s", "--max-size", type=int,
                           help="Maximum dimension (maintains aspect ratio)")
    size_group.add_argument("-e", "--exact-size", nargs=2, type=int, metavar=('W', 'H'),
                           help="Exact width and height in pixels")
    
    parser.add_argument("--no-aspect", action="store_false", dest="maintain_aspect",
                       help="Don't maintain aspect ratio (use with -e)")
    parser.add_argument("-f", "--format", choices=['jpg', 'png', 'webp'],
                       help="Convert to specific format")
    parser.add_argument("-r", "--recursive", action="store_true",
                       help="Process subdirectories recursively")
    
    args = parser.parse_args()
    
    processor = ImageBatchProcessor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        quality=args.quality,
        max_dimension=args.max_size,
        exact_size=tuple(args.exact_size) if args.exact_size else None,
        maintain_aspect=args.maintain_aspect,
        convert_to=args.format,
        recursive=args.recursive
    )
    
    processor.run()

if __name__ == "__main__":
    main()