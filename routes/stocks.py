from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

from config.database import get_db
from models.stock import Stock as StockModel
from models.producto import Producto as ProductoModel
from models.ubicacion import Ubicacion as UbicacionModel
from schemas.stock import StockCreate, StockResponse, StockUpdate, StockDetalleResponse
from utils.auth import get_current_active_user
from models.user import User as UserModel

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.post("/", response_model=StockResponse)
async def create_stock(
    stock: StockCreate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    # Verificar que exista el producto
    producto = db.query(ProductoModel).filter(ProductoModel.id == stock.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar que exista la ubicación
    ubicacion = db.query(UbicacionModel).filter(UbicacionModel.id == stock.ubicacion_id).first()
    if not ubicacion:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    
    # Verificar si ya existe un registro de stock para este producto y ubicación
    existing_stock = db.query(StockModel).filter(
        StockModel.producto_id == stock.producto_id,
        StockModel.ubicacion_id == stock.ubicacion_id
    ).first()
    
    if existing_stock:
        raise HTTPException(
            status_code=400, 
            detail="Ya existe un registro de stock para este producto en esta ubicación"
        )
    
    db_stock = StockModel(**stock.model_dump())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.get("/", response_model=List[StockDetalleResponse])
async def read_stocks(
    skip: int = 0, 
    limit: int = 100, 
    producto_id: int = None,
    ubicacion_id: int = None,
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    query = db.query(StockModel)
    
    # Filtrar por producto si se proporciona
    if producto_id:
        query = query.filter(StockModel.producto_id == producto_id)
    
    # Filtrar por ubicación si se proporciona
    if ubicacion_id:
        query = query.filter(StockModel.ubicacion_id == ubicacion_id)
    
    stocks = query.offset(skip).limit(limit).all()
    return stocks

@router.get("/{stock_id}", response_model=StockDetalleResponse)
async def read_stock(
    stock_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_stock = db.query(StockModel).filter(StockModel.id == stock_id).first()
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    return db_stock

@router.put("/{stock_id}", response_model=StockResponse)
async def update_stock(
    stock_id: int, 
    stock: StockUpdate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_stock = db.query(StockModel).filter(StockModel.id == stock_id).first()
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    
    # Si se está cambiando producto_id o ubicacion_id, verificar que no exista otro registro con la misma combinación
    if (stock.producto_id and stock.producto_id != db_stock.producto_id) or \
       (stock.ubicacion_id and stock.ubicacion_id != db_stock.ubicacion_id):
        
        new_producto_id = stock.producto_id if stock.producto_id else db_stock.producto_id
        new_ubicacion_id = stock.ubicacion_id if stock.ubicacion_id else db_stock.ubicacion_id
        
        existing_stock = db.query(StockModel).filter(
            StockModel.producto_id == new_producto_id,
            StockModel.ubicacion_id == new_ubicacion_id,
            StockModel.id != stock_id
        ).first()
        
        if existing_stock:
            raise HTTPException(
                status_code=400, 
                detail="Ya existe un registro de stock para este producto en esta ubicación"
            )
    
    # Actualizar solo los campos proporcionados
    stock_data = stock.model_dump(exclude_unset=True)
    for key, value in stock_data.items():
        setattr(db_stock, key, value)
    
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock(
    stock_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_stock = db.query(StockModel).filter(StockModel.id == stock_id).first()
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    
    db.delete(db_stock)
    db.commit()
    return None 