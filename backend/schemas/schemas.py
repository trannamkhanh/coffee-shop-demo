from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class BanSchema(BaseModel):
    ID_Ban: Optional[int] = None
    TenBan: str
    TrangThai: str = "Trong"
    Ma_QR_Code: str

    class Config:
        from_attributes = True


class MonAnSchema(BaseModel):
    ID_Mon: Optional[int] = None
    TenMon: str
    Gia: Decimal
    GiamGia: Decimal = Decimal("0")
    HinhAnh: Optional[str] = None
    DanhMuc: str
    TrangThai: str = "ConHang"

    class Config:
        from_attributes = True


class MonAnCreate(BaseModel):
    TenMon: str
    Gia: Decimal
    GiamGia: Decimal = Decimal("0")
    HinhAnh: Optional[str] = None
    DanhMuc: str
    TrangThai: str = "ConHang"


class NhanVienSchema(BaseModel):
    ID_NhanVien: Optional[int] = None
    HoTen: str
    TenDangNhap: str
    ChucVu: str = "PhucVu"

    class Config:
        from_attributes = True


class NhanVienCreate(BaseModel):
    HoTen: str
    TenDangNhap: str
    MatKhau: str
    ChucVu: str = "PhucVu"


class ChiTietHoaDonSchema(BaseModel):
    ID_ChiTiet: Optional[int] = None
    ID_HoaDon: Optional[int] = None
    ID_Mon: int
    SoLuong: int
    GiaTaiThoiDiem: Decimal

    class Config:
        from_attributes = True


class HoaDonSchema(BaseModel):
    ID_HoaDon: Optional[int] = None
    ID_Ban: int
    ThoiGianTao: Optional[datetime] = None
    TongTien: Decimal = Decimal("0")
    TrangThaiThanhToan: str = "ChuaThanhToan"
    chi_tiet: List[ChiTietHoaDonSchema] = []

    class Config:
        from_attributes = True


class DatMonRequest(BaseModel):
    ID_Ban: int
    danh_sach_mon: List[ChiTietHoaDonSchema]


class DatMonResponse(BaseModel):
    message: str
    ID_HoaDon: int
    is_new: bool
