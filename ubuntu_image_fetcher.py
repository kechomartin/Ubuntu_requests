import requests
import os
import hashlib
import json
import mimetypes
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime

class UbuntuImageFetcher:
    def __init__(self):
        self.download_dir = "Fetched_Images"
        self.metadata_file = os.path.join(self.download_dir, "download_metadata.json")
        self.downloaded_hashes = self.load_download_history()
        
        # Security settings
        self.max_file_size = 50 * 1024 * 1024  # 50 MB limit
        self.allowed_content_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
            'image/bmp', 'image/webp', 'image/svg+xml', 'image/tiff'
        }
        
    def main(self):
        print("Welcome to the Ubuntu Image Fetcher")
        print("A tool for mindfully collecting images from the web")
        print("Built with community spirit and security in mind\n")
        
        mode = self.get_mode_choice()
        
        if mode == '1':
            self.single_url_mode()
        elif mode == '2':
            self.multiple_urls_mode()
        else:
            print("Invalid choice. Exiting gracefully.")
            
    def get_mode_choice(self):
        print("Choose your approach:")
        print("1. Download single image")
        print("2. Download multiple images")
        choice = input("\nEnter your choice (1 or 2): ").strip()
        return choice
        
    def single_url_mode(self):
        url = input("\nPlease enter the image URL: ").strip()
        if url:
            self.download_image(url)
            
    def multiple_urls_mode(self):
        print("\nEnter URLs one by one (press Enter with empty line to finish):")
        urls = []
        
        while True:
            url = input(f"URL {len(urls) + 1}: ").strip()
            if not url:
                break
            urls.append(url)
            
        if not urls:
            print("No URLs provided. Community awaits your return.")
            return
            
        print(f"\nProcessing {len(urls)} URLs with Ubuntu spirit...")
        successful = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            if self.download_image(url, batch_mode=True):
                successful += 1
                
        print(f"\n✓ Successfully downloaded {successful}/{len(urls)} images")
        print("Community enriched through collective effort.")
        
    def download_image(self, url, batch_mode=False):
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.download_dir, exist_ok=True)
            
            # Security check: Validate URL format
            if not self.is_valid_url(url):
                print("✗ Invalid URL format")
                return False
                
            # Prepare secure request headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Ubuntu; Linux x86_64) AppleWebKit/537.36',
                'Accept': 'image/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'DNT': '1',  # Do Not Track
                'Connection': 'close'  # Security best practice
            }
            
            # First, make a HEAD request to check headers without downloading
            try:
                head_response = requests.head(url, timeout=10, headers=headers, allow_redirects=True)
                if not self.validate_response_headers(head_response):
                    return False
            except requests.exceptions.RequestException:
                # If HEAD fails, we'll check during GET request
                pass
            
            # Make the actual request with security measures
            response = requests.get(
                url, 
                timeout=30, 
                headers=headers, 
                stream=True,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Security validation
            if not self.validate_response_headers(response):
                return False
                
            # Check for duplicate based on content hash
            content_hash = self.calculate_content_hash(response)
            if self.is_duplicate(content_hash, url):
                print("⚠ Duplicate image detected - skipping download")
                return False
            
            # Extract and validate filename
            filename = self.extract_filename(url, response)
            filepath = self.get_unique_filepath(filename)
            
            # Download with progress tracking for large files
            file_size = int(response.headers.get('Content-Length', 0))
            
            if file_size > self.max_file_size:
                print(f"✗ File too large ({self.format_file_size(file_size)}). Max allowed: {self.format_file_size(self.max_file_size)}")
                return False
            
            downloaded_size = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Safety check during download
                        if downloaded_size > self.max_file_size:
                            f.close()
                            os.remove(filepath)
                            print("✗ File exceeded size limit during download")
                            return False
            
            # Verify downloaded file
            actual_size = os.path.getsize(filepath)
            if actual_size == 0:
                os.remove(filepath)
                print("✗ Downloaded file was empty")
                return False
            
            # Save metadata for duplicate detection
            self.save_download_metadata(content_hash, url, filepath, actual_size)
            
            # Success message
            if not batch_mode:
                print(f"✓ Successfully fetched: {os.path.basename(filepath)}")
                print(f"✓ Image saved to {filepath}")
                print(f"✓ File size: {self.format_file_size(actual_size)}")
                print("\nConnection strengthened. Community enriched.")
            else:
                print(f"  ✓ Downloaded: {os.path.basename(filepath)} ({self.format_file_size(actual_size)})")
                
            return True
            
        except requests.exceptions.Timeout:
            print("✗ Connection timeout: Server response too slow")
        except requests.exceptions.ConnectionError:
            print("✗ Connection error: Unable to reach server")
        except requests.exceptions.HTTPError as e:
            print(f"✗ HTTP error: {e}")
        except requests.exceptions.TooManyRedirects:
            print("✗ Too many redirects: Potential security risk")
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error: {e}")
        except IOError as e:
            print(f"✗ File error: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            
        return False
    
    def is_valid_url(self, url):
        """Validate URL format and security"""
        try:
            parsed = urlparse(url)
            # Only allow HTTP/HTTPS
            if parsed.scheme not in ('http', 'https'):
                print("✗ Only HTTP/HTTPS URLs are allowed")
                return False
            # Prevent local file access
            if parsed.hostname in ('localhost', '127.0.0.1', '0.0.0.0'):
                print("✗ Local URLs are not allowed for security reasons")
                return False
            return True
        except Exception:
            return False
    
    def validate_response_headers(self, response):
        """Check important HTTP headers for security and content validation"""
        # Check Content-Type
        content_type = response.headers.get('Content-Type', '').lower().split(';')[0]
        
        if content_type and content_type not in self.allowed_content_types:
            print(f"✗ Content type '{content_type}' not allowed")
            return False
            
        # Check Content-Length for size validation
        content_length = response.headers.get('Content-Length')
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_file_size:
                    print(f"✗ File too large: {self.format_file_size(size)}")
                    return False
            except ValueError:
                pass
                
        # Security headers check (informational)
        security_headers = ['X-Content-Type-Options', 'X-Frame-Options', 'Content-Security-Policy']
        missing_headers = [h for h in security_headers if h not in response.headers]
        
        if missing_headers and not content_type.startswith('image/'):
            print(f"⚠ Warning: Some security headers missing: {', '.join(missing_headers)}")
            
        return True
    
    def calculate_content_hash(self, response):
        """Calculate SHA-256 hash of content for duplicate detection"""
        hasher = hashlib.sha256()
        
        # Reset stream position if possible
        if hasattr(response, 'content'):
            hasher.update(response.content)
        else:
            # Stream hash calculation
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    hasher.update(chunk)
                    
        return hasher.hexdigest()
    
    def is_duplicate(self, content_hash, url):
        """Check if image was already downloaded"""
        for record in self.downloaded_hashes:
            if record['hash'] == content_hash:
                return True
        return False
    
    def extract_filename(self, url, response):
        """Extract filename from URL or Content-Disposition header"""
        # Try Content-Disposition header first
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            try:
                filename = content_disposition.split('filename=')[1].strip('"\'')
                if filename and self.is_safe_filename(filename):
                    return filename
            except IndexError:
                pass
        
        # Extract from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # If no filename or extension, generate one
        if not filename or '.' not in filename:
            content_type = response.headers.get('Content-Type', '').lower().split(';')[0]
            extension = self.get_extension_from_content_type(content_type)
            filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"
            
        return filename if self.is_safe_filename(filename) else f"safe_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    
    def is_safe_filename(self, filename):
        """Check if filename is safe (no path traversal, special chars)"""
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return not any(char in filename for char in dangerous_chars) and len(filename) < 255
    
    def get_extension_from_content_type(self, content_type):
        """Get file extension from Content-Type"""
        extensions = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png', 
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'image/tiff': '.tiff'
        }
        return extensions.get(content_type, '.jpg')
    
    def get_unique_filepath(self, filename):
        """Generate unique filepath to prevent overwrites"""
        filepath = os.path.join(self.download_dir, filename)
        
        if not os.path.exists(filepath):
            return filepath
            
        name, ext = os.path.splitext(filename)
        counter = 1
        
        while os.path.exists(filepath):
            new_filename = f"{name}_{counter}{ext}"
            filepath = os.path.join(self.download_dir, new_filename)
            counter += 1
            
        return filepath
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"
    
    def load_download_history(self):
        """Load previous download metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []
    
    def save_download_metadata(self, content_hash, url, filepath, file_size):
        """Save download metadata for duplicate detection"""
        metadata = {
            'hash': content_hash,
            'url': url,
            'filepath': filepath,
            'file_size': file_size,
            'download_date': datetime.now().isoformat()
        }
        
        self.downloaded_hashes.append(metadata)
        
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.downloaded_hashes, f, indent=2)
        except IOError as e:
            print(f"⚠ Warning: Could not save metadata: {e}")

def main():
    fetcher = UbuntuImageFetcher()
    fetcher.main()

if __name__ == "__main__":
    main()