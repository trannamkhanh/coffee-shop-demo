from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from config.database import get_db
from models import HoaDon, Ban, ChiTietHoaDon, MonAn
from schemas.schemas import HoaDonSchema
from services.order_service import thanh_toan_hoa_don
from routers.auth import get_current_user, require_role
from models import NhanVien

router = APIRouter(prefix="/api/cashier", tags=["Cashier"])


@router.get("/hoa-don-chua-thanh-toan")
def get_unpaid_invoices(
    db: Session = Depends(get_db),
    current_user: NhanVien = Depends(require_role("Admin", "ThuNgan")),
):
    hoa_dons = (
        db.query(HoaDon)
        .options(joinedload(HoaDon.ban), joinedload(HoaDon.chi_tiet).joinedload(ChiTietHoaDon.mon_an))
        .filter(HoaDon.TrangThaiThanhToan == "ChuaThanhToan")
        .order_by(HoaDon.ThoiGianTao.desc())
        .all()
    )

    result = []
    for hd in hoa_dons:
        items = []
        for ct in hd.chi_tiet:
            items.append({
                "ID_ChiTiet": ct.ID_ChiTiet,
                "TenMon": ct.mon_an.TenMon if ct.mon_an else "N/A",
                "SoLuong": ct.SoLuong,
                "GiaTaiThoiDiem": float(ct.GiaTaiThoiDiem),
                "ThanhTien": float(ct.GiaTaiThoiDiem * ct.SoLuong),
            })

        result.append({
            "ID_HoaDon": hd.ID_HoaDon,
            "TenBan": hd.ban.TenBan if hd.ban else "N/A",
            "ID_Ban": hd.ID_Ban,
            "ThoiGianTao": hd.ThoiGianTao.isoformat() if hd.ThoiGianTao else "",
            "TongTien": float(hd.TongTien),
            "chi_tiet": items,
        })

    return result


@router.get("/ban-co-khach")
def get_occupied_tables(
    db: Session = Depends(get_db),
    current_user: NhanVien = Depends(require_role("Admin", "ThuNgan")),
):
    bans = db.query(Ban).filter(Ban.TrangThai == "CoKhach").all()
    return [
        {
            "ID_Ban": b.ID_Ban,
            "TenBan": b.TenBan,
            "Ma_QR_Code": b.Ma_QR_Code,
        }
        for b in bans
    ]


@router.get("/ban/{id_ban}/hoa-don-chi-tiet")
def get_table_invoice_detail(
    id_ban: int,
    db: Session = Depends(get_db),
    current_user: NhanVien = Depends(require_role("Admin", "ThuNgan")),
):
    hoa_don = (
        db.query(HoaDon)
        .options(joinedload(HoaDon.chi_tiet).joinedload(ChiTietHoaDon.mon_an))
        .filter(
            HoaDon.ID_Ban == id_ban,
            HoaDon.TrangThaiThanhToan == "ChuaThanhToan",
        )
        .first()
    )
    if not hoa_don:
        raise HTTPException(status_code=404, detail="Bàn này không có hóa đơn đang mở")

    items = []
    for ct in hoa_don.chi_tiet:
        items.append({
            "ID_ChiTiet": ct.ID_ChiTiet,
            "TenMon": ct.mon_an.TenMon if ct.mon_an else "N/A",
            "SoLuong": ct.SoLuong,
            "GiaTaiThoiDiem": float(ct.GiaTaiThoiDiem),
            "ThanhTien": float(ct.GiaTaiThoiDiem * ct.SoLuong),
        })

    return {
        "ID_HoaDon": hoa_don.ID_HoaDon,
        "ThoiGianTao": hoa_don.ThoiGianTao.isoformat() if hoa_don.ThoiGianTao else "",
        "TongTien": float(hoa_don.TongTien),
        "chi_tiet": items,
    }


@router.post("/thanh-toan/{id_hoa_don}")
def cashier_payment(
    id_hoa_don: int,
    db: Session = Depends(get_db),
    current_user: NhanVien = Depends(require_role("Admin", "ThuNgan")),
):
    try:
        hoa_don = thanh_toan_hoa_don(id_hoa_don, db)
        return {
            "message": "Thanh toán thành công!",
            "ID_HoaDon": hoa_don.ID_HoaDon,
            "TongTien": float(hoa_don.TongTien),
            "NhanVien": current_user.HoTen,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
