import bcrypt

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with a salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def check_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False
