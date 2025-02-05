import bcrypt
import os

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()  # Stocker ce hash en base


def verify_password(stored_hash, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_hash.encode())  # Vérifie avec le hash stocké


print(verify_password('$2b$12$jfyCf2MkZfWyHc.QvCppjuS4gq7XgMWba.RLTQx9z9L77G/kcIXIe','admin'))