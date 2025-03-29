from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from models.tipo_movimiento import TipoMovimiento as TipoMovimientoModel
from schemas.tipo_movimiento import TipoMovimientoCreate, TipoMovimientoResponse, TipoMovimientoUpdate
from utils.auth import get_current_active_user
from models.user import User as UserModel

router = APIRouter(prefix="/tipos-movimiento", tags=["tipos-movimiento"])

@router.post("/", response_model=TipoMovimientoResponse)
async def create_tipo_movimiento(
    tipo_movimiento: TipoMovimientoCreate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    # Verificar que no exista otro tipo con el mismo código o nombre
    codigo_exists = db.query(TipoMovimientoModel).filter(TipoMovimientoModel.codigo == tipo_movimiento.codigo).first()
    if codigo_exists:
        raise HTTPException(status_code=400, detail="Ya existe un tipo de movimiento con ese código")
    
    nombre_exists = db.query(TipoMovimientoModel).filter(TipoMovimientoModel.nombre == tipo_movimiento.nombre).first()
    if nombre_exists:
        raise HTTPException(status_code=400, detail="Ya existe un tipo de movimiento con ese nombre")
    
    db_tipo_movimiento = TipoMovimientoModel(**tipo_movimiento.model_dump())
    db.add(db_tipo_movimiento)
    db.commit()
    db.refresh(db_tipo_movimiento)
    return db_tipo_movimiento

@router.get("/", response_model=List[TipoMovimientoResponse])
async def read_tipos_movimiento(
    skip: int = 0, 
    limit: int = 100, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    tipos_movimiento = db.query(TipoMovimientoModel).offset(skip).limit(limit).all()
    return tipos_movimiento

@router.get("/{tipo_movimiento_id}", response_model=TipoMovimientoResponse)
async def read_tipo_movimiento(
    tipo_movimiento_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_tipo_movimiento = db.query(TipoMovimientoModel).filter(TipoMovimientoModel.id == tipo_movimiento_id).first()
    if db_tipo_movimiento is None:
        raise HTTPException(status_code=404, detail="Tipo de movimiento no encontrado")
    return db_tipo_movimiento

@router.put("/{tipo_movimiento_id}", response_model=TipoMovimientoResponse)
async def update_tipo_movimiento(
    tipo_movimiento_id: int, 
    tipo_movimiento: TipoMovimientoUpdate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_tipo_movimiento = db.query(TipoMovimientoModel).filter(TipoMovimientoModel.id == tipo_movimiento_id).first()
    if db_tipo_movimiento is None:
        raise HTTPException(status_code=404, detail="Tipo de movimiento no encontrado")
    
    # Verificar que no exista otro tipo con el mismo código o nombre
    if tipo_movimiento.codigo and tipo_movimiento.codigo != db_tipo_movimiento.codigo:
        codigo_exists = db.query(TipoMovimientoModel).filter(
            TipoMovimientoModel.codigo == tipo_movimiento.codigo
        ).first()
        if codigo_exists:
            raise HTTPException(status_code=400, detail="Ya existe un tipo de movimiento con ese código")
    
    if tipo_movimiento.nombre and tipo_movimiento.nombre != db_tipo_movimiento.nombre:
        nombre_exists = db.query(TipoMovimientoModel).filter(
            TipoMovimientoModel.nombre == tipo_movimiento.nombre
        ).first()
        if nombre_exists:
            raise HTTPException(status_code=400, detail="Ya existe un tipo de movimiento con ese nombre")
    
    # Actualizar solo los campos proporcionados
    tipo_movimiento_data = tipo_movimiento.model_dump(exclude_unset=True)
    for key, value in tipo_movimiento_data.items():
        setattr(db_tipo_movimiento, key, value)
    
    db.commit()
    db.refresh(db_tipo_movimiento)
    return db_tipo_movimiento

@router.delete("/{tipo_movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tipo_movimiento(
    tipo_movimiento_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_tipo_movimiento = db.query(TipoMovimientoModel).filter(TipoMovimientoModel.id == tipo_movimiento_id).first()
    if db_tipo_movimiento is None:
        raise HTTPException(status_code=404, detail="Tipo de movimiento no encontrado")
    
    # Verificar si hay movimientos asociados antes de eliminar
    if db_tipo_movimiento.movimientos:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar el tipo de movimiento porque tiene movimientos asociados"
        )
    
    db.delete(db_tipo_movimiento)
    db.commit()
    return None 