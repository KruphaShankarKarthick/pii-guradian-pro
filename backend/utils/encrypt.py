from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def generate_key_from_passkey(passkey: str, salt: bytes = None) -> tuple:
    """
    Generate encryption key from user passkey
    
    Args:
        passkey: User-provided passkey
        salt: Salt for key derivation (generated if None)
        
    Returns:
        Tuple of (encryption_key, salt)
    """
    if salt is None:
        salt = base64.urlsafe_b64encode(b"piiguardian_salt_2024")  # Fixed salt for demo
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(passkey.encode()))
    return key, salt

def encrypt_pii_fields(pii_fields: List[Dict[str, Any]], passkey: str) -> Dict[str, Any]:
    """
    Encrypt PII field values using AES-256
    
    Args:
        pii_fields: List of detected PII fields
        passkey: User-provided encryption passkey
        
    Returns:
        Dictionary containing encrypted data and metadata
    """
    try:
        key, salt = generate_key_from_passkey(passkey)
        fernet = Fernet(key)
        
        encrypted_fields = []
        field_mapping = {}  # Map placeholder IDs to encrypted data
        
        for i, field in enumerate(pii_fields):
            # Generate placeholder ID
            placeholder_id = f"ENCRYPTED_FIELD_{i+1:03d}"
            
            # Encrypt the original value
            encrypted_value = fernet.encrypt(field["original_value"].encode())
            
            # Create encrypted field record
            encrypted_field = {
                **field,
                "placeholder_id": placeholder_id,
                "encrypted_value": base64.b64encode(encrypted_value).decode(),
                "encrypted": True
            }
            encrypted_fields.append(encrypted_field)
            
            # Store mapping for PDF replacement
            field_mapping[placeholder_id] = {
                "original_value": field["original_value"],
                "encrypted_value": encrypted_field["encrypted_value"],
                "type": field["type"],
                "location": field["location"]
            }
        
        encryption_metadata = {
            "encrypted_fields": encrypted_fields,
            "field_mapping": field_mapping,
            "salt": base64.b64encode(salt).decode(),
            "encryption_method": "AES-256-Fernet"
        }
        
        logger.info(f"Encrypted {len(pii_fields)} PII fields")
        return encryption_metadata
        
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        raise Exception(f"Failed to encrypt PII fields: {str(e)}")

def decrypt_pii_fields(encrypted_metadata: Dict[str, Any], passkey: str) -> Dict[str, str]:
    """
    Decrypt PII field values using the provided passkey
    
    Args:
        encrypted_metadata: Encryption metadata from encrypt_pii_fields
        passkey: User-provided decryption passkey
        
    Returns:
        Dictionary mapping placeholder IDs to original values
    """
    try:
        salt = base64.b64decode(encrypted_metadata["salt"])
        key, _ = generate_key_from_passkey(passkey, salt)
        fernet = Fernet(key)
        
        decrypted_mapping = {}
        
        for placeholder_id, field_data in encrypted_metadata["field_mapping"].items():
            try:
                # Decrypt the encrypted value
                encrypted_bytes = base64.b64decode(field_data["encrypted_value"])
                decrypted_value = fernet.decrypt(encrypted_bytes).decode()
                
                decrypted_mapping[placeholder_id] = decrypted_value
                
            except Exception as e:
                logger.error(f"Failed to decrypt field {placeholder_id}: {str(e)}")
                raise ValueError("Invalid passkey or corrupted data")
        
        logger.info(f"Decrypted {len(decrypted_mapping)} PII fields")
        return decrypted_mapping
        
    except Exception as e:
        if "Invalid passkey" in str(e):
            raise ValueError("Invalid passkey provided")
        logger.error(f"Decryption error: {str(e)}")
        raise Exception(f"Failed to decrypt PII fields: {str(e)}")

def generate_placeholder_text(placeholder_id: str, pii_type: str) -> str:
    """
    Generate placeholder text for encrypted fields
    
    Args:
        placeholder_id: Unique placeholder identifier
        pii_type: Type of PII being replaced
        
    Returns:
        Formatted placeholder text
    """
    return f"[{placeholder_id}:{pii_type}]"

def validate_passkey_strength(passkey: str) -> bool:
    """
    Validate passkey meets minimum security requirements
    
    Args:
        passkey: User-provided passkey
        
    Returns:
        True if passkey meets requirements
    """
    if len(passkey) < 8:
        return False
    
    # Could add additional complexity requirements here
    # - Upper/lowercase letters
    # - Numbers
    # - Special characters
    
    return True
