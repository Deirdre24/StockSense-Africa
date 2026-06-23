import bcrypt
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv("apiKey.env")

# supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def sign_up(email: str, password: str, business_name: str, role: str) -> dict:
    existing = supabase.table("users").select("email").eq("email", email).execute()
    if existing.data:
        return {"success": False, "message": "Email already registered."}
    
    password_hash = hash_password(password)
    result = supabase.table("users").insert({
        "email": email,
        "password_hash": password_hash,
        "business_name": business_name,
        "role": role
    }).execute()
    
    if result.data:
        return {"success": True, "user": result.data[0]}
    return {"success": False, "message": "Signup failed. Try again."}

def sign_in(email: str, password: str) -> dict:
    result = supabase.table("users").select("*").eq("email", email).execute()
    if not result.data:
        return {"success": False, "message": "Email not found."}
    
    user = result.data[0]
    if not verify_password(password, user["password_hash"]):
        return {"success": False, "message": "Incorrect password."}
    
    return {"success": True, "user": user}