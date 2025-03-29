from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from models.proveedor import Proveedor as ProveedorModel
from schemas.proveedor import ProveedorCreate, ProveedorResponse, ProveedorUpdate
from utils.auth import get_current_active_user
from models.user import User as UserModel

router = APIRouter(prefix="/proveedores", tags=["proveedores"])

@router.post("/", response_model=ProveedorResponse)
async def create_proveedor(
    proveedor: ProveedorCreate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_proveedor = ProveedorModel(**proveedor.model_dump())
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

@router.get("/", response_model=List[ProveedorResponse])
async def read_proveedores(
    skip: int = 0, 
    limit: int = 100, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    proveedores = db.query(ProveedorModel).offset(skip).limit(limit).all()
    return proveedores

@router.get("/{proveedor_id}", response_model=ProveedorResponse)
async def read_proveedor(
    proveedor_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == proveedor_id).first()
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return db_proveedor

@router.put("/{proveedor_id}", response_model=ProveedorResponse)
async def update_proveedor(
    proveedor_id: int, 
    proveedor: ProveedorUpdate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == proveedor_id).first()
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Actualizar solo los campos proporcionados
    proveedor_data = proveedor.model_dump(exclude_unset=True)
    for key, value in proveedor_data.items():
        setattr(db_proveedor, key, value)
    
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proveedor(
    proveedor_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_proveedor = db.query(ProveedorModel).filter(ProveedorModel.id == proveedor_id).first()
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Verificar si hay productos asociados antes de eliminar
    if db_proveedor.productos:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar el proveedor porque tiene productos asociados"
        )
    
    db.delete(db_proveedor)
    db.commit()
    return None 