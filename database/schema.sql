-- ============================================================
-- COFFEE SHOP MANAGEMENT SYSTEM - SQL Server Schema
-- ============================================================

CREATE DATABASE CoffeeShopDB
GO

USE CoffeeShopDB
GO

-- ============================================================
-- 1. BAN (Tables)
-- ============================================================
CREATE TABLE Ban (
    ID_Ban INT IDENTITY(1,1) PRIMARY KEY,
    TenBan NVARCHAR(10) NOT NULL,
    TrangThai NVARCHAR(20) NOT NULL DEFAULT N'Trong'
        CHECK (TrangThai IN (N'Trong', N'CoKhach')),
    Ma_QR_Code NVARCHAR(100) NOT NULL UNIQUE
)
GO

-- ============================================================
-- 2. MONAN (Menu Items)
-- ============================================================
CREATE TABLE MonAn (
    ID_Mon INT IDENTITY(1,1) PRIMARY KEY,
    TenMon NVARCHAR(100) NOT NULL,
    Gia DECIMAL(18,0) NOT NULL CHECK (Gia >= 0),
    GiamGia DECIMAL(5,2) NOT NULL DEFAULT 0 CHECK (GiamGia >= 0 AND GiamGia <= 100),
    HinhAnh NVARCHAR(500),
    DanhMuc NVARCHAR(50) NOT NULL,
    TrangThai NVARCHAR(20) NOT NULL DEFAULT N'ConHang'
        CHECK (TrangThai IN (N'ConHang', N'HetHang'))
)
GO

-- ============================================================
-- 3. NHANVIEN (Employees / Users)
-- ============================================================
CREATE TABLE NhanVien (
    ID_NhanVien INT IDENTITY(1,1) PRIMARY KEY,
    HoTen NVARCHAR(100) NOT NULL,
    TenDangNhap NVARCHAR(50) NOT NULL UNIQUE,
    MatKhau NVARCHAR(255) NOT NULL,
    ChucVu NVARCHAR(20) NOT NULL DEFAULT N'PhucVu'
        CHECK (ChucVu IN (N'Admin', N'ThuNgan', N'PhucVu'))
)
GO

-- ============================================================
-- 4. HOADON (Orders / Invoices)
-- ============================================================
CREATE TABLE HoaDon (
    ID_HoaDon INT IDENTITY(1,1) PRIMARY KEY,
    ID_Ban INT NOT NULL,
    ThoiGianTao DATETIME NOT NULL DEFAULT GETDATE(),
    TongTien DECIMAL(18,0) NOT NULL DEFAULT 0,
    TrangThaiThanhToan NVARCHAR(20) NOT NULL DEFAULT N'ChuaThanhToan'
        CHECK (TrangThaiThanhToan IN (N'ChuaThanhToan', N'DaThanhToan')),
    CONSTRAINT FK_HoaDon_Ban FOREIGN KEY (ID_Ban) REFERENCES Ban(ID_Ban)
)
GO

-- ============================================================
-- 5. CHITIETHOADON (Order Details / Line Items)
-- ============================================================
CREATE TABLE ChiTietHoaDon (
    ID_ChiTiet INT IDENTITY(1,1) PRIMARY KEY,
    ID_HoaDon INT NOT NULL,
    ID_Mon INT NOT NULL,
    SoLuong INT NOT NULL CHECK (SoLuong > 0),
    GiaTaiThoiDiem DECIMAL(18,0) NOT NULL CHECK (GiaTaiThoiDiem >= 0),
    CONSTRAINT FK_CTHD_HoaDon FOREIGN KEY (ID_HoaDon) REFERENCES HoaDon(ID_HoaDon)
        ON DELETE CASCADE,
    CONSTRAINT FK_CTHD_MonAn FOREIGN KEY (ID_Mon) REFERENCES MonAn(ID_Mon)
)
GO

-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX IX_HoaDon_ID_Ban ON HoaDon(ID_Ban)
CREATE INDEX IX_HoaDon_TrangThai ON HoaDon(TrangThaiThanhToan)
CREATE INDEX IX_ChiTietHoaDon_ID_HoaDon ON ChiTietHoaDon(ID_HoaDon)

-- ============================================================
-- SAMPLE DATA
-- ============================================================
INSERT INTO Ban (TenBan, TrangThai, Ma_QR_Code) VALUES
(N'B01', N'Trong', 'table_B01'),
(N'B02', N'Trong', 'table_B02'),
(N'B03', N'Trong', 'table_B03'),
(N'B04', N'Trong', 'table_B04'),
(N'B05', N'Trong', 'table_B05')

INSERT INTO MonAn (TenMon, Gia, HinhAnh, DanhMuc, TrangThai) VALUES
(N'Cà phê đen', 25000, '/images/cafe-den.jpg', N'Cà phê', N'ConHang'),
(N'Cà phê sữa', 30000, '/images/cafe-sua.jpg', N'Cà phê', N'ConHang'),
(N'Bạc xỉu', 30000, '/images/bac-xiu.jpg', N'Cà phê', N'ConHang'),
(N'Trà đào', 35000, '/images/tra-dao.jpg', N'Trà', N'ConHang'),
(N'Trà chanh', 25000, '/images/tra-chanh.jpg', N'Trà', N'ConHang'),
(N'Sinh tố bơ', 40000, '/images/sinh-to-bo.jpg', N'Sinh tố', N'ConHang'),
(N'Nước cam', 30000, '/images/nuoc-cam.jpg', N'Nước ép', N'ConHang'),
(N'Cacao nóng', 25000, '/images/cacao-nong.jpg', N'Sô-cô-la', N'ConHang')

INSERT INTO NhanVien (HoTen, TenDangNhap, MatKhau, ChucVu) VALUES
(N'Admin', 'admin', '$2b$12$LJ3m4ys3Lk0TSw.H.jqOjO/R0Y0p7E0eE0eE0eE0eE0eE0eE0e', N'Admin'),
(N'Thu ngân 1', 'thungan1', '$2b$12$LJ3m4ys3Lk0TSw.H.jqOjO/R0Y0p7E0eE0eE0eE0eE0eE0eE0e', N'ThuNgan')
GO
