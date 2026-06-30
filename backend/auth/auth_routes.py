import os, sys
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.database import get_db, User
from auth.auth import (hash_password, verify_password, encrypt, decrypt,
                       create_access_token, create_refresh_token,
                       decode_token, generate_otp, send_otp_email)

router = APIRouter(prefix="/auth", tags=["auth"])
otp_store: dict = {}

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(401, "Invalid or expired token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    users = db.query(User).all()
    if any(decrypt(u.email_encrypted) == req.email for u in users):
        raise HTTPException(400, "Email already registered")

    otp = generate_otp()
    otp_store[req.email] = (otp, datetime.utcnow() + timedelta(minutes=10))
    otp_store[f"{req.email}_data"] = {
        "name": req.name,
        "password_hash": hash_password(req.password),
    }

    sent = send_otp_email(req.email, otp, req.name)
    if not sent:
        raise HTTPException(500, "Failed to send verification email")

    return {"message": "OTP sent to your email. Please verify to complete registration."}


@router.post("/verify")
def verify(req: VerifyRequest, db: Session = Depends(get_db)):
    entry = otp_store.get(req.email)
    if not entry:
        raise HTTPException(400, "No OTP found. Please register again.")

    otp, expires = entry
    if datetime.utcnow() > expires:
        otp_store.pop(req.email, None)
        raise HTTPException(400, "OTP expired. Please register again.")

    if req.otp != otp:
        raise HTTPException(400, "Invalid OTP")

    data = otp_store.pop(f"{req.email}_data", {})
    otp_store.pop(req.email, None)

    user = User(
        name=data.get("name") or req.email.split("@")[0],
        email_encrypted=encrypt(req.email),
        password_hash=data["password_hash"],
        is_verified="True",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Email verified. Account created.",
        "access_token":  create_access_token(user.id, req.email),
        "refresh_token": create_refresh_token(user.id),
    }


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    users = db.query(User).all()
    user = next((u for u in users if decrypt(u.email_encrypted) == req.email), None)
    if not user:
        raise HTTPException(401, "Invalid email or password")
    if user.is_verified != "True":
        raise HTTPException(401, "Email not verified")
    if not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

    return {
        "access_token":  create_access_token(user.id, req.email),
        "refresh_token": create_refresh_token(user.id),
        "user": {"id": user.id, "name": user.name, "email": req.email},
    }


@router.post("/refresh")
def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(401, "User not found")
    return {"access_token": create_access_token(user.id, decrypt(user.email_encrypted))}


class ForgotRequest(BaseModel):
    email: EmailStr

class ResetRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


@router.post("/forgot-password")
def forgot_password(req: ForgotRequest, db: Session = Depends(get_db)):
    users = db.query(User).all()
    user = next((u for u in users if decrypt(u.email_encrypted) == req.email), None)
    if not user:
        raise HTTPException(404, "No account found with this email")

    otp = generate_otp()
    otp_store[f"reset_{req.email}"] = (otp, datetime.utcnow() + timedelta(minutes=10))
    sent = send_otp_email(req.email, otp, user.name)
    if not sent:
        raise HTTPException(500, "Failed to send email")

    return {"message": "OTP sent to your email"}


@router.post("/reset-password")
def reset_password(req: ResetRequest, db: Session = Depends(get_db)):
    entry = otp_store.get(f"reset_{req.email}")
    if not entry:
        raise HTTPException(400, "No OTP found. Request a new one.")

    otp, expires = entry
    if datetime.utcnow() > expires:
        otp_store.pop(f"reset_{req.email}", None)
        raise HTTPException(400, "OTP expired. Request a new one.")

    if req.otp != otp:
        raise HTTPException(400, "Invalid OTP")

    users = db.query(User).all()
    user = next((u for u in users if decrypt(u.email_encrypted) == req.email), None)
    if not user:
        raise HTTPException(404, "User not found")

    user.password_hash = hash_password(req.new_password)
    db.commit()
    otp_store.pop(f"reset_{req.email}", None)

    return {"message": "Password reset successfully. You can now login."}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id":    current_user.id,
        "name":  current_user.name,
        "email": decrypt(current_user.email_encrypted),
    }