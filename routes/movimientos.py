from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from config.database import get_db
from models.movimiento_inventario import MovimientoInventario as MovimientoModel
from models.tipo_movimiento import TipoMovimiento as TipoMovimientoModel
from models.producto import Producto as ProductoModel
from models.ubicacion import Ubicacion as UbicacionModel
from models.stock import Stock as StockModel
from schemas.movimiento_inventario import MovimientoInventarioCreate, MovimientoInventarioResponse, MovimientoInventarioUpdate, MovimientoInventarioDetalleResponse
from utils.auth import get_current_active_user
from models.user import User as UserModel

router = APIRouter(prefix="/movimientos", tags=["movimientos"])

@router.post("/", response_model=MovimientoInventarioResponse)
async def create_movimiento(
    movimiento: MovimientoInventarioCreate, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    # Verificar que exista el producto
    producto = db.query(ProductoModel).filter(ProductoModel.id == movimiento.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar que exista el tipo de movimiento
    tipo_movimiento = db.query(TipoMovimientoModel).filter(TipoMovimientoModel.id == movimiento.tipo_movimiento_id).first()
    if not tipo_movimiento:
        raise HTTPException(status_code=404, detail="Tipo de movimiento no encontrado")
    
    # Verificar ubicaciones según el tipo de movimiento
    if tipo_movimiento.afecta_stock == "entrada" and not movimiento.ubicacion_destino_id:
        raise HTTPException(
            status_code=400, 
            detail="Para movimientos de entrada se requiere una ubicación de destino"
        )
    
    if tipo_movimiento.afecta_stock == "salida" and not movimiento.ubicacion_origen_id:
        raise HTTPException(
            status_code=400, 
            detail="Para movimientos de salida se requiere una ubicación de origen"
        )
    
    if tipo_movimiento.afecta_stock not in ["entrada", "salida", "ninguno"]:
        raise HTTPException(
            status_code=400, 
            detail="El tipo de movimiento debe afectar al stock como 'entrada', 'salida' o 'ninguno'"
        )
    
    # Verificar ubicaciones si se proporcionan
    if movimiento.ubicacion_origen_id:
        origen = db.query(UbicacionModel).filter(UbicacionModel.id == movimiento.ubicacion_origen_id).first()
        if not origen:
            raise HTTPException(status_code=404, detail="Ubicación de origen no encontrada")
    
    if movimiento.ubicacion_destino_id:
        destino = db.query(UbicacionModel).filter(UbicacionModel.id == movimiento.ubicacion_destino_id).first()
        if not destino:
            raise HTTPException(status_code=404, detail="Ubicación de destino no encontrada")
    
    # Verificar stock suficiente para movimientos de salida
    if tipo_movimiento.afecta_stock == "salida" and movimiento.ubicacion_origen_id:
        stock = db.query(StockModel).filter(
            StockModel.producto_id == movimiento.producto_id,
            StockModel.ubicacion_id == movimiento.ubicacion_origen_id
        ).first()
        
        if not stock or stock.cantidad < movimiento.cantidad:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente en la ubicación de origen. Disponible: {stock.cantidad if stock else 0}"
            )
    
    # Crear el movimiento
    db_movimiento = MovimientoModel(
        cantidad=movimiento.cantidad,
        tipo_movimiento_id=movimiento.tipo_movimiento_id,
        producto_id=movimiento.producto_id,
        ubicacion_origen_id=movimiento.ubicacion_origen_id,
        ubicacion_destino_id=movimiento.ubicacion_destino_id,
        referencia=movimiento.referencia,
        observaciones=movimiento.observaciones,
        usuario_id=current_user.id,
        fecha=datetime.now()
    )
    
    db.add(db_movimiento)
    
    # Actualizar el stock según el tipo de movimiento
    if tipo_movimiento.afecta_stock == "entrada" and movimiento.ubicacion_destino_id:
        # Buscar o crear el registro de stock en la ubicación de destino
        stock_destino = db.query(StockModel).filter(
            StockModel.producto_id == movimiento.producto_id,
            StockModel.ubicacion_id == movimiento.ubicacion_destino_id
        ).first()
        
        if stock_destino:
            stock_destino.cantidad += movimiento.cantidad
        else:
            nuevo_stock = StockModel(
                producto_id=movimiento.producto_id,
                ubicacion_id=movimiento.ubicacion_destino_id,
                cantidad=movimiento.cantidad
            )
            db.add(nuevo_stock)
    
    elif tipo_movimiento.afecta_stock == "salida" and movimiento.ubicacion_origen_id:
        # Actualizar el stock en la ubicación de origen
        stock_origen = db.query(StockModel).filter(
            StockModel.producto_id == movimiento.producto_id,
            StockModel.ubicacion_id == movimiento.ubicacion_origen_id
        ).first()
        
        stock_origen.cantidad -= movimiento.cantidad
    
    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento

@router.get("/", response_model=List[MovimientoInventarioDetalleResponse])
async def read_movimientos(
    skip: int = 0, 
    limit: int = 100,
    producto_id: Optional[int] = None,
    tipo_movimiento_id: Optional[int] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    query = db.query(MovimientoModel)
    
    # Aplicar filtros si se proporcionan
    if producto_id:
        query = query.filter(MovimientoModel.producto_id == producto_id)
    
    if tipo_movimiento_id:
        query = query.filter(MovimientoModel.tipo_movimiento_id == tipo_movimiento_id)
    
    if fecha_desde:
        query = query.filter(MovimientoModel.fecha >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(MovimientoModel.fecha <= fecha_hasta)
    
    # Ordenar por fecha descendente
    query = query.order_by(MovimientoModel.fecha.desc())
    
    movimientos = query.offset(skip).limit(limit).all()
    return movimientos

@router.get("/{movimiento_id}", response_model=MovimientoInventarioDetalleResponse)
async def read_movimiento(
    movimiento_id: int, 
    current_user: UserModel = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    db_movimiento = db.query(MovimientoModel).filter(MovimientoModel.id == movimiento_id).first()
    if db_movimiento is None:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return db_movimiento