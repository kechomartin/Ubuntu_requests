import requests
import os
import hashlib
from urllib.parse import urlparse
from pathlib import Path

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    
    # Get URL from user
    url = input("Please enter the image URL: ")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs("Fetched_Images", exist_ok=True)
        
        # Fetch the image with appropriate headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, timeout=10, headers=headers, stream=True)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Check Content-Type to ensure it's an image
        content_type = response.headers.get('Content-Type', '').lower()
        if not content_type.startswith('image/'):
            print(f"⚠ Warning: Content type '{content_type}' may not be an image")
            proceed = input("Continue anyway? (y/N): ").lower()
            if proceed != 'y':
                print("Download cancelled.")
                return
        
        # Extract filename from URL or generate one
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # If no filename or extension, try to determine from Content-Type
        if not filename or '.' not in filename:
            extension = get_extension_from_content_type(content_type)
            filename = f"downloaded_image{extension}"
        
        # Ensure unique filename to prevent overwriting
        filepath = get_unique_filepath("Fetched_Images", filename)
        
        # Save the image in chunks to handle large files efficiently
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verify the downloaded file
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            os.remove(filepath)
            print("✗ Downloaded file was empty")
            return
            
        print(f"✓ Successfully fetched: {os.path.basename(filepath)}")
        print(f"✓ Image saved to {filepath}")
        print(f"✓ File size: {format_file_size(file_size)}")
        print("\nConnection strengthened. Community enriched.")
        
    except requests.exceptions.Timeout:
        print("✗ Connection timeout: The server took too long to respond")
    except requests.exceptions.ConnectionError:
        print("✗ Connection error: Unable to reach the server")
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
    except IOError as e:
        print(f"✗ File error: Unable to save image - {e}")
    except Exception as e:
        print(f"✗ An unexpected error occurred: {e}")

def get_extension_from_content_type(content_type):
    """Extract file extension from Content-Type header"""
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

def get_unique_filepath(directory, filename):
    """Generate a unique filepath to avoid overwriting existing files"""
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        return filepath
    
    # If file exists, add a number suffix
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while os.path.exists(filepath):
        new_filename = f"{name}_{counter}{ext}"
        filepath = os.path.join(directory, new_filename)
        counter += 1
    
    return filepath

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"

if __name__ == "__main__":
    main()