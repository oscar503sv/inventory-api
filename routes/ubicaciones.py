from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from models.ubicacion import Ubicacion as UbicacionModel
from schemas.ubicacion import UbicacionCreate, UbicacionResponse, UbicacionUpdate
from utils.auth import get_current_active_user
from models.user import User as UserModel

router = APIRouter(prefix="/ubicaciones", tags=["ubicaciones"])

@router.post("/", response_model=UbicacionResponse)
async def create_ubicacion(
    ubicacion: UbicacionCreate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_ubicacion = db.query(UbicacionModel).filter(UbicacionModel.nombre == ubicacion.nombre).first()
    if db_ubicacion:
        raise HTTPException(status_code=400, detail="Ya existe una ubicación con ese nombre")
    
    db_ubicacion = UbicacionModel(**ubicacion.model_dump())
    db.add(db_ubicacion)
    db.commit()
    db.refresh(db_ubicacion)
    return db_ubicacion

@router.get("/", response_model=List[UbicacionResponse])
async def read_ubicaciones(
    skip: int = 0, 
    limit: int = 100, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    ubicaciones = db.query(UbicacionModel).offset(skip).limit(limit).all()
    return ubicaciones

@router.get("/{ubicacion_id}", response_model=UbicacionResponse)
async def read_ubicacion(
    ubicacion_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_ubicacion = db.query(UbicacionModel).filter(UbicacionModel.id == ubicacion_id).first()
    if db_ubicacion is None:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return db_ubicacion

@router.put("/{ubicacion_id}", response_model=UbicacionResponse)
async def update_ubicacion(
    ubicacion_id: int, 
    ubicacion: UbicacionUpdate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_ubicacion = db.query(UbicacionModel).filter(UbicacionModel.id == ubicacion_id).first()
    if db_ubicacion is None:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    
    # Verificar que no exista otra ubicación con el mismo nombre
    if ubicacion.nombre and ubicacion.nombre != db_ubicacion.nombre:
        nombre_exists = db.query(UbicacionModel).filter(UbicacionModel.nombre == ubicacion.nombre).first()
        if nombre_exists:
            raise HTTPException(status_code=400, detail="Ya existe una ubicación con ese nombre")
    
    # Actualizar solo los campos proporcionados
    ubicacion_data = ubicacion.model_dump(exclude_unset=True)
    for key, value in ubicacion_data.items():
        setattr(db_ubicacion, key, value)
    
    db.commit()
    db.refresh(db_ubicacion)
    return db_ubicacion

@router.delete("/{ubicacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ubicacion(
    ubicacion_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_ubicacion = db.query(UbicacionModel).filter(UbicacionModel.id == ubicacion_id).first()
    if db_ubicacion is None:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    
    # Verificar si hay stocks o movimientos asociados antes de eliminar
    if db_ubicacion.stocks:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar la ubicación porque tiene stock asociado"
        )
    
    if db_ubicacion.movimientos_origen or db_ubicacion.movimientos_destino:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar la ubicación porque tiene movimientos de inventario asociados"
        )
    
    db.delete(db_ubicacion)
    db.commit()
    return None 