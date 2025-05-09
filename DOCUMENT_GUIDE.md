# Document Management Guide

This guide explains how to add new documents to your chatbot and manage the dataset.

## Supported Document Types

The chatbot currently supports the following document types:
- PDF (`.pdf`) files
- Word (`.docx`) files

## Adding New Documents

### Quick Method: Using the Add Document Script

The easiest way to add a new document is to use the `add_document.py` script:

```bash
python add_document.py
```

This script will:
1. Show you the current documents in the system
2. Ask for a document ID and path
3. Update the configuration file

### Manual Method: Editing the Configuration

If you prefer, you can manually edit the configuration file:

1. Open `app/config.py`
2. Find the `document_paths` setting
3. Add your new document entry in the format:
   ```python
   {"id": "doc3", "path": "path/to/your/document.pdf"}
   ```

## Testing Documents

Before adding a document to the system, you can test if it can be processed correctly:

```bash
python test_document.py path/to/your/document.pdf
```

This will show you:
- Document statistics (pages, characters, words)
- Content preview
- Any processing errors

## Document Placement

Documents should be placed in the root directory of the application or in a subdirectory. Make sure the path in the configuration file correctly points to the document location.

## After Adding Documents

After adding new documents:

1. Restart the API for changes to take effect:
   ```bash
   python chatbot_api.py
   ```

2. The documents will be automatically loaded into the MongoDB database when the API starts.

## Troubleshooting

If documents aren't being properly loaded:

1. Check the logs in the `logs/` directory
2. Verify the document path is correct
3. Test the document with `test_document.py`
4. Make sure MongoDB is running correctly
5. Check that document format is supported

## Best Practices

- Use unique and descriptive document IDs
- Keep document sizes reasonable
- Ensure documents are properly formatted
- Use high-quality PDFs with extractable text (not scanned images)
- For Word documents, avoid complex formatting that might not be preserved 