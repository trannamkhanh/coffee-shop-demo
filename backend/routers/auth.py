from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from config.database import get_db
from models import NhanVien

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in .env file")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
router = APIRouter(prefix="/api/auth", tags=["Auth"])


class Token(BaseModel):
    access_token: str
    token_type: str
    chuc_vu: str
    ho_ten: str


class TokenData(BaseModel):
    username: Optional[str] = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(NhanVien).filter(NhanVien.TenDangNhap == username).first()
    if user is None:
        raise credentials_exception
    return user


def require_role(*roles: str):
    def role_checker(current_user: NhanVien = Depends(get_current_user)):
        if current_user.ChucVu not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yêu cầu quyền: {', '.join(roles)}",
            )
        return current_user

    return role_checker


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(NhanVien).filter(NhanVien.TenDangNhap == form_data.username).first()
    if not user or not verify_password(form_data.password, user.MatKhau):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
        )

    access_token = create_access_token(data={"sub": user.TenDangNhap, "chuc_vu": user.ChucVu})
    return Token(
        access_token=access_token,
        token_type="bearer",
        chuc_vu=user.ChucVu,
        ho_ten=user.HoTen,
    )


@router.get("/me")
def get_me(current_user: NhanVien = Depends(get_current_user)):
    return {
        "ID_NhanVien": current_user.ID_NhanVien,
        "HoTen": current_user.HoTen,
        "TenDangNhap": current_user.TenDangNhap,
        "ChucVu": current_user.ChucVu,
    }
