from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from config.database import Base, engine, get_db
# Importar todos los modelos para asegurar que se creen todas las tablas
from models import User as UserModel, TokenBlacklist, Categoria, Proveedor, Ubicacion, Producto, Stock, TipoMovimiento, MovimientoInventario
from schemas.token import Token
from schemas.user import UserCreate, UserResponse
from utils.utils import create_access_token, get_password_hash, verify_password, add_token_to_blacklist
from routes import users, profile, categorias, proveedores, ubicaciones, productos, stocks, tipos_movimiento, movimientos

app = FastAPI(
    title="Sistema de Inventario API",
    description="API para la gestión de inventario de productos",
    version="1.0.0"
)

# Crear tablas
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/signup", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    add_token_to_blacklist(token, db)
    return {"msg": "Successfully logged out"}

# Incluir rutas
app.include_router(users.router, prefix="/admin", tags=["users"])
app.include_router(profile.router, tags=["profile"])
app.include_router(categorias.router)
app.include_router(proveedores.router)
app.include_router(ubicaciones.router)
app.include_router(productos.router)
app.include_router(stocks.router)
app.include_router(tipos_movimiento.router)
app.include_router(movimientos.router)
