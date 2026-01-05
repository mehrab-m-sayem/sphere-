"""
Key Management Module
SPHERE - Secure Patient Health Record System

Handles key generation, storage, distribution, and rotation
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from pathlib import Path

from .rsa import RSA
from .ecc import ECC, Point


class KeyManager:
    """Manages cryptographic keys for the SPHERE system"""
    
    def __init__(self, storage_path: str = "keys"):
        """
        Initialize Key Manager
        
        Args:
            storage_path: Directory to store keys
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.rsa = RSA(key_size=2048)
        self.ecc = ECC()
    
    def generate_user_keys(self, user_id: str) -> Dict:
        """
        Generate RSA and ECC key pairs for a user
        
        Args:
            user_id: Unique user identifier
        
        Returns:
            Dictionary containing all keys
        """
        # Generate RSA keys
        rsa_public, rsa_private = self.rsa.generate_keypair()
        
        # Generate ECC keys
        ecc_public, ecc_private = self.ecc.generate_keypair()
        
        # Prepare key data
        keys = {
            'user_id': user_id,
            'generated_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(days=365)).isoformat(),
            'rsa': {
                'public': {
                    'e': rsa_public[0],
                    'n': rsa_public[1]
                },
                'private': {
                    'd': rsa_private[0],
                    'n': rsa_private[1]
                }
            },
            'ecc': {
                'public': {
                    'x': ecc_public.x,
                    'y': ecc_public.y,
                    'curve': 'secp256k1'
                },
                'private': ecc_private
            }
        }
        
        return keys
    
    def save_keys(self, user_id: str, keys: Dict) -> bool:
        """
        Save user keys to storage
        
        Args:
            user_id: User identifier
            keys: Key dictionary
        
        Returns:
            True if successful
        """
        try:
            # Save public keys (can be shared)
            public_keys = {
                'user_id': user_id,
                'rsa_public': keys['rsa']['public'],
                'ecc_public': keys['ecc']['public'],
                'generated_at': keys['generated_at'],
                'expires_at': keys['expires_at']
            }
            
            public_path = self.storage_path / f"{user_id}_public.json"
            with open(public_path, 'w') as f:
                json.dump(public_keys, f, indent=2)
            
            # Save private keys (must be protected)
            private_keys = {
                'user_id': user_id,
                'rsa_private': keys['rsa']['private'],
                'ecc_private': keys['ecc']['private'],
                'generated_at': keys['generated_at']
            }
            
            private_path = self.storage_path / f"{user_id}_private.json"
            with open(private_path, 'w') as f:
                json.dump(private_keys, f, indent=2)
            
            # Set restrictive permissions on private key file
            os.chmod(private_path, 0o600)
            
            return True
        except Exception as e:
            print(f"Error saving keys: {e}")
            return False
    
    def load_public_keys(self, user_id: str) -> Optional[Dict]:
        """
        Load user's public keys
        
        Args:
            user_id: User identifier
        
        Returns:
            Dictionary with public keys or None
        """
        try:
            public_path = self.storage_path / f"{user_id}_public.json"
            with open(public_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading public keys: {e}")
            return None
    
    def load_private_keys(self, user_id: str) -> Optional[Dict]:
        """
        Load user's private keys
        
        Args:
            user_id: User identifier
        
        Returns:
            Dictionary with private keys or None
        """
        try:
            private_path = self.storage_path / f"{user_id}_private.json"
            with open(private_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading private keys: {e}")
            return None
    
    def get_rsa_public_key(self, user_id: str) -> Optional[Tuple[int, int]]:
        """Get RSA public key as tuple (e, n)"""
        keys = self.load_public_keys(user_id)
        if not keys:
            return None
        
        rsa_pub = keys['rsa_public']
        return (rsa_pub['e'], rsa_pub['n'])
    
    def get_rsa_private_key(self, user_id: str) -> Optional[Tuple[int, int]]:
        """Get RSA private key as tuple (d, n)"""
        keys = self.load_private_keys(user_id)
        if not keys:
            return None
        
        rsa_priv = keys['rsa_private']
        return (rsa_priv['d'], rsa_priv['n'])
    
    def get_ecc_public_key(self, user_id: str) -> Optional[Point]:
        """Get ECC public key as Point"""
        keys = self.load_public_keys(user_id)
        if not keys:
            return None
        
        ecc_pub = keys['ecc_public']
        return Point(ecc_pub['x'], ecc_pub['y'], self.ecc.curve)
    
    def get_ecc_private_key(self, user_id: str) -> Optional[int]:
        """Get ECC private key as integer"""
        keys = self.load_private_keys(user_id)
        if not keys:
            return None
        
        return keys['ecc_private']
    
    def rotate_keys(self, user_id: str) -> bool:
        """
        Rotate user keys (generate new keys)
        
        Args:
            user_id: User identifier
        
        Returns:
            True if successful
        """
        # Archive old keys
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            public_path = self.storage_path / f"{user_id}_public.json"
            private_path = self.storage_path / f"{user_id}_private.json"
            
            if public_path.exists():
                archive_pub = self.storage_path / f"{user_id}_public_{timestamp}.json.bak"
                public_path.rename(archive_pub)
            
            if private_path.exists():
                archive_priv = self.storage_path / f"{user_id}_private_{timestamp}.json.bak"
                private_path.rename(archive_priv)
            
            # Generate and save new keys
            new_keys = self.generate_user_keys(user_id)
            return self.save_keys(user_id, new_keys)
        
        except Exception as e:
            print(f"Error rotating keys: {e}")
            return False
    
    def check_key_expiration(self, user_id: str) -> bool:
        """
        Check if user's keys are expired
        
        Args:
            user_id: User identifier
        
        Returns:
            True if keys are expired
        """
        keys = self.load_public_keys(user_id)
        if not keys:
            return True
        
        expires_at = datetime.fromisoformat(keys['expires_at'])
        return datetime.utcnow() > expires_at
    
    def delete_keys(self, user_id: str) -> bool:
        """
        Delete user keys (e.g., when user account is deleted)
        
        Args:
            user_id: User identifier
        
        Returns:
            True if successful
        """
        try:
            public_path = self.storage_path / f"{user_id}_public.json"
            private_path = self.storage_path / f"{user_id}_private.json"
            
            if public_path.exists():
                public_path.unlink()
            
            if private_path.exists():
                private_path.unlink()
            
            return True
        except Exception as e:
            print(f"Error deleting keys: {e}")
            return False
    
    def list_users_with_keys(self) -> list:
        """List all users who have keys stored"""
        try:
            public_files = list(self.storage_path.glob("*_public.json"))
            user_ids = [f.stem.replace('_public', '') for f in public_files]
            return user_ids
        except Exception as e:
            print(f"Error listing users: {e}")
            return []


# System-wide master key management
class SystemKeyManager:
    """Manages system-wide master keys for additional encryption layer"""
    
    def __init__(self, storage_path: str = "keys"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.master_key_path = self.storage_path / "master_key.json"
    
    def generate_master_key(self) -> Dict:
        """Generate system master keys"""
        rsa = RSA(key_size=4096)  # Larger key for system
        ecc = ECC()
        
        rsa_public, rsa_private = rsa.generate_keypair()
        ecc_public, ecc_private = ecc.generate_keypair()
        
        master_keys = {
            'generated_at': datetime.utcnow().isoformat(),
            'rsa': {
                'public': {'e': rsa_public[0], 'n': rsa_public[1]},
                'private': {'d': rsa_private[0], 'n': rsa_private[1]}
            },
            'ecc': {
                'public': {'x': ecc_public.x, 'y': ecc_public.y},
                'private': ecc_private
            }
        }
        
        return master_keys
    
    def save_master_key(self, master_keys: Dict) -> bool:
        """Save system master keys"""
        try:
            with open(self.master_key_path, 'w') as f:
                json.dump(master_keys, f, indent=2)
            
            # Restrictive permissions
            os.chmod(self.master_key_path, 0o600)
            return True
        except Exception as e:
            print(f"Error saving master key: {e}")
            return False
    
    def load_master_key(self) -> Optional[Dict]:
        """Load system master keys"""
        try:
            if not self.master_key_path.exists():
                # Generate if doesn't exist
                master_keys = self.generate_master_key()
                self.save_master_key(master_keys)
                return master_keys
            
            with open(self.master_key_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading master key: {e}")
            return None


def test_key_management():
    """Test key management system"""
    print("Testing Key Management System...")
    
    # Initialize key manager
    km = KeyManager(storage_path="test_keys")
    
    # Generate keys for a user
    user_id = "test_user_001"
    keys = km.generate_user_keys(user_id)
    print(f"Generated keys for {user_id}")
    
    # Save keys
    success = km.save_keys(user_id, keys)
    assert success, "Failed to save keys"
    print("Keys saved successfully")
    
    # Load public keys
    public_keys = km.load_public_keys(user_id)
    assert public_keys is not None, "Failed to load public keys"
    print("Public keys loaded successfully")
    
    # Load private keys
    private_keys = km.load_private_keys(user_id)
    assert private_keys is not None, "Failed to load private keys"
    print("Private keys loaded successfully")
    
    # Test key retrieval
    rsa_pub = km.get_rsa_public_key(user_id)
    assert rsa_pub is not None, "Failed to get RSA public key"
    print(f"RSA Public Key: (e={rsa_pub[0]}, n={rsa_pub[1][:50]}...)")
    
    # Check expiration
    is_expired = km.check_key_expiration(user_id)
    print(f"Keys expired: {is_expired}")
    
    # List users
    users = km.list_users_with_keys()
    print(f"Users with keys: {users}")
    
    # Clean up test keys
    km.delete_keys(user_id)
    print("Test keys deleted")
    
    # Test system master key
    print("\nTesting System Master Key...")
    skm = SystemKeyManager(storage_path="test_keys")
    master_key = skm.load_master_key()
    assert master_key is not None, "Failed to load master key"
    print("Master key loaded/generated")
    
    print("\nAll key management tests passed!")


if __name__ == "__main__":
    test_key_management()