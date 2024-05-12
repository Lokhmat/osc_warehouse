from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print("Enter your password")
password = input()
print(f"Matching password hash is:\n{pwd_context.hash(password)}")
