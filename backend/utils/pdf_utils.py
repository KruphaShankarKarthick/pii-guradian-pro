import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import logging

from .encrypt import encrypt_pii_fields, decrypt_pii_fields, generate_placeholder_text

logger = logging.getLogger(__name__)

def generate_encrypted_pdf(original_path: str, pii_fields: List[Dict[str, Any]], passkey: str) -> str:
    """
    Generate encrypted PDF with PII fields replaced by placeholders
    
    Args:
        original_path: Path to original PDF
        pii_fields: List of detected PII fields
        passkey: Encryption passkey
        
    Returns:
        Path to encrypted PDF file
    """
    try:
        # Encrypt PII fields
        encryption_metadata = encrypt_pii_fields(pii_fields, passkey)
        
        # Open original PDF
        pdf_document = fitz.open(original_path)
        
        # Create new PDF with replacements
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # Replace PII text with placeholders
            for field in encryption_metadata["encrypted_fields"]:
                original_value = field["original_value"]
                placeholder_id = field["placeholder_id"]
                placeholder_text = generate_placeholder_text(placeholder_id, field["type"])
                
                # Find and replace text (simplified approach)
                text_instances = page.search_for(original_value)
                for inst in text_instances:
                    # Add redaction annotation
                    redact_annot = page.add_redact_annot(inst)
                    redact_annot.set_text(placeholder_text)
                    redact_annot.update()
            
            # Apply redactions
            page.apply_redactions()
        
        # Save encrypted PDF
        encrypted_filename = f"encrypted_{Path(original_path).stem}.pdf"
        encrypted_path = Path(original_path).parent / encrypted_filename
        pdf_document.save(str(encrypted_path))
        pdf_document.close()
        
        # Save encryption metadata alongside PDF
        metadata_path = encrypted_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(encryption_metadata, f, indent=2)
        
        logger.info(f"Generated encrypted PDF: {encrypted_path}")
        return str(encrypted_path)
        
    except Exception as e:
        logger.error(f"PDF encryption error: {str(e)}")
        raise Exception(f"Failed to generate encrypted PDF: {str(e)}")

def generate_decrypted_pdf(encrypted_path: str, pii_fields: List[Dict[str, Any]], passkey: str) -> str:
    """
    Generate decrypted PDF by restoring original PII values
    
    Args:
        encrypted_path: Path to encrypted PDF
        pii_fields: Original PII fields metadata
        passkey: Decryption passkey
        
    Returns:
        Path to decrypted PDF file
    """
    try:
        # Load encryption metadata
        metadata_path = Path(encrypted_path).with_suffix('.json')
        if not metadata_path.exists():
            raise FileNotFoundError("Encryption metadata not found")
        
        with open(metadata_path, 'r') as f:
            encryption_metadata = json.load(f)
        
        # Decrypt PII fields
        decrypted_mapping = decrypt_pii_fields(encryption_metadata, passkey)
        
        # Open encrypted PDF
        pdf_document = fitz.open(encrypted_path)
        
        # Restore original values
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # Replace placeholders with original values
            for placeholder_id, original_value in decrypted_mapping.items():
                field_data = encryption_metadata["field_mapping"][placeholder_id]
                placeholder_text = generate_placeholder_text(placeholder_id, field_data["type"])
                
                # Find and replace placeholder text
                text_instances = page.search_for(placeholder_text)
                for inst in text_instances:
                    # Add redaction annotation with original value
                    redact_annot = page.add_redact_annot(inst)
                    redact_annot.set_text(original_value)
                    redact_annot.update()
            
            # Apply redactions
            page.apply_redactions()
        
        # Save decrypted PDF
        decrypted_filename = f"decrypted_{Path(encrypted_path).stem.replace('encrypted_', '')}.pdf"
        decrypted_path = Path(encrypted_path).parent / decrypted_filename
        pdf_document.save(str(decrypted_path))
        pdf_document.close()
        
        logger.info(f"Generated decrypted PDF: {decrypted_path}")
        return str(decrypted_path)
        
    except ValueError as e:
        if "Invalid passkey" in str(e):
            raise ValueError("Invalid passkey provided")
        raise e
    except Exception as e:
        logger.error(f"PDF decryption error: {str(e)}")
        raise Exception(f"Failed to generate decrypted PDF: {str(e)}")

def extract_text_with_coordinates(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract text with coordinate information for precise replacement
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of text blocks with coordinates
    """
    try:
        pdf_document = fitz.open(pdf_path)
        text_blocks = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # Get text with coordinates
            text_dict = page.get_text("dict")
            
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_blocks.append({
                                "text": span["text"],
                                "bbox": span["bbox"],
                                "page": page_num,
                                "font": span["font"],
                                "size": span["size"]
                            })
        
        pdf_document.close()
        return text_blocks
        
    except Exception as e:
        logger.error(f"Text extraction error: {str(e)}")
        raise Exception(f"Failed to extract text with coordinates: {str(e)}")

def create_redacted_pdf_simple(original_path: str, replacements: Dict[str, str]) -> str:
    """
    Simple text replacement approach for PDF redaction
    
    Args:
        original_path: Path to original PDF
        replacements: Dictionary of text to replace (original -> replacement)
        
    Returns:
        Path to redacted PDF
    """
    try:
        # Read original PDF
        with open(original_path, 'rb') as file:
            reader = PdfReader(file)
            writer = PdfWriter()
            
            # Process each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                
                # Extract text content
                content = page.extract_text()
                
                # Apply replacements
                for original, replacement in replacements.items():
                    content = content.replace(original, replacement)
                
                # Note: This is a simplified approach
                # Real implementation would need to modify PDF content streams
                writer.add_page(page)
            
            # Save redacted PDF
            redacted_filename = f"redacted_{Path(original_path).name}"
            redacted_path = Path(original_path).parent / redacted_filename
            
            with open(redacted_path, 'wb') as output_file:
                writer.write(output_file)
        
        return str(redacted_path)
        
    except Exception as e:
        logger.error(f"PDF redaction error: {str(e)}")
        raise Exception(f"Failed to create redacted PDF: {str(e)}")
