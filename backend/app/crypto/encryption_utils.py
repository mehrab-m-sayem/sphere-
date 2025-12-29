"""
Encryption Utilities
SPHERE - Secure Patient Health Record System

High-level encryption/decryption functions combining RSA, ECC, and HMAC
"""

import json
from typing import Dict, Any, Tuple, Optional

from .rsa import RSA
from .ecc import ECC, Point
from .mac import HMAC
from .key_management import KeyManager


class DataEncryptor:
    """
    Handles encryption and decryption of user data
    Implements multi-level encryption (RSA + ECC) for enhanced security
    """
    
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
        self.rsa = RSA(key_size=2048)
        self.ecc = ECC()
        self.hmac_key = "SPHERE_SYSTEM_HMAC_KEY_2025"  # Should be stored securely
    
    def encrypt_data(self, data: str, user_id: str, use_multi_level: bool = True) -> Dict[str, str]:
        """
        Encrypt data using asymmetric encryption
        
        Args:
            data: Plaintext data to encrypt
            user_id: User ID for key retrieval
            use_multi_level: If True, use RSA + ECC multi-level encryption
        
        Returns:
            Dictionary containing encrypted data and metadata
        """
        # Get user's public keys
        rsa_public = self.key_manager.get_rsa_public_key(user_id)
        
        if not rsa_public:
            raise ValueError(f"No public key found for user {user_id}")
        
        # First level: RSA encryption
        encrypted_rsa = self.rsa.encrypt(data, rsa_public)
        
        if use_multi_level:
            # Second level: ECC encryption
            ecc_public = self.key_manager.get_ecc_public_key(user_id)
            if not ecc_public:
                raise ValueError(f"No ECC public key found for user {user_id}")
            
            encrypted_ecc = self.ecc.encrypt(encrypted_rsa, ecc_public)
            final_encrypted = encrypted_ecc
            encryption_method = "RSA+ECC"
        else:
            final_encrypted = encrypted_rsa
            encryption_method = "RSA"
        
        # Generate HMAC for integrity verification
        hmac = HMAC(self.hmac_key)
        mac = hmac.compute_hex(final_encrypted)
        
        return {
            'encrypted_data': final_encrypted,
            'mac': mac,
            'encryption_method': encryption_method,
            'user_id': user_id
        }
    
    def decrypt_data(self, encrypted_dict: Dict[str, str]) -> str:
        """
        Decrypt data and verify integrity
        
        Args:
            encrypted_dict: Dictionary containing encrypted data and metadata
        
        Returns:
            Decrypted plaintext data
        
        Raises:
            ValueError: If MAC verification fails or decryption fails
        """
        encrypted_data = encrypted_dict['encrypted_data']
        mac = encrypted_dict['mac']
        encryption_method = encrypted_dict['encryption_method']
        user_id = encrypted_dict['user_id']
        
        # Verify HMAC
        hmac = HMAC(self.hmac_key)
        if not hmac.verify(encrypted_data, mac):
            raise ValueError("Data integrity check failed - MAC verification failed")
        
        # Get user's private keys
        rsa_private = self.key_manager.get_rsa_private_key(user_id)
        if not rsa_private:
            raise ValueError(f"No private key found for user {user_id}")
        
        if encryption_method == "RSA+ECC":
            # First decrypt with ECC
            ecc_private = self.key_manager.get_ecc_private_key(user_id)
            if not ecc_private:
                raise ValueError(f"No ECC private key found for user {user_id}")
            
            decrypted_ecc = self.ecc.decrypt(encrypted_data, ecc_private)
            
            # Then decrypt with RSA
            decrypted_rsa = self.rsa.decrypt(decrypted_ecc, rsa_private)
            return decrypted_rsa
        else:
            # Single-level RSA decryption
            return self.rsa.decrypt(encrypted_data, rsa_private)
    
    def encrypt_field(self, field_value: Any, user_id: str) -> str:
        """
        Encrypt a single field value
        Handles conversion of different data types to string
        """
        if field_value is None:
            return None
        
        # Convert to string for encryption
        str_value = str(field_value)
        
        encrypted_dict = self.encrypt_data(str_value, user_id, use_multi_level=False)
        
        # Return as JSON string for storage
        return json.dumps(encrypted_dict)
    
    def decrypt_field(self, encrypted_field: str) -> Any:
        """
        Decrypt a single field value
        """
        if not encrypted_field:
            return None
        
        try:
            encrypted_dict = json.loads(encrypted_field)
            return self.decrypt_data(encrypted_dict)
        except Exception as e:
            print(f"Error decrypting field: {e}")
            return None
    
    def encrypt_user_profile(self, profile_data: Dict[str, Any], user_id: str) -> Dict[str, str]:
        """
        Encrypt all fields in a user profile
        
        Args:
            profile_data: Dictionary of profile fields
            user_id: User ID
        
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_profile = {}
        
        # Fields that should be encrypted
        sensitive_fields = ['name', 'email', 'contact_no', 'age', 'sex', 'specialization']
        
        for field, value in profile_data.items():
            if field in sensitive_fields and value is not None:
                encrypted_profile[field] = self.encrypt_field(value, user_id)
            else:
                # Non-sensitive fields can be stored as-is
                encrypted_profile[field] = value
        
        return encrypted_profile
    
    def decrypt_user_profile(self, encrypted_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt all encrypted fields in a user profile
        
        Args:
            encrypted_profile: Dictionary with encrypted fields
        
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_profile = {}
        
        for field, value in encrypted_profile.items():
            # Try to decrypt if it looks like encrypted data
            if isinstance(value, str) and value.startswith('{') and '"encrypted_data"' in value:
                try:
                    decrypted_profile[field] = self.decrypt_field(value)
                except:
                    decrypted_profile[field] = value
            else:
                decrypted_profile[field] = value
        
        return decrypted_profile


class MessageEncryptor:
    """
    Handles encryption of messages between users
    """
    
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
        self.rsa = RSA(key_size=2048)
        self.ecc = ECC()
    
    def encrypt_message(self, message: str, sender_id: str, recipient_id: str) -> Dict[str, str]:
        """
        Encrypt message from sender to recipient
        
        Args:
            message: Message text
            sender_id: Sender user ID
            recipient_id: Recipient user ID
        
        Returns:
            Dictionary with encrypted message and signature
        """
        # Encrypt message with recipient's public key
        recipient_rsa_public = self.key_manager.get_rsa_public_key(recipient_id)
        if not recipient_rsa_public:
            raise ValueError(f"No public key for recipient {recipient_id}")
        
        encrypted_message = self.rsa.encrypt(message, recipient_rsa_public)
        
        # Sign message with sender's private key
        sender_ecc_private = self.key_manager.get_ecc_private_key(sender_id)
        if not sender_ecc_private:
            raise ValueError(f"No private key for sender {sender_id}")
        
        signature = self.ecc.sign(message, sender_ecc_private)
        
        return {
            'encrypted_message': encrypted_message,
            'signature_r': signature[0],
            'signature_s': signature[1],
            'sender_id': sender_id,
            'recipient_id': recipient_id
        }
    
    def decrypt_and_verify_message(self, encrypted_dict: Dict) -> Tuple[str, bool]:
        """
        Decrypt message and verify signature
        
        Returns:
            Tuple of (decrypted_message, signature_valid)
        """
        encrypted_message = encrypted_dict['encrypted_message']
        signature = (encrypted_dict['signature_r'], encrypted_dict['signature_s'])
        sender_id = encrypted_dict['sender_id']
        recipient_id = encrypted_dict['recipient_id']
        
        # Decrypt with recipient's private key
        recipient_rsa_private = self.key_manager.get_rsa_private_key(recipient_id)
        if not recipient_rsa_private:
            raise ValueError(f"No private key for recipient {recipient_id}")
        
        decrypted_message = self.rsa.decrypt(encrypted_message, recipient_rsa_private)
        
        # Verify signature with sender's public key
        sender_ecc_public = self.key_manager.get_ecc_public_key(sender_id)
        if not sender_ecc_public:
            return decrypted_message, False
        
        signature_valid = self.ecc.verify(decrypted_message, signature, sender_ecc_public)
        
        return decrypted_message, signature_valid


def test_encryption_utils():
    """Test encryption utilities"""
    print("Testing Encryption Utilities...")
    
    # Setup
    km = KeyManager(storage_path="test_keys")
    user_id = "test_user_001"
    
    # Generate keys
    keys = km.generate_user_keys(user_id)
    km.save_keys(user_id, keys)
    
    # Test data encryption
    encryptor = DataEncryptor(km)
    
    print("\n1. Testing single-level encryption (RSA only)...")
    data = "Patient Name: John Doe, Age: 35, Condition: Healthy"
    encrypted = encryptor.encrypt_data(data, user_id, use_multi_level=False)
    print(f"Original: {data}")
    print(f"Encrypted: {encrypted['encrypted_data'][:100]}...")
    
    decrypted = encryptor.decrypt_data(encrypted)
    print(f"Decrypted: {decrypted}")
    assert data == decrypted, "Single-level encryption failed!"
    print("✓ Single-level encryption test passed")
    
    print("\n2. Testing multi-level encryption (RSA + ECC)...")
    encrypted_multi = encryptor.encrypt_data(data, user_id, use_multi_level=True)
    print(f"Encrypted: {encrypted_multi['encrypted_data'][:100]}...")
    
    decrypted_multi = encryptor.decrypt_data(encrypted_multi)
    print(f"Decrypted: {decrypted_multi}")
    assert data == decrypted_multi, "Multi-level encryption failed!"
    print("✓ Multi-level encryption test passed")
    
    print("\n3. Testing profile encryption...")
    profile = {
        'name': 'Dr. Jane Smith',
        'email': 'jane.smith@hospital.com',
        'contact_no': '+1234567890',
        'specialization': 'Cardiology'
    }
    
    encrypted_profile = encryptor.encrypt_user_profile(profile, user_id)
    print(f"Encrypted profile keys: {list(encrypted_profile.keys())}")
    
    decrypted_profile = encryptor.decrypt_user_profile(encrypted_profile)
    print(f"Decrypted profile: {decrypted_profile}")
    assert profile['name'] == decrypted_profile['name'], "Profile encryption failed!"
    print("✓ Profile encryption test passed")
    
    # Cleanup
    km.delete_keys(user_id)
    
    print("\n✓ All encryption utility tests passed!")


if __name__ == "__main__":
    test_encryption_utils()