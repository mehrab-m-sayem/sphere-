"""
RSA Encryption Implementation 
"""

import random
import math
from typing import Tuple


class RSA:
    """RSA Encryption/Decryption implementation from scratch"""
    
    def __init__(self, key_size: int = 1024):
        self.key_size = key_size
        self.public_key = None
        self.private_key = None
    
    @staticmethod
    def is_prime(n: int, k: int = 5) -> bool:
        """Miller-Rabin primality test"""
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False
        
        # Write n-1 as 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        # Witness loop
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n)
            
            if x == 1 or x == n - 1:
                continue
            
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        
        return True
    
    @staticmethod
    def generate_prime(bits: int) -> int:
        """Generate a prime number with specified bit length"""
        while True:
            num = random.getrandbits(bits)
            # Set MSB and LSB to ensure odd number of correct bit length
            num |= (1 << bits - 1) | 1
            if RSA.is_prime(num):
                return num
    
    @staticmethod
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """Extended Euclidean Algorithm"""
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = RSA.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    @staticmethod
    def mod_inverse(e: int, phi: int) -> int:
        """Calculate modular multiplicative inverse"""
        gcd, x, _ = RSA.extended_gcd(e, phi)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return x % phi
    
    def generate_keypair(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Generate RSA key pair
        Returns: ((e, n), (d, n)) where (e,n) is public key and (d,n) is private key
        """
        # Generate two distinct primes
        p = self.generate_prime(self.key_size // 2)
        q = self.generate_prime(self.key_size // 2)
        
        while p == q:
            q = self.generate_prime(self.key_size // 2)
        
        # Calculate n and phi(n)
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # Choose e (commonly 65537)
        e = 65537
        
        # Ensure e and phi are coprime
        while math.gcd(e, phi) != 1:
            e = random.randrange(2, phi)
        
        # Calculate d (private exponent)
        d = self.mod_inverse(e, phi)
        
        self.public_key = (e, n)
        self.private_key = (d, n)
        
        return self.public_key, self.private_key
    
    @staticmethod
    def encrypt_block(plaintext_block: int, public_key: Tuple[int, int]) -> int:
        """Encrypt a single block using public key"""
        e, n = public_key
        return pow(plaintext_block, e, n)
    
    @staticmethod
    def decrypt_block(ciphertext_block: int, private_key: Tuple[int, int]) -> int:
        """Decrypt a single block using private key"""
        d, n = private_key
        return pow(ciphertext_block, d, n)
    
    @staticmethod
    def bytes_to_int(data: bytes) -> int:
        """Convert bytes to integer"""
        return int.from_bytes(data, byteorder='big')
    
    @staticmethod
    def int_to_bytes(num: int, length: int) -> bytes:
        """Convert integer to bytes"""
        return num.to_bytes(length, byteorder='big')
    
    def encrypt(self, plaintext: str, public_key: Tuple[int, int]) -> str:
        """
        Encrypt plaintext string using RSA
        Returns hex-encoded ciphertext
        """
        e, n = public_key
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Calculate block size (in bytes)
        # Must be less than log2(n)/8 to avoid overflow
        block_size = (n.bit_length() - 1) // 8
        
        encrypted_blocks = []
        
        # Pad plaintext if necessary
        while len(plaintext_bytes) % block_size != 0:
            plaintext_bytes += b'\x00'
        
        # Encrypt each block
        for i in range(0, len(plaintext_bytes), block_size):
            block = plaintext_bytes[i:i + block_size]
            block_int = self.bytes_to_int(block)
            
            # Ensure block is smaller than n
            if block_int >= n:
                raise ValueError("Block too large for key size")
            
            encrypted_block = self.encrypt_block(block_int, public_key)
            encrypted_blocks.append(encrypted_block)
        
        # Convert to hex string
        return ','.join(hex(block)[2:] for block in encrypted_blocks)
    
    def decrypt(self, ciphertext: str, private_key: Tuple[int, int]) -> str:
        """
        Decrypt hex-encoded ciphertext using RSA
        Returns plaintext string
        """
        d, n = private_key
        
        # Parse hex-encoded blocks
        encrypted_blocks = [int(block, 16) for block in ciphertext.split(',')]
        
        # Calculate block size
        block_size = (n.bit_length() - 1) // 8
        
        decrypted_bytes = b''
        
        # Decrypt each block
        for encrypted_block in encrypted_blocks:
            decrypted_block = self.decrypt_block(encrypted_block, private_key)
            block_bytes = self.int_to_bytes(decrypted_block, block_size)
            decrypted_bytes += block_bytes
        
        # Remove padding
        decrypted_bytes = decrypted_bytes.rstrip(b'\x00')
        
        return decrypted_bytes.decode('utf-8')


def test_rsa():
    """Test RSA implementation"""
    print("Testing RSA Implementation...")
    
    rsa = RSA(key_size=512)  # Smaller key for faster testing
    public_key, private_key = rsa.generate_keypair()
    
    print(f"Public Key: {public_key}")
    print(f"Private Key: {private_key}")
    
    # Test encryption/decryption
    plaintext = "Hello, SPHERE! This is a test message."
    print(f"\nOriginal: {plaintext}")
    
    encrypted = rsa.encrypt(plaintext, public_key)
    print(f"Encrypted: {encrypted[:100]}...")
    
    decrypted = rsa.decrypt(encrypted, private_key)
    print(f"Decrypted: {decrypted}")
    
    assert plaintext == decrypted, "Encryption/Decryption failed!"
    print("\n✓ RSA test passed!")


if __name__ == "__main__":
    test_rsa()