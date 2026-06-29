from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models import Ban
from schemas.schemas import BanSchema

router = APIRouter(prefix="/api/tables", tags=["Tables"])


@router.get("/", response_model=List[BanSchema])
def get_all_tables(db: Session = Depends(get_db)):
    return db.query(Ban).all()


@router.get("/{id_ban}", response_model=BanSchema)
def get_table(id_ban: int, db: Session = Depends(get_db)):
    ban = db.query(Ban).filter(Ban.ID_Ban == id_ban).first()
    if not ban:
        raise HTTPException(status_code=404, detail="Bàn không tồn tại")
    return ban


@router.get("/qr/{ma_qr}", response_model=BanSchema)
def get_table_by_qr(ma_qr: str, db: Session = Depends(get_db)):
    ban = db.query(Ban).filter(Ban.Ma_QR_Code == ma_qr).first()
    if not ban:
        raise HTTPException(status_code=404, detail="Mã QR không hợp lệ")
    return ban
