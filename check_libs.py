try:
    from jose import jwt
    from passlib.context import CryptContext
    print("Imports OK")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    h = pwd_context.hash("test")
    print(f"Bcrypt OK: {h[:10]}...")
except Exception as e:
    print(f"Error: {e}")
