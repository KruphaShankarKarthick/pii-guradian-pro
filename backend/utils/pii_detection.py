import spacy
import re
from typing import List, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.error("spaCy English model not found. Please install with: python -m spacy download en_core_web_sm")
    raise

# PII detection patterns
PII_PATTERNS = {
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'),
    "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
    "date_of_birth": re.compile(r'\b(?:0[1-9]|1[0-2])[\/\-](?:0[1-9]|[12]\d|3[01])[\/\-](?:19|20)\d{2}\b'),
    "zip_code": re.compile(r'\b\d{5}(?:-\d{4})?\b'),
    "ip_address": re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
    "passport": re.compile(r'\b[A-Z]{1,2}[0-9]{6,9}\b'),
    "driver_license": re.compile(r'\b[A-Z]{1,2}[0-9]{6,12}\b'),
}

def detect_pii(text: str, file_path: str) -> List[Dict[str, Any]]:
    """
    Detect PII in extracted text using NLP and regex patterns
    
    Args:
        text: Extracted text from document
        file_path: Path to original file
        
    Returns:
        List of detected PII fields with metadata
    """
    try:
        detected_pii = []
        
        # Use spaCy NER for named entities
        doc = nlp(text)
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "DATE", "MONEY"]:
                pii_field = {
                    "type": _map_spacy_label(ent.label_),
                    "value": _mask_value(ent.text, ent.label_),
                    "original_value": ent.text,
                    "confidence": 0.85,  # Default confidence for spaCy NER
                    "location": {
                        "page": 1,  # Would need page tracking for multi-page
                        "bbox": [0, 0, 0, 0],  # Would need coordinates from OCR
                        "start": ent.start_char,
                        "end": ent.end_char
                    },
                    "encrypted": False,
                    "detection_method": "spacy_ner"
                }
                detected_pii.append(pii_field)
        
        # Use regex patterns for specific PII types
        for pii_type, pattern in PII_PATTERNS.items():
            matches = pattern.finditer(text)
            for match in matches:
                pii_field = {
                    "type": _format_pii_type(pii_type),
                    "value": _mask_value(match.group(), pii_type),
                    "original_value": match.group(),
                    "confidence": _get_pattern_confidence(pii_type),
                    "location": {
                        "page": 1,
                        "bbox": [0, 0, 0, 0],
                        "start": match.start(),
                        "end": match.end()
                    },
                    "encrypted": False,
                    "detection_method": "regex_pattern"
                }
                detected_pii.append(pii_field)
        
        # Remove duplicates and filter by confidence
        filtered_pii = _filter_and_deduplicate_pii(detected_pii)
        
        logger.info(f"PII detection complete. Found {len(filtered_pii)} fields")
        return filtered_pii
        
    except Exception as e:
        logger.error(f"PII detection error: {str(e)}")
        raise Exception(f"Failed to detect PII: {str(e)}")

def _map_spacy_label(label: str) -> str:
    """Map spaCy entity labels to PII types"""
    mapping = {
        "PERSON": "Person Name",
        "ORG": "Organization",
        "GPE": "Location",
        "DATE": "Date",
        "MONEY": "Financial Information"
    }
    return mapping.get(label, label)

def _format_pii_type(pii_type: str) -> str:
    """Format PII type for display"""
    formatting = {
        "ssn": "Social Security Number",
        "phone": "Phone Number",
        "email": "Email Address",
        "credit_card": "Credit Card Number",
        "date_of_birth": "Date of Birth",
        "zip_code": "ZIP Code",
        "ip_address": "IP Address",
        "passport": "Passport Number",
        "driver_license": "Driver License"
    }
    return formatting.get(pii_type, pii_type.replace("_", " ").title())

def _mask_value(value: str, pii_type: str) -> str:
    """Create masked version of PII value"""
    if pii_type in ["ssn", "Social Security Number"]:
        if len(value) >= 4:
            return f"***-**-{value[-4:]}"
    elif pii_type in ["phone", "Phone Number"]:
        if len(value) >= 4:
            return f"***-***-{value[-4:]}"
    elif pii_type in ["email", "Email Address"]:
        if "@" in value:
            username, domain = value.split("@", 1)
            masked_username = username[:2] + "***" if len(username) > 2 else "***"
            return f"{masked_username}@{domain}"
    elif pii_type in ["credit_card", "Credit Card Number"]:
        if len(value) >= 4:
            return f"****-****-****-{value[-4:]}"
    elif len(value) > 4:
        return f"{value[:2]}***{value[-2:]}"
    else:
        return "***"

def _get_pattern_confidence(pii_type: str) -> float:
    """Get confidence score for different PII patterns"""
    confidence_scores = {
        "ssn": 0.95,
        "phone": 0.85,
        "email": 0.95,
        "credit_card": 0.90,
        "date_of_birth": 0.75,
        "zip_code": 0.70,
        "ip_address": 0.80,
        "passport": 0.85,
        "driver_license": 0.80
    }
    return confidence_scores.get(pii_type, 0.70)

def _filter_and_deduplicate_pii(pii_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter PII by confidence and remove duplicates"""
    # Filter by minimum confidence
    MIN_CONFIDENCE = 0.60
    filtered = [pii for pii in pii_list if pii["confidence"] >= MIN_CONFIDENCE]
    
    # Remove duplicates based on value and type
    seen = set()
    deduplicated = []
    
    for pii in filtered:
        key = (pii["type"], pii["original_value"])
        if key not in seen:
            seen.add(key)
            deduplicated.append(pii)
    
    return deduplicated
