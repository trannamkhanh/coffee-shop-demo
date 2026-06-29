import os
import socket

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import menu, tables, employees, orders, auth, cashier
from config.database import Base, engine, SessionLocal, DATABASE_URL

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
from models import Ban, MonAn, NhanVien, HoaDon, ChiTietHoaDon
from passlib.context import CryptContext

app = FastAPI(
    title="CoffeeShop Management API",
    description="API quản lý quán cà phê - Đặt món qua QR, quản lý bàn, menu, nhân viên",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(menu.router)
app.include_router(tables.router)
app.include_router(employees.router)
app.include_router(orders.router)
app.include_router(auth.router)
app.include_router(cashier.router)

if os.path.isdir(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/api/system/public-url")
def get_public_url():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    if local_ip.startswith("127."):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.connect(("8.8.8.8", 80))
                local_ip = sock.getsockname()[0]
            except OSError:
                local_ip = "127.0.0.1"

    return {
        "base_url": f"http://{local_ip}:8000",
        "frontend_url": f"http://{local_ip}:8000/frontend/guest/menu.html",
    }


@app.get("/")
def root():
    return {"message": "CoffeeShop API is running"}


def seed_sqlite_demo_data():
    if not DATABASE_URL.startswith("sqlite"):
        return

    db = SessionLocal()
    try:
        if db.query(Ban).first():
            return

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        bans = [
            Ban(TenBan="B01", TrangThai="Trong", Ma_QR_Code="table_B01"),
            Ban(TenBan="B02", TrangThai="Trong", Ma_QR_Code="table_B02"),
            Ban(TenBan="B03", TrangThai="Trong", Ma_QR_Code="table_B03"),
            Ban(TenBan="B04", TrangThai="Trong", Ma_QR_Code="table_B04"),
            Ban(TenBan="B05", TrangThai="Trong", Ma_QR_Code="table_B05"),
        ]

        menu_items = [
            MonAn(TenMon="Cà phê đen", Gia=25000, DanhMuc="Cà phê", TrangThai="ConHang", HinhAnh="/images/cafe-den.jpg"),
            MonAn(TenMon="Cà phê sữa", Gia=30000, DanhMuc="Cà phê", TrangThai="ConHang", HinhAnh="/images/cafe-sua.jpg"),
            MonAn(TenMon="Bạc xỉu", Gia=30000, DanhMuc="Cà phê", TrangThai="ConHang", HinhAnh="/images/bac-xiu.jpg"),
            MonAn(TenMon="Trà đào", Gia=35000, DanhMuc="Trà", TrangThai="ConHang", HinhAnh="/images/tra-dao.jpg"),
            MonAn(TenMon="Trà chanh", Gia=25000, DanhMuc="Trà", TrangThai="ConHang", HinhAnh="/images/tra-chanh.jpg"),
            MonAn(TenMon="Sinh tố bơ", Gia=40000, DanhMuc="Sinh tố", TrangThai="ConHang", HinhAnh="/images/sinh-to-bo.jpg"),
            MonAn(TenMon="Nước cam", Gia=30000, DanhMuc="Nước ép", TrangThai="ConHang", HinhAnh="/images/nuoc-cam.jpg"),
            MonAn(TenMon="Cacao nóng", Gia=25000, DanhMuc="Sô-cô-la", TrangThai="ConHang", HinhAnh="/images/cacao-nong.jpg"),
        ]

        employees = [
            NhanVien(
                HoTen="Admin",
                TenDangNhap="admin",
                MatKhau=pwd_context.hash("123456"),
                ChucVu="Admin",
            ),
            NhanVien(
                HoTen="Thu ngân 1",
                TenDangNhap="thungan1",
                MatKhau=pwd_context.hash("123456"),
                ChucVu="ThuNgan",
            ),
        ]

        db.add_all(bans + menu_items + employees)
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_sqlite_demo_data()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
