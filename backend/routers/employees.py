from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext
from config.database import get_db
from models import NhanVien
from schemas.schemas import NhanVienSchema, NhanVienCreate
from routers.auth import require_role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.get("/", response_model=List[NhanVienSchema])
def get_all_employees(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Admin")),
):
    return db.query(NhanVien).all()


@router.post("/", response_model=NhanVienSchema)
def create_employee(
    emp: NhanVienCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Admin")),
):
    existing = (
        db.query(NhanVien)
        .filter(NhanVien.TenDangNhap == emp.TenDangNhap)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")

    new_emp = NhanVien(
        HoTen=emp.HoTen,
        TenDangNhap=emp.TenDangNhap,
        MatKhau=pwd_context.hash(emp.MatKhau),
        ChucVu=emp.ChucVu,
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp
