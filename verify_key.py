from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# GitHub App credentials (loaded securely at runtime)
import os

private_key = os.environ.get("GITHUB_PRIVATE_KEY", "")
if not private_key:
    raise RuntimeError("GITHUB_PRIVATE_KEY not set")

print(f"Private key length: {len(private_key)}")

try:
    # Load the private key
    key_bytes = private_key.encode('utf-8')
    private_key_obj = serialization.load_pem_private_key(
        key_bytes,
        password=None
    )
    
    # Get the public key
    public_key = private_key_obj.public_key()
    
    # Serialize the public key
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    print("Private key is valid!")
    print(f"Public key: {pem.decode('utf-8')[:50]}...")
except Exception as e:
    print(f"Error loading private key: {str(e)}")
    import traceback
    traceback.print_exc()
