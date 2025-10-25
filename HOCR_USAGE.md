# HOCR Plugin Usage Guide

This guide explains how to use the HOCR (HTML-based OCR) output format with the PaddleOCR-VL API.

## What is HOCR?

HOCR is an open standard for representing OCR results in HTML format. It preserves:
- Text content
- Layout structure (pages, paragraphs, lines, words)
- Bounding box coordinates for each element
- Metadata about the OCR process

## Usage

To get OCR results in HOCR format, add the `response_format` parameter to your API request:

### Example 1: Using response_format as a string

```bash
curl -X POST http://localhost:7777/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "paddleocr-vl",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Extract all text from this image"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://example.com/document.jpg"
            }
          }
        ]
      }
    ],
    "response_format": "hocr"
  }'
```

### Example 2: Using response_format as an object

```bash
curl -X POST http://localhost:7777/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "paddleocr-vl",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Parse this document"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/png;base64,iVBORw0KG..."
            }
          }
        ]
      }
    ],
    "response_format": {
      "type": "hocr"
    }
  }'
```

### Python Example

```python
import requests
import base64

# Read and encode image
with open("document.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# Make API request
response = requests.post(
    "http://localhost:7777/v1/chat/completions",
    json={
        "model": "paddleocr-vl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract text from this image"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        "response_format": "hocr"
    }
)

# Save HOCR output
with open("output.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("HOCR output saved to output.html")
```

### JavaScript/Node.js Example

```javascript
const fs = require('fs');
const axios = require('axios');

async function convertToHOCR(imagePath) {
    // Read and encode image
    const imageBuffer = fs.readFileSync(imagePath);
    const base64Image = imageBuffer.toString('base64');

    // Make API request
    const response = await axios.post('http://localhost:7777/v1/chat/completions', {
        model: 'paddleocr-vl',
        messages: [
            {
                role: 'user',
                content: [
                    {
                        type: 'text',
                        text: 'Extract all text from this image'
                    },
                    {
                        type: 'image_url',
                        image_url: {
                            url: `data:image/jpeg;base64,${base64Image}`
                        }
                    }
                ]
            }
        ],
        response_format: 'hocr'
    });

    // Save HOCR output
    fs.writeFileSync('output.html', response.data);
    console.log('HOCR output saved to output.html');
}

convertToHOCR('document.jpg');
```

## HOCR Output Structure

The HOCR output follows this hierarchical structure:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta name="ocr-system" content="PaddleOCR-VL" />
  </head>
  <body>
    <div class="ocr_page" id="page_1" title="bbox 0 0 800 600">
      <div class="ocr_carea" id="carea_1_1" title="bbox 10 10 790 590">
        <p class="ocr_par" id="par_1_1" title="bbox 20 20 780 50">
          <span class="ocr_line" id="line_1_1" title="bbox 30 20 500 50">
            <span class="ocrx_word" id="word_1_1" title="bbox 30 20 80 50">Hello</span>
            <span class="ocrx_word" id="word_1_2" title="bbox 90 20 140 50">World</span>
          </span>
        </p>
      </div>
    </div>
  </body>
</html>
```

### HOCR Elements

- **ocr_page**: Represents the entire page
- **ocr_carea**: Text area or column
- **ocr_par**: Paragraph
- **ocr_line**: Line of text
- **ocrx_word**: Individual word

Each element includes a `title` attribute with:
- **bbox**: Bounding box coordinates (x0 y0 x1 y1)

## Default Behavior

If you don't specify `response_format`, the API returns plain text in JSON format:

```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "paddleocr-vl-0.9b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Extracted text content here..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  }
}
```

## Notes

- **Coordinate Estimation**: PaddleOCR-VL generates text without explicit coordinate information. The HOCR plugin estimates bounding boxes based on text flow and typical character dimensions.
- **Streaming**: HOCR format is currently not supported with streaming responses. Use `"stream": false` (default).
- **Content Type**: HOCR responses are returned as `text/html; charset=utf-8`.

## Use Cases

HOCR format is useful for:
- Preserving document layout structure
- Integration with document processing pipelines
- Converting to other formats (PDF with searchable text, etc.)
- Building document viewers with text overlay
- Accessibility tools (screen readers, text-to-speech)

## Further Reading

- [HOCR Specification](https://github.com/kba/hocr-spec)
- [HOCR Tools](https://github.com/ocropus/hocr-tools)
