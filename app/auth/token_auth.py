# app/auth/token_auth.py

import os
from fastapi import Header, HTTPException, Depends
from dotenv import load_dotenv

load_dotenv()

def verify_token(authorization: str = Header(None)):
    expected_token = os.getenv("HACKRX_SECRET_TOKEN")

    print("Incoming Authorization:", authorization)
    print("Expected Authorization:", f"Bearer {expected_token}")

    if not authorization or authorization != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return True
