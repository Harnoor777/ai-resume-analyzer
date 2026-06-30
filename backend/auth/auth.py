import os, random, string, smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from jose import JWTError, jwt
import bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

load_dotenv()

SECRET_KEY     = os.getenv("SECRET_KEY", "changeme-use-a-long-random-string")
ALGORITHM      = "HS256"
ACCESS_EXPIRE  = 30
REFRESH_EXPIRE = 7 * 24 * 60
AES_KEY        = os.getenv("AES_KEY", "0123456789abcdef").encode()[:32].ljust(32, b'0')

MAIL_USERNAME  = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD  = os.getenv("MAIL_PASSWORD")
MAIL_FROM      = os.getenv("MAIL_FROM")
MAIL_SERVER    = "smtp.gmail.com"
MAIL_PORT      = 587

def hash_password(password: str) -> str:
    # Use bcrypt directly (Python 3.13 compatible)
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    # Use bcrypt directly for verification
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False

def encrypt(text: str) -> str:
    if not text: return ""
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    ct = cipher.encrypt(pad(text.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct).decode()

def decrypt(token: str) -> str:
    if not token: return ""
    try:
        raw    = base64.b64decode(token)
        iv     = raw[:16]
        ct     = raw[16:]
        cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ct), AES.block_size).decode()
    except:
        return token

def create_token(data: dict, expires_minutes: int) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(user_id: int, email: str) -> str:
    return create_token({"sub": str(user_id), "email": email, "type": "access"}, ACCESS_EXPIRE)

def create_refresh_token(user_id: int) -> str:
    return create_token({"sub": str(user_id), "type": "refresh"}, REFRESH_EXPIRE)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(to_email: str, otp: str, name: str = "") -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your ResumeMatch account"
    msg["From"]    = MAIL_FROM
    msg["To"]      = to_email

    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:480px;margin:0 auto;padding:40px 24px;background:#141210;color:#F0EDE8;border-radius:16px">
      <h2 style="color:#E07A45;margin-bottom:8px">ResumeMatch</h2>
      <p style="color:#8A857E;margin-bottom:24px">Hi {name or 'there'}, verify your email to get started.</p>
      <div style="background:#1E1B18;border-radius:12px;padding:24px;text-align:center;margin-bottom:24px">
        <p style="color:#8A857E;font-size:13px;margin-bottom:8px">Your verification code</p>
        <div style="font-size:36px;font-weight:900;letter-spacing:8px;color:#E07A45">{otp}</div>
        <p style="color:#8A857E;font-size:12px;margin-top:8px">Expires in 10 minutes</p>
      </div>
      <p style="color:#8A857E;font-size:12px">If you didn't create an account, ignore this email.</p>
    </div>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False