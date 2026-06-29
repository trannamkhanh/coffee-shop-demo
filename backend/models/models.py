from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base


class Ban(Base):
    __tablename__ = "Ban"

    ID_Ban = Column(Integer, primary_key=True, autoincrement=True)
    TenBan = Column(String(10), nullable=False)
    TrangThai = Column(String(20), nullable=False, default="Trong")
    Ma_QR_Code = Column(String(100), nullable=False, unique=True)

    hoa_dons = relationship("HoaDon", back_populates="ban")


class MonAn(Base):
    __tablename__ = "MonAn"

    ID_Mon = Column(Integer, primary_key=True, autoincrement=True)
    TenMon = Column(String(100), nullable=False)
    Gia = Column(Numeric(18, 0), nullable=False)
    GiamGia = Column(Numeric(5, 2), nullable=False, default=0)
    HinhAnh = Column(String(500))
    DanhMuc = Column(String(50), nullable=False)
    TrangThai = Column(String(20), nullable=False, default="ConHang")

    chi_tiet = relationship("ChiTietHoaDon", back_populates="mon_an")


class NhanVien(Base):
    __tablename__ = "NhanVien"

    ID_NhanVien = Column(Integer, primary_key=True, autoincrement=True)
    HoTen = Column(String(100), nullable=False)
    TenDangNhap = Column(String(50), nullable=False, unique=True)
    MatKhau = Column(String(255), nullable=False)
    ChucVu = Column(String(20), nullable=False, default="PhucVu")


class HoaDon(Base):
    __tablename__ = "HoaDon"

    ID_HoaDon = Column(Integer, primary_key=True, autoincrement=True)
    ID_Ban = Column(Integer, ForeignKey("Ban.ID_Ban"), nullable=False)
    ThoiGianTao = Column(DateTime, nullable=False, default=datetime.now)
    TongTien = Column(Numeric(18, 0), nullable=False, default=0)
    TrangThaiThanhToan = Column(String(20), nullable=False, default="ChuaThanhToan")

    ban = relationship("Ban", back_populates="hoa_dons")
    chi_tiet = relationship("ChiTietHoaDon", back_populates="hoa_don",
                            cascade="all, delete-orphan")


class ChiTietHoaDon(Base):
    __tablename__ = "ChiTietHoaDon"

    ID_ChiTiet = Column(Integer, primary_key=True, autoincrement=True)
    ID_HoaDon = Column(Integer, ForeignKey("HoaDon.ID_HoaDon"), nullable=False)
    ID_Mon = Column(Integer, ForeignKey("MonAn.ID_Mon"), nullable=False)
    SoLuong = Column(Integer, nullable=False)
    GiaTaiThoiDiem = Column(Numeric(18, 0), nullable=False)

    hoa_don = relationship("HoaDon", back_populates="chi_tiet")
    mon_an = relationship("MonAn", back_populates="chi_tiet")
