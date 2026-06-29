from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from models import Ban, MonAn, HoaDon, ChiTietHoaDon
from schemas.schemas import DatMonRequest, DatMonResponse, ChiTietHoaDonSchema


def dat_mon_qua_qr(request: DatMonRequest, db: Session) -> DatMonResponse:
    ban = db.query(Ban).filter(Ban.ID_Ban == request.ID_Ban).first()
    if not ban:
        raise ValueError(f"Bàn ID {request.ID_Ban} không tồn tại")

    hoa_don_hien_tai = (
        db.query(HoaDon)
        .filter(
            HoaDon.ID_Ban == request.ID_Ban,
            HoaDon.TrangThaiThanhToan == "ChuaThanhToan",
        )
        .first()
    )

    is_new = False
    if not hoa_don_hien_tai:
        hoa_don_hien_tai = HoaDon(
            ID_Ban=request.ID_Ban,
            ThoiGianTao=datetime.now(),
            TongTien=Decimal("0"),
            TrangThaiThanhToan="ChuaThanhToan",
        )
        db.add(hoa_don_hien_tai)
        db.flush()
        is_new = True

    tong_tien = Decimal("0")

    for item in request.danh_sach_mon:
        mon_an = db.query(MonAn).filter(MonAn.ID_Mon == item.ID_Mon).first()
        if not mon_an:
            continue
        if mon_an.TrangThai == "HetHang":
            continue

        gia_sau_giam = mon_an.Gia * (1 - mon_an.GiamGia / Decimal("100"))
        thanh_tien = gia_sau_giam * item.SoLuong

        chi_tiet = ChiTietHoaDon(
            ID_HoaDon=hoa_don_hien_tai.ID_HoaDon,
            ID_Mon=item.ID_Mon,
            SoLuong=item.SoLuong,
            GiaTaiThoiDiem=gia_sau_giam,
        )
        db.add(chi_tiet)
        tong_tien += thanh_tien

    hoa_don_hien_tai.TongTien += tong_tien

    if ban.TrangThai == "Trong":
        ban.TrangThai = "CoKhach"

    db.commit()
    db.refresh(hoa_don_hien_tai)

    return DatMonResponse(
        message="Đặt món thành công!",
        ID_HoaDon=hoa_don_hien_tai.ID_HoaDon,
        is_new=is_new,
    )


def thanh_toan_hoa_don(id_hoa_don: int, db: Session):
    hoa_don = (
        db.query(HoaDon)
        .filter(
            HoaDon.ID_HoaDon == id_hoa_don,
            HoaDon.TrangThaiThanhToan == "ChuaThanhToan",
        )
        .first()
    )
    if not hoa_don:
        raise ValueError("Hóa đơn không tồn tại hoặc đã thanh toán")

    hoa_don.TrangThaiThanhToan = "DaThanhToan"

    ban = db.query(Ban).filter(Ban.ID_Ban == hoa_don.ID_Ban).first()
    if ban:
        ban.TrangThai = "Trong"

    db.commit()
    return hoa_don
