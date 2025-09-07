# Ubuntu Image Fetcher

A Python script inspired by Ubuntu's community principles for mindfully collecting images from the web with security and efficiency in mind.

## Features

- **Single & Batch Downloads**: Download individual images or multiple URLs at once
- **Security First**: Built-in protections against malicious content and unsafe URLs
- **Duplicate Prevention**: SHA-256 content hashing prevents downloading the same image twice
- **Smart Filename Handling**: Extracts filenames from URLs or Content-Disposition headers
- **Error Handling**: Graceful handling of network issues, timeouts, and invalid content
- **Progress Tracking**: Real-time feedback during downloads
- **Ubuntu Spirit**: Community-focused messaging and mindful resource usage

## Requirements

- Python 3.6 or higher
- Internet connection
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd ubuntu-image-fetcher
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Version
```bash
python ubuntu_image_fetcher_basic.py
```

### Enhanced Version (Recommended)
```bash
python ubuntu_image_fetcher.py
```

### Example Session
```
Welcome to the Ubuntu Image Fetcher
A tool for mindfully collecting images from the web
Built with community spirit and security in mind

Choose your approach:
1. Download single image
2. Download multiple images

Enter your choice (1 or 2): 1

Please enter the image URL: https://example.com/image.jpg
✓ Successfully fetched: image.jpg
✓ Image saved to Fetched_Images/image.jpg
✓ File size: 156.3 KB

Connection strengthened. Community enriched.
```

## Security Features

- **URL Validation**: Only allows HTTP/HTTPS URLs, blocks localhost access
- **Content-Type Checking**: Validates that downloaded content is actually an image
- **File Size Limits**: Prevents downloading files larger than 50MB
- **Safe Filenames**: Prevents path traversal attacks and sanitizes filenames
- **Request Headers**: Uses appropriate headers for better compatibility and security

## Project Structure

```
ubuntu-image-fetcher/
├── ubuntu_image_fetcher.py          # Enhanced version with all features
├── ubuntu_image_fetcher_basic.py    # Basic implementation
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
└── Fetched_Images/                 # Created automatically (ignored by git)
    ├── download_metadata.json      # Metadata for duplicate detection
    └── [downloaded images]         # Your fetched images
```

## Technical Details

### Dependencies
- `requests`: For HTTP requests and downloads
- `hashlib`: For SHA-256 content hashing (built-in)
- `json`: For metadata storage (built-in)
- `os`, `pathlib`: For file system operations (built-in)
- `urllib.parse`: For URL parsing (built-in)

### Error Handling
The application handles various error scenarios:
- Network timeouts and connection errors
- HTTP errors (404, 403, etc.)
- Invalid URLs or content types
- File system errors
- Malformed responses

### Duplicate Detection
Uses SHA-256 content hashing to identify duplicate images regardless of filename or URL differences. Metadata is stored in `Fetched_Images/download_metadata.json`.

## Contributing

This project follows Ubuntu's community principles:
- **Humanity**: Treat all users and contributors with respect
- **Ubuntu**: "I am what I am because of who we all are" - collaborative development
- **Free Software**: Open source and transparent development

Feel free to submit issues, feature requests, or pull requests!

## License

This project is open source and available under the [MIT License](LICENSE).

## Assignment Context

This project was created as part of an Ubuntu-inspired programming assignment focusing on:
- Proper use of the `requests` library
- Effective error handling for network operations
- File management and directory creation
- Clean, readable code with clear documentation
- Security-conscious programming practices

---

*Built with Ubuntu spirit - Connection strengthened. Community enriched.*