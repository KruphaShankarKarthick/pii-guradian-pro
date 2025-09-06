# PII Guardian Pro - Linked Visual Data Privacy with Selective AES Encryption

A full-stack PII (Personally Identifiable Information) protection platform that allows users to upload PDF documents, automatically detect sensitive information, and encrypt only the PII fields using AES encryption.

## Features

- 🔍 **AI-Powered PII Detection**: Automatically detects names, addresses, SSNs, phone numbers, emails, and more
- 🔒 **Selective AES Encryption**: Encrypts only sensitive data while preserving document structure
- 📄 **OCR Processing**: Extracts text from scanned documents and images
- 🌐 **Full-Stack Solution**: React frontend with Python FastAPI backend
- 📱 **Modern UI**: Professional interface with drag-and-drop functionality

## Project Structure

```
project-root/
├── frontend/           (React + Tailwind)
│   ├── src/
│   │   ├── App.js
│   │   └── components/
│   │       ├── DragDropUpload.js
│   │       ├── EncryptButton.js
│   │       └── DecryptButton.js
│   └── package.json
├── backend/           (Python FastAPI)
│   ├── main.py
│   ├── requirements.txt
│   └── utils/
│       ├── ocr.py
│       ├── pii_detection.py
│       ├── encrypt.py
│       └── pdf_utils.py
├── data/             (For test datasets)
└── README.md
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Download the spaCy English model:
```bash
python -m spacy download en_core_web_sm
```

4. Run the backend server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## Usage

1. **Upload Document**: Drag and drop a PDF file or click "Choose Files"
2. **PII Detection**: The system automatically analyzes the document for sensitive information
3. **Encrypt PDF**: Set a passkey and download the encrypted version with PII replaced by placeholders
4. **Decrypt PDF**: Enter your passkey to restore the original content

## Technology Stack

### Frontend
- **React 18**: Modern component-based UI
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Beautiful icons
- **React Router**: Client-side routing

### Backend
- **FastAPI**: High-performance Python web framework
- **PyTesseract**: OCR engine for text extraction
- **spaCy**: Natural language processing for named entity recognition
- **Cryptography**: AES-256 encryption
- **PyMuPDF & PyPDF2**: PDF processing and manipulation
- **OpenCV & Pillow**: Image processing

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload` - Upload PDF document
- `POST /api/analyze/{document_id}` - Analyze document for PII
- `POST /api/encrypt` - Encrypt PII fields in document
- `POST /api/decrypt` - Decrypt document with passkey
- `GET /api/documents` - List all documents

## Security Features

- **AES-256 Encryption**: Industry-standard encryption for sensitive data
- **PBKDF2 Key Derivation**: Secure key generation from passphrases
- **Selective Encryption**: Only PII fields are encrypted, preserving document layout
- **Zero-Knowledge Architecture**: Passphrases are not stored on the server

## License

This project is licensed under the MIT License.