from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models import MonAn
from schemas.schemas import MonAnSchema, MonAnCreate
from routers.auth import require_role

router = APIRouter(prefix="/api/menu", tags=["Menu"])


@router.get("/", response_model=List[MonAnSchema])
def get_all_menu(db: Session = Depends(get_db)):
    return db.query(MonAn).all()


@router.get("/{id_mon}", response_model=MonAnSchema)
def get_mon(id_mon: int, db: Session = Depends(get_db)):
    mon = db.query(MonAn).filter(MonAn.ID_Mon == id_mon).first()
    if not mon:
        raise HTTPException(status_code=404, detail="Món không tồn tại")
    return mon


@router.post("/", response_model=MonAnSchema)
def create_mon(
    mon: MonAnCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Admin")),
):
    new_mon = MonAn(**mon.model_dump())
    db.add(new_mon)
    db.commit()
    db.refresh(new_mon)
    return new_mon


@router.put("/{id_mon}", response_model=MonAnSchema)
def update_mon(
    id_mon: int,
    mon: MonAnCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Admin")),
):
    existing = db.query(MonAn).filter(MonAn.ID_Mon == id_mon).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Món không tồn tại")
    for key, value in mon.model_dump().items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{id_mon}")
def delete_mon(
    id_mon: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Admin")),
):
    existing = db.query(MonAn).filter(MonAn.ID_Mon == id_mon).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Món không tồn tại")
    db.delete(existing)
    db.commit()
    return {"message": "Xóa món thành công"}
