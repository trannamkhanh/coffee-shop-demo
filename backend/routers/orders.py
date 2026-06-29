from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.schemas import DatMonRequest, DatMonResponse, HoaDonSchema
from services.order_service import dat_mon_qua_qr, thanh_toan_hoa_don
from models import HoaDon, ChiTietHoaDon

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("/dat-mon", response_model=DatMonResponse)
def create_order(request: DatMonRequest, db: Session = Depends(get_db)):
    try:
        result = dat_mon_qua_qr(request, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/hoa-don/{id_hoa_don}", response_model=HoaDonSchema)
def get_hoa_don(id_hoa_don: int, db: Session = Depends(get_db)):
    hoa_don = db.query(HoaDon).filter(HoaDon.ID_HoaDon == id_hoa_don).first()
    if not hoa_don:
        raise HTTPException(status_code=404, detail="Hóa đơn không tồn tại")
    return hoa_don


@router.get("/ban/{id_ban}/hoa-don-dang-mo", response_model=HoaDonSchema)
def get_hoa_don_dang_mo(id_ban: int, db: Session = Depends(get_db)):
    hoa_don = (
        db.query(HoaDon)
        .filter(
            HoaDon.ID_Ban == id_ban,
            HoaDon.TrangThaiThanhToan == "ChuaThanhToan",
        )
        .first()
    )
    if not hoa_don:
        raise HTTPException(status_code=404, detail="Không có hóa đơn đang mở cho bàn này")
    return hoa_don


@router.post("/thanh-toan/{id_hoa_don}")
def payment(id_hoa_don: int, db: Session = Depends(get_db)):
    try:
        hoa_don = thanh_toan_hoa_don(id_hoa_don, db)
        return {
            "message": "Thanh toán thành công!",
            "ID_HoaDon": hoa_don.ID_HoaDon,
            "TongTien": float(hoa_don.TongTien),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
