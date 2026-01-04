"""
HMAC (Hash-based Message Authentication Code) Implementation from Scratch
SPHERE - Secure Patient Health Record System

Implements HMAC-SHA256 according to RFC 2104
All cryptographic primitives implemented from scratch - no built-in crypto libraries used
"""

from typing import Union


class SHA256:
    """
    SHA-256 Hash Function Implementation from Scratch
    Follows FIPS 180-4 specification
    """
    
    # Initial hash values (first 32 bits of fractional parts of square roots of first 8 primes)
    H0 = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    
    # Round constants (first 32 bits of fractional parts of cube roots of first 64 primes)
    K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
        0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
        0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    
    def __init__(self):
        self.block_size = 64  # 512 bits = 64 bytes
        self.digest_size = 32  # 256 bits = 32 bytes
    
    @staticmethod
    def _right_rotate(value: int, amount: int) -> int:
        """Right rotate a 32-bit integer"""
        return ((value >> amount) | (value << (32 - amount))) & 0xFFFFFFFF
    
    @staticmethod
    def _right_shift(value: int, amount: int) -> int:
        """Right shift a 32-bit integer"""
        return value >> amount
    
    def _pad_message(self, message: bytes) -> bytes:
        """
        Pad message according to SHA-256 specification
        - Append bit '1' to message
        - Append zeros until message length ≡ 448 (mod 512)
        - Append original length as 64-bit big-endian integer
        """
        original_length = len(message) * 8  # Length in bits
        
        # Append the bit '1' (0x80 = 10000000 in binary)
        message += b'\x80'
        
        # Append zeros until length ≡ 448 (mod 512), i.e., 56 bytes (mod 64)
        while (len(message) % 64) != 56:
            message += b'\x00'
        
        # Append original length as 64-bit big-endian integer
        message += original_length.to_bytes(8, byteorder='big')
        
        return message
    
    def _process_block(self, block: bytes, h: list) -> list:
        """Process a single 512-bit (64-byte) block"""
        
        # Parse block into 16 32-bit big-endian words
        w = []
        for i in range(16):
            w.append(int.from_bytes(block[i*4:(i+1)*4], byteorder='big'))
        
        # Extend the 16 words into 64 words
        for i in range(16, 64):
            # σ0(x) = ROTR^7(x) XOR ROTR^18(x) XOR SHR^3(x)
            s0 = (self._right_rotate(w[i-15], 7) ^ 
                  self._right_rotate(w[i-15], 18) ^ 
                  self._right_shift(w[i-15], 3))
            
            # σ1(x) = ROTR^17(x) XOR ROTR^19(x) XOR SHR^10(x)
            s1 = (self._right_rotate(w[i-2], 17) ^ 
                  self._right_rotate(w[i-2], 19) ^ 
                  self._right_shift(w[i-2], 10))
            
            w.append((w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFF)
        
        # Initialize working variables
        a, b, c, d, e, f, g, hh = h
        
        # Main compression loop
        for i in range(64):
            # Σ1(e) = ROTR^6(e) XOR ROTR^11(e) XOR ROTR^25(e)
            S1 = (self._right_rotate(e, 6) ^ 
                  self._right_rotate(e, 11) ^ 
                  self._right_rotate(e, 25))
            
            # Ch(e,f,g) = (e AND f) XOR ((NOT e) AND g)
            ch = (e & f) ^ ((~e) & g)
            
            # temp1 = h + Σ1(e) + Ch(e,f,g) + K[i] + W[i]
            temp1 = (hh + S1 + ch + self.K[i] + w[i]) & 0xFFFFFFFF
            
            # Σ0(a) = ROTR^2(a) XOR ROTR^13(a) XOR ROTR^22(a)
            S0 = (self._right_rotate(a, 2) ^ 
                  self._right_rotate(a, 13) ^ 
                  self._right_rotate(a, 22))
            
            # Maj(a,b,c) = (a AND b) XOR (a AND c) XOR (b AND c)
            maj = (a & b) ^ (a & c) ^ (b & c)
            
            # temp2 = Σ0(a) + Maj(a,b,c)
            temp2 = (S0 + maj) & 0xFFFFFFFF
            
            # Update working variables
            hh = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF
        
        # Add compressed chunk to current hash value
        return [
            (h[0] + a) & 0xFFFFFFFF,
            (h[1] + b) & 0xFFFFFFFF,
            (h[2] + c) & 0xFFFFFFFF,
            (h[3] + d) & 0xFFFFFFFF,
            (h[4] + e) & 0xFFFFFFFF,
            (h[5] + f) & 0xFFFFFFFF,
            (h[6] + g) & 0xFFFFFFFF,
            (h[7] + hh) & 0xFFFFFFFF
        ]
    
    def hash(self, message: Union[str, bytes]) -> bytes:
        """
        Compute SHA-256 hash of message
        
        Args:
            message: Input message (string or bytes)
        
        Returns:
            32-byte hash digest
        """
        # Convert string to bytes if necessary
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Pad the message
        padded = self._pad_message(message)
        
        # Initialize hash values
        h = self.H0.copy()
        
        # Process each 512-bit block
        for i in range(0, len(padded), 64):
            block = padded[i:i+64]
            h = self._process_block(block, h)
        
        # Produce final hash value (big-endian)
        digest = b''
        for value in h:
            digest += value.to_bytes(4, byteorder='big')
        
        return digest
    
    def hash_hex(self, message: Union[str, bytes]) -> str:
        """
        Compute SHA-256 hash and return as hexadecimal string
        
        Args:
            message: Input message (string or bytes)
        
        Returns:
            64-character hexadecimal hash string
        """
        return self.hash(message).hex()


class HMAC:
    """
    HMAC (Hash-based Message Authentication Code) Implementation
    Follows RFC 2104 specification
    
    HMAC(K, m) = H((K' ⊕ opad) || H((K' ⊕ ipad) || m))
    
    Where:
        K' = key padded to block size (or hashed if longer)
        ipad = 0x36 repeated block_size times
        opad = 0x5c repeated block_size times
        H = hash function (SHA-256)
        || = concatenation
        ⊕ = XOR
    """
    
    def __init__(self, key: Union[str, bytes]):
        """
        Initialize HMAC with a key
        
        Args:
            key: Secret key (string or bytes)
        """
        self.sha256 = SHA256()
        self.block_size = 64  # SHA-256 block size in bytes
        
        # Convert key to bytes if string
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        # If key is longer than block size, hash it
        if len(key) > self.block_size:
            key = self.sha256.hash(key)
        
        # Pad key with zeros to block size
        self.key = key + b'\x00' * (self.block_size - len(key))
        
        # Pre-compute inner and outer padded keys
        self.inner_key = bytes(k ^ 0x36 for k in self.key)  # K' ⊕ ipad
        self.outer_key = bytes(k ^ 0x5c for k in self.key)  # K' ⊕ opad
    
    def compute(self, message: Union[str, bytes]) -> bytes:
        """
        Compute HMAC of message
        
        Args:
            message: Input message (string or bytes)
        
        Returns:
            32-byte HMAC digest
        """
        # Convert message to bytes if string
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Step 1: Compute inner hash: H(inner_key || message)
        inner_hash = self.sha256.hash(self.inner_key + message)
        
        # Step 2: Compute outer hash: H(outer_key || inner_hash)
        return self.sha256.hash(self.outer_key + inner_hash)
    
    def compute_hex(self, message: Union[str, bytes]) -> str:
        """
        Compute HMAC and return as hexadecimal string
        
        Args:
            message: Input message (string or bytes)
        
        Returns:
            64-character hexadecimal HMAC string
        """
        return self.compute(message).hex()
    
    def verify(self, message: Union[str, bytes], expected_mac: str) -> bool:
        """
        Verify HMAC of message against expected value
        Uses constant-time comparison to prevent timing attacks
        
        Args:
            message: Input message
            expected_mac: Expected HMAC (hex string)
        
        Returns:
            True if HMAC matches, False otherwise
        """
        computed_mac = self.compute_hex(message)
        
        # Constant-time comparison to prevent timing attacks
        if len(computed_mac) != len(expected_mac):
            return False
        
        result = 0
        for a, b in zip(computed_mac, expected_mac):
            result |= ord(a) ^ ord(b)
        
        return result == 0


class CBCMAC:
    """
    CBC-MAC Implementation using custom block cipher
    Note: This is a simplified implementation for educational purposes
    Uses a simple Feistel-based block cipher
    """
    
    def __init__(self, key: Union[str, bytes]):
        """
        Initialize CBC-MAC with a key
        
        Args:
            key: Secret key (string or bytes)
        """
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        self.sha256 = SHA256()
        # Derive a 32-byte key using SHA-256
        self.key = self.sha256.hash(key)
        self.block_size = 16  # 128-bit blocks
    
    def _feistel_round(self, left: bytes, right: bytes, round_key: bytes) -> tuple:
        """Perform one round of Feistel cipher"""
        # Simple round function: XOR with hash of (right || round_key)
        f_output = self.sha256.hash(right + round_key)[:8]
        new_left = right
        new_right = bytes(l ^ f for l, f in zip(left, f_output))
        return new_left, new_right
    
    def _encrypt_block(self, block: bytes) -> bytes:
        """Encrypt a single 16-byte block using Feistel network"""
        # Split block into left and right halves
        left = block[:8]
        right = block[8:]
        
        # 16 rounds of Feistel
        for i in range(16):
            # Derive round key from main key
            round_key = self.sha256.hash(self.key + i.to_bytes(4, 'big'))[:16]
            left, right = self._feistel_round(left, right, round_key)
        
        return left + right
    
    def _xor_blocks(self, block1: bytes, block2: bytes) -> bytes:
        """XOR two blocks together"""
        return bytes(a ^ b for a, b in zip(block1, block2))
    
    def _pad_message(self, message: bytes) -> bytes:
        """Pad message to multiple of block size using PKCS7"""
        pad_len = self.block_size - (len(message) % self.block_size)
        return message + bytes([pad_len] * pad_len)
    
    def compute(self, message: Union[str, bytes]) -> bytes:
        """
        Compute CBC-MAC of message
        
        Args:
            message: Input message (string or bytes)
        
        Returns:
            16-byte MAC
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Pad message
        padded = self._pad_message(message)
        
        # Initialize with zero IV
        prev_cipher = b'\x00' * self.block_size
        
        # Process each block in CBC mode
        for i in range(0, len(padded), self.block_size):
            block = padded[i:i + self.block_size]
            # XOR with previous ciphertext
            xored = self._xor_blocks(block, prev_cipher)
            # Encrypt
            prev_cipher = self._encrypt_block(xored)
        
        return prev_cipher
    
    def compute_hex(self, message: Union[str, bytes]) -> str:
        """
        Compute CBC-MAC and return as hexadecimal string
        """
        return self.compute(message).hex()
    
    def verify(self, message: Union[str, bytes], expected_mac: str) -> bool:
        """
        Verify CBC-MAC of message against expected value
        Uses constant-time comparison
        """
        computed_mac = self.compute_hex(message)
        
        if len(computed_mac) != len(expected_mac):
            return False
        
        result = 0
        for a, b in zip(computed_mac, expected_mac):
            result |= ord(a) ^ ord(b)
        
        return result == 0


def test_sha256():
    """Test SHA-256 implementation against known test vectors"""
    print("Testing SHA-256 Implementation...")
    
    sha = SHA256()
    
    # Test vector 1: Empty string
    result = sha.hash_hex("")
    expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert result == expected, f"Empty string test failed: {result}"
    print("✓ Empty string test passed")
    
    # Test vector 2: "abc"
    result = sha.hash_hex("abc")
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert result == expected, f"'abc' test failed: {result}"
    print("✓ 'abc' test passed")
    
    # Test vector 3: Longer string
    result = sha.hash_hex("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq")
    expected = "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
    assert result == expected, f"Long string test failed: {result}"
    print("✓ Long string test passed")
    
    print("✓ All SHA-256 tests passed!\n")


def test_hmac():
    """Test HMAC implementation against known test vectors (RFC 4231)"""
    print("Testing HMAC-SHA256 Implementation...")
    
    # Test vector 1 from RFC 4231
    key1 = bytes([0x0b] * 20)
    data1 = b"Hi There"
    hmac1 = HMAC(key1)
    result1 = hmac1.compute_hex(data1)
    expected1 = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
    assert result1 == expected1, f"Test 1 failed: {result1}"
    print("✓ RFC 4231 Test Vector 1 passed")
    
    # Test vector 2 from RFC 4231
    key2 = b"Jefe"
    data2 = b"what do ya want for nothing?"
    hmac2 = HMAC(key2)
    result2 = hmac2.compute_hex(data2)
    expected2 = "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
    assert result2 == expected2, f"Test 2 failed: {result2}"
    print("✓ RFC 4231 Test Vector 2 passed")
    
    # Test vector 3 from RFC 4231
    key3 = bytes([0xaa] * 20)
    data3 = bytes([0xdd] * 50)
    hmac3 = HMAC(key3)
    result3 = hmac3.compute_hex(data3)
    expected3 = "773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe"
    assert result3 == expected3, f"Test 3 failed: {result3}"
    print("✓ RFC 4231 Test Vector 3 passed")
    
    # Test verification
    assert hmac3.verify(data3, expected3), "Verification test failed"
    assert not hmac3.verify(data3, "wrong_mac" + "0" * 56), "Negative verification test failed"
    print("✓ Verification test passed")
    
    print("✓ All HMAC tests passed!\n")


def test_cbcmac():
    """Test CBC-MAC implementation"""
    print("Testing CBC-MAC Implementation...")
    
    key = "SPHERE_SECRET_KEY"
    mac = CBCMAC(key)
    
    # Test basic functionality
    message = "Patient data: John Doe, Age 45, Diagnosis: Healthy"
    result = mac.compute_hex(message)
    print(f"✓ CBC-MAC computed: {result[:32]}...")
    
    # Test verification
    assert mac.verify(message, result), "CBC-MAC verification failed"
    print("✓ CBC-MAC verification passed")
    
    # Test that different messages produce different MACs
    different_message = "Patient data: Jane Doe, Age 30, Diagnosis: Cold"
    different_result = mac.compute_hex(different_message)
    assert result != different_result, "Different messages should produce different MACs"
    print("✓ Different messages produce different MACs")
    
    print("✓ All CBC-MAC tests passed!\n")


if __name__ == "__main__":
    test_sha256()
    test_hmac()
    test_cbcmac()
    print("=" * 50)
    print("All MAC tests passed successfully!")
    print("=" * 50)
