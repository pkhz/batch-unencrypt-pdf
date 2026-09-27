# Batch PDF Unencrypt

A small PySide6 desktop app for decrypting many PDF files in one batch using a known password.

## Features

- Select multiple PDF files at once
- Enter a known password for all selected documents
- Choose an output folder for unencrypted files
- Remove selected files before processing
- View a processing log for each file
- Export unencrypted PDFs without changing the original files

## Requirements

- Python 3.10+
- PySide6
- pypdf

## Setup

From the project folder (example C:\path):

```cmd
git clone <repo>
cd C:\path
```

Virtual environment:
```
python -m venv .venv
source .venv/Scripts/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

## Run the app

```powershell
python unencrypt.py
```

## How to use

1. Click "Select PDFs" and choose one or more encrypted PDF files.
2. Optionally click "Remove selected" to delete any file from the upload list.
3. Enter the known password in the password field.
4. Choose an output folder or keep the default folder next to the source files.
5. Click "Unencrypt selected PDFs".
6. Review the log for each file result.

## Notes

- The original PDFs are not modified.
- Decrypted files are written as new PDFs with names like:
  - `document_unencrypted.pdf`
  - `document_unencrypted_1.pdf`
- Files that are not encrypted or use the wrong password will be reported in the log.
