import os
import sys
import logging
from pathlib import Path
import shutil
import tempfile

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Import utilities
from utils.ocr import process_ocr
from utils.pii_detection import detect_pii
from utils.encrypt import encrypt_pii_fields, decrypt_pii_fields
from utils.pdf_utils import generate_encrypted_pdf, generate_decrypted_pdf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PII Guardian Pro API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory storage for demo purposes
documents_store = {}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "PII Guardian Pro API is running"}

@app.post("/api/upload")
async def upload_document(document: UploadFile = File(...)):
    """Upload a PDF document for processing"""
    try:
        # Validate file type
        if not document.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{document.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)
        
        # Create document record
        doc_id = str(len(documents_store) + 1)
        doc_record = {
            "id": doc_id,
            "filename": document.filename,
            "original_path": str(file_path),
            "status": "uploaded",
            "detected_pii": None,
            "encrypted_path": None
        }
        documents_store[doc_id] = doc_record
        
        logger.info(f"Document uploaded: {document.filename}")
        return {"document": doc_record}
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/analyze/{document_id}")
async def analyze_document(document_id: str):
    """Analyze document for PII detection"""
    try:
        if document_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = documents_store[document_id]
        doc["status"] = "processing"
        
        # Process OCR
        logger.info(f"Processing OCR for document: {doc['filename']}")
        extracted_text = process_ocr(doc["original_path"])
        
        # Detect PII
        logger.info(f"Detecting PII for document: {doc['filename']}")
        detected_pii = detect_pii(extracted_text, doc["original_path"])
        
        # Update document record
        doc["detected_pii"] = detected_pii
        doc["status"] = "analyzed"
        
        logger.info(f"Analysis complete for {doc['filename']}: {len(detected_pii)} PII fields found")
        return {"document": doc, "detectedPII": detected_pii}
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        if document_id in documents_store:
            documents_store[document_id]["status"] = "error"
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/encrypt")
async def encrypt_document(document_id: str = Form(...), passkey: str = Form(...)):
    """Encrypt detected PII in document"""
    try:
        if document_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = documents_store[document_id]
        
        if not doc["detected_pii"]:
            raise HTTPException(status_code=400, detail="Document must be analyzed first")
        
        if len(passkey) < 8:
            raise HTTPException(status_code=400, detail="Passkey must be at least 8 characters")
        
        # Generate encrypted PDF
        logger.info(f"Encrypting document: {doc['filename']}")
        encrypted_path = generate_encrypted_pdf(
            doc["original_path"], 
            doc["detected_pii"], 
            passkey
        )
        
        # Update document record
        doc["encrypted_path"] = encrypted_path
        doc["status"] = "encrypted"
        
        logger.info(f"Encryption complete for {doc['filename']}")
        return FileResponse(
            encrypted_path,
            filename=f"encrypted_{doc['filename']}",
            media_type="application/pdf"
        )
        
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")

@app.post("/api/decrypt")
async def decrypt_document(document_id: str = Form(...), passkey: str = Form(...)):
    """Decrypt document with passkey"""
    try:
        if document_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = documents_store[document_id]
        
        if not doc["encrypted_path"]:
            raise HTTPException(status_code=404, detail="Encrypted document not found")
        
        # Generate decrypted PDF
        logger.info(f"Decrypting document: {doc['filename']}")
        decrypted_path = generate_decrypted_pdf(
            doc["encrypted_path"],
            doc["detected_pii"],
            passkey
        )
        
        # Update document record
        doc["status"] = "decrypted"
        
        logger.info(f"Decryption complete for {doc['filename']}")
        return FileResponse(
            decrypted_path,
            filename=f"decrypted_{doc['filename']}",
            media_type="application/pdf"
        )
        
    except ValueError as e:
        if "Invalid passkey" in str(e):
            raise HTTPException(status_code=401, detail="Invalid passkey")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")

@app.get("/api/documents")
async def get_documents():
    """Get all documents"""
    return {"documents": list(documents_store.values())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)