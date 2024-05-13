from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"])
print("Enter your password")
password = input()
print(f"Matching password hash is:\n{pwd_context.hash(password)}")
