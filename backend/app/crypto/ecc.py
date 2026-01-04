"""
ECC (Elliptic Curve Cryptography) Implementation from Scratch
SPHERE - Secure Patient Health Record System
Using secp256k1 curve parameters
"""

import random
from typing import Tuple, Optional

# Import SHA256 implementation from mac module
# We use late import in methods to avoid circular import issues


class Point:
    """Represents a point on an elliptic curve"""
    
    def __init__(self, x: Optional[int], y: Optional[int], curve: 'EllipticCurve'):
        self.x = x
        self.y = y
        self.curve = curve
        self.is_infinity = (x is None and y is None)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y and self.is_infinity == other.is_infinity
    
    def __add__(self, other: 'Point') -> 'Point':
        """Point addition on elliptic curve"""
        if not isinstance(other, Point):
            raise TypeError("Can only add Point to Point")
        
        # Handle point at infinity
        if self.is_infinity:
            return other
        if other.is_infinity:
            return self
        
        p = self.curve.p
        
        # Handle point doubling
        if self.x == other.x:
            if self.y == other.y:
                return self.double()
            else:
                # Points are inverses, result is point at infinity
                return Point(None, None, self.curve)
        
        # Point addition (different points)
        # slope = (y2 - y1) / (x2 - x1) mod p
        slope = ((other.y - self.y) * self.curve.mod_inverse(other.x - self.x, p)) % p
        
        # x3 = slope^2 - x1 - x2 mod p
        x3 = (slope * slope - self.x - other.x) % p
        
        # y3 = slope * (x1 - x3) - y1 mod p
        y3 = (slope * (self.x - x3) - self.y) % p
        
        return Point(x3, y3, self.curve)
    
    def double(self) -> 'Point':
        """Point doubling on elliptic curve"""
        if self.is_infinity:
            return self
        
        p = self.curve.p
        a = self.curve.a
        
        # slope = (3 * x1^2 + a) / (2 * y1) mod p
        numerator = (3 * self.x * self.x + a) % p
        denominator = (2 * self.y) % p
        slope = (numerator * self.curve.mod_inverse(denominator, p)) % p
        
        # x3 = slope^2 - 2 * x1 mod p
        x3 = (slope * slope - 2 * self.x) % p
        
        # y3 = slope * (x1 - x3) - y1 mod p
        y3 = (slope * (self.x - x3) - self.y) % p
        
        return Point(x3, y3, self.curve)
    
    def scalar_multiply(self, k: int) -> 'Point':
        """Scalar multiplication using double-and-add algorithm"""
        if self.is_infinity:
            return self
        
        if k == 0:
            return Point(None, None, self.curve)
        
        if k < 0:
            # Negative scalar: return inverse point
            k = -k
            result = self.scalar_multiply(k)
            return Point(result.x, (-result.y) % self.curve.p, self.curve)
        
        # Binary representation of k
        result = Point(None, None, self.curve)  # Start with point at infinity
        addend = self
        
        while k:
            if k & 1:
                result = result + addend
            addend = addend.double()
            k >>= 1
        
        return result
    
    def __repr__(self) -> str:
        if self.is_infinity:
            return "Point(Infinity)"
        return f"Point({self.x}, {self.y})"


class EllipticCurve:
    """Elliptic Curve y^2 = x^3 + ax + b (mod p)"""
    
    def __init__(self, a: int, b: int, p: int, G: Tuple[int, int], n: int):
        """
        Initialize elliptic curve with parameters
        a, b: curve coefficients
        p: prime modulus
        G: generator point (base point)
        n: order of G
        """
        self.a = a
        self.b = b
        self.p = p
        self.G = Point(G[0], G[1], self)
        self.n = n
    
    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """Calculate modular multiplicative inverse using extended Euclidean algorithm"""
        def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = extended_gcd(a % m, m)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        return x % m


class ECC:
    """ECC Encryption/Decryption implementation"""
    
    def __init__(self):
        # Using secp256k1 curve parameters (used in Bitcoin)
        # y^2 = x^3 + 7 (mod p)
        self.curve = EllipticCurve(
            a=0,
            b=7,
            p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
            G=(
                0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
                0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
            ),
            n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        )
        self.public_key = None
        self.private_key = None
    
    def generate_keypair(self) -> Tuple[Point, int]:
        """
        Generate ECC key pair
        Returns: (public_key_point, private_key_int)
        """
        # Private key: random integer in [1, n-1]
        private_key = random.randint(1, self.curve.n - 1)
        
        # Public key: private_key * G
        public_key = self.curve.G.scalar_multiply(private_key)
        
        self.private_key = private_key
        self.public_key = public_key
        
        return public_key, private_key
    
    def encrypt(self, plaintext: str, public_key: Point) -> str:
        """
        Encrypt plaintext using ECC (ElGamal-style encryption)
        Returns: encrypted string in format "c1x,c1y,c2_hex"
        """
        # Import SHA256 here to avoid circular import
        from .mac import SHA256
        sha256 = SHA256()
        
        # Convert plaintext to integer
        plaintext_bytes = plaintext.encode('utf-8')
        plaintext_hash = sha256.hash(plaintext_bytes)
        m = int.from_bytes(plaintext_hash[:16], byteorder='big')  # Use first 128 bits
        
        # Generate random k
        k = random.randint(1, self.curve.n - 1)
        
        # C1 = k * G
        C1 = self.curve.G.scalar_multiply(k)
        
        # C2 = M + k * public_key
        # We'll encode message in x-coordinate
        shared_secret = public_key.scalar_multiply(k)
        
        # Derive encryption key from shared secret using custom SHA256
        key_bytes = sha256.hash(
            str(shared_secret.x).encode() + str(shared_secret.y).encode()
        )
        
        # XOR plaintext with key (stream cipher style)
        encrypted_bytes = bytes(a ^ b for a, b in zip(plaintext_bytes, key_bytes * (len(plaintext_bytes) // len(key_bytes) + 1)))
        
        c2_hex = encrypted_bytes.hex()
        
        return f"{C1.x},{C1.y},{c2_hex}"
    
    def decrypt(self, ciphertext: str, private_key: int) -> str:
        """
        Decrypt ciphertext using ECC private key
        """
        # Import SHA256 here to avoid circular import
        from .mac import SHA256
        sha256 = SHA256()
        
        parts = ciphertext.split(',')
        c1_x = int(parts[0])
        c1_y = int(parts[1])
        c2_hex = parts[2]
        
        # Reconstruct C1
        C1 = Point(c1_x, c1_y, self.curve)
        
        # Calculate shared secret: private_key * C1
        shared_secret = C1.scalar_multiply(private_key)
        
        # Derive decryption key using custom SHA256
        key_bytes = sha256.hash(
            str(shared_secret.x).encode() + str(shared_secret.y).encode()
        )
        
        # Decrypt
        encrypted_bytes = bytes.fromhex(c2_hex)
        decrypted_bytes = bytes(a ^ b for a, b in zip(encrypted_bytes, key_bytes * (len(encrypted_bytes) // len(key_bytes) + 1)))
        
        return decrypted_bytes.decode('utf-8')
    
    def sign(self, message: str, private_key: int) -> Tuple[int, int]:
        """
        Create digital signature using ECDSA
        Returns: (r, s) signature tuple
        """
        # Import SHA256 here to avoid circular import
        from .mac import SHA256
        sha256 = SHA256()
        
        # Hash the message using custom SHA256
        hash_bytes = sha256.hash(message.encode())
        z = int.from_bytes(hash_bytes, byteorder='big')
        
        while True:
            # Generate random k
            k = random.randint(1, self.curve.n - 1)
            
            # Calculate r = (k * G).x mod n
            point = self.curve.G.scalar_multiply(k)
            r = point.x % self.curve.n
            
            if r == 0:
                continue
            
            # Calculate k_inv = k^-1 mod n
            k_inv = self.curve.mod_inverse(k, self.curve.n)
            
            # Calculate s = k^-1 * (z + r * private_key) mod n
            s = (k_inv * (z + r * private_key)) % self.curve.n
            
            if s == 0:
                continue
            
            return r, s
    
    def verify(self, message: str, signature: Tuple[int, int], public_key: Point) -> bool:
        """
        Verify digital signature using ECDSA
        """
        # Import SHA256 here to avoid circular import
        from .mac import SHA256
        sha256 = SHA256()
        
        r, s = signature
        
        # Check if r and s are in valid range
        if not (1 <= r < self.curve.n and 1 <= s < self.curve.n):
            return False
        
        # Hash the message using custom SHA256
        hash_bytes = sha256.hash(message.encode())
        z = int.from_bytes(hash_bytes, byteorder='big')
        
        # Calculate w = s^-1 mod n
        w = self.curve.mod_inverse(s, self.curve.n)
        
        # Calculate u1 = z * w mod n
        u1 = (z * w) % self.curve.n
        
        # Calculate u2 = r * w mod n
        u2 = (r * w) % self.curve.n
        
        # Calculate point = u1 * G + u2 * public_key
        point1 = self.curve.G.scalar_multiply(u1)
        point2 = public_key.scalar_multiply(u2)
        point = point1 + point2
        
        if point.is_infinity:
            return False
        
        # Verify r == point.x mod n
        return r == (point.x % self.curve.n)


def test_ecc():
    """Test ECC implementation"""
    print("Testing ECC Implementation...")
    
    ecc = ECC()
    public_key, private_key = ecc.generate_keypair()
    
    print(f"Public Key: ({public_key.x}, {public_key.y})")
    print(f"Private Key: {private_key}")
    
    # Test encryption/decryption
    plaintext = "SPHERE Health Record System!"
    print(f"\nOriginal: {plaintext}")
    
    encrypted = ecc.encrypt(plaintext, public_key)
    print(f"Encrypted: {encrypted[:100]}...")
    
    decrypted = ecc.decrypt(encrypted, private_key)
    print(f"Decrypted: {decrypted}")
    
    assert plaintext == decrypted, "Encryption/Decryption failed!"
    
    # Test digital signature
    message = "Test message for signing"
    signature = ecc.sign(message, private_key)
    print(f"\nSignature: {signature}")
    
    is_valid = ecc.verify(message, signature, public_key)
    print(f"Signature valid: {is_valid}")
    
    assert is_valid, "Signature verification failed!"
    print("\n✓ ECC test passed!")


if __name__ == "__main__":
    test_ecc()