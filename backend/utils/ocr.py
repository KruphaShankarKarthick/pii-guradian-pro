import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def process_ocr(file_path: str) -> str:
    """
    Extract text from PDF using OCR
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text as string
    """
    try:
        extracted_text = ""
        
        # Open PDF document
        pdf_document = fitz.open(file_path)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            
            # First try to extract text directly
            text = page.get_text()
            if text.strip():
                extracted_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
            else:
                # If no text found, use OCR on page image
                logger.info(f"No text found on page {page_num + 1}, using OCR")
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # Higher resolution
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("ppm")
                
                # Convert to PIL Image
                img = Image.open(io.BytesIO(img_data))
                
                # Preprocess image for better OCR
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                
                # Apply image enhancement
                gray = cv2.medianBlur(gray, 3)
                
                # Convert back to PIL
                processed_img = Image.fromarray(gray)
                
                # Perform OCR
                ocr_text = pytesseract.image_to_string(
                    processed_img,
                    config='--oem 3 --psm 6'  # Use LSTM OCR engine
                )
                
                if ocr_text.strip():
                    extracted_text += f"\n--- Page {page_num + 1} (OCR) ---\n{ocr_text}\n"
        
        pdf_document.close()
        
        logger.info(f"OCR extraction complete. Text length: {len(extracted_text)}")
        return extracted_text
        
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def preprocess_image_for_ocr(image_path: str) -> Image.Image:
    """
    Preprocess image to improve OCR accuracy
    
    Args:
        image_path: Path to image file
        
    Returns:
        Preprocessed PIL Image
    """
    # Load image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply noise reduction
    denoised = cv2.medianBlur(gray, 5)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Convert back to PIL Image
    return Image.fromarray(thresh)
