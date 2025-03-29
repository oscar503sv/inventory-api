from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from models.categoria import Categoria as CategoriaModel
from schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate
from utils.auth import get_current_active_user
from models.user import User as UserModel

router = APIRouter(prefix="/categorias", tags=["categorias"])

@router.post("/", response_model=CategoriaResponse)
async def create_categoria(
    categoria: CategoriaCreate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_categoria = db.query(CategoriaModel).filter(CategoriaModel.nombre == categoria.nombre).first()
    if db_categoria:
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
    
    db_categoria = CategoriaModel(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@router.get("/", response_model=List[CategoriaResponse])
async def read_categorias(
    skip: int = 0, 
    limit: int = 100, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    categorias = db.query(CategoriaModel).offset(skip).limit(limit).all()
    return categorias

@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def read_categoria(
    categoria_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_categoria = db.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_categoria

@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def update_categoria(
    categoria_id: int, 
    categoria: CategoriaUpdate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_categoria = db.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar que no exista otra categoría con el mismo nombre
    if categoria.nombre and categoria.nombre != db_categoria.nombre:
        nombre_exists = db.query(CategoriaModel).filter(CategoriaModel.nombre == categoria.nombre).first()
        if nombre_exists:
            raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
    
    # Actualizar solo los campos proporcionados
    categoria_data = categoria.model_dump(exclude_unset=True)
    for key, value in categoria_data.items():
        setattr(db_categoria, key, value)
    
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(
    categoria_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_categoria = db.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar si hay productos asociados antes de eliminar
    if db_categoria.productos:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar la categoría porque tiene productos asociados"
        )
    
    db.delete(db_categoria)
    db.commit()
    return None 