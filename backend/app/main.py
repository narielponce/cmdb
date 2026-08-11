# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os

from .database import engine, Base, get_db
from .config import settings
from . import models, schemas, crud, simulator, pdf_generator

# Try to run auto-migrations for positioning columns
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE hosts ADD COLUMN IF NOT EXISTS plano_id INTEGER;"))
        conn.execute(text("ALTER TABLE hosts ADD COLUMN IF NOT EXISTS plano_x FLOAT;"))
        conn.execute(text("ALTER TABLE hosts ADD COLUMN IF NOT EXISTS plano_y FLOAT;"))
        conn.execute(text("ALTER TABLE racks ADD COLUMN IF NOT EXISTS plano_id INTEGER;"))
        conn.execute(text("ALTER TABLE racks ADD COLUMN IF NOT EXISTS plano_x FLOAT;"))
        conn.execute(text("ALTER TABLE racks ADD COLUMN IF NOT EXISTS plano_y FLOAT;"))
        conn.commit()
        print("🌱 Auto-migration of positioning columns succeeded.")
    except Exception as e:
        print(f"Skipping auto-migration columns: {e}")

Base.metadata.create_all(bind=engine)

# ==========================================
# SEGURIDAD Y TOKEN HELPERS
# ==========================================
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token de autenticación",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def check_module_permission(module_name: str, require_write: bool = False):
    def dependency(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
        if user.is_superadmin:
            return user
            
        if not user.role:
            raise HTTPException(status_code=403, detail="El usuario no tiene un rol asignado")
            
        perm = db.query(models.RoleModule).filter(
            models.RoleModule.role_id == user.role_id,
            models.RoleModule.module_name == module_name
        ).first()
        
        if not perm:
            raise HTTPException(status_code=403, detail=f"No tiene permisos para el módulo {module_name}")
            
        if require_write and not perm.can_write:
            raise HTTPException(status_code=403, detail=f"No tiene permisos de escritura en el módulo {module_name}")
            
        if not perm.can_read:
            raise HTTPException(status_code=403, detail=f"No tiene permisos de lectura en el módulo {module_name}")
            
        return user
    return dependency

def check_superadmin(user: models.User = Depends(get_current_user)):
    if not user.is_superadmin:
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requieren permisos de Superadmin.")
    return user

def check_global_permission(request: Request, db: Session = Depends(get_db)):
    path = request.url.path
    if path in ["/api/health", "/api/auth/login"] or path.startswith("/static") or path.startswith("/docs") or path.startswith("/redoc") or path == "/openapi.json":
        return
        
    if path.startswith("/api/usuarios") or path.startswith("/api/roles"):
        return

    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó un token de autenticación válido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ")[1]
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token de sesión inválido o vencido")
        
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
    if user.is_superadmin:
        return user
        
    method = request.method
    is_write = method in ["POST", "PUT", "DELETE"]
    
    # Permitir lectura (GET) de entidades de configuración e infraestructura a usuarios
    # que tengan acceso de lectura en crud, simulator o itam.
    shared_read_endpoints = [
        "/api/subestaciones",
        "/api/blindobarras",
        "/api/ups",
        "/api/racks",
        "/api/switches",
        "/api/hosts",
        "/api/servidores",
        "/api/aplicaciones",
        "/api/dependencias",
        "/api/procesos",
        "/api/planos",
        "/api/marcas",
        "/api/estados",
        "/api/tipos-host",
        "/api/tipos-servidor"
    ]
    
    is_shared_read = False
    if method == "GET":
        for endpoint in shared_read_endpoints:
            if path.startswith(endpoint):
                is_shared_read = True
                break

    if is_shared_read:
        if not user.role:
            raise HTTPException(status_code=403, detail="El usuario no tiene un rol asignado")
        
        has_permission = db.query(models.RoleModule).filter(
            models.RoleModule.role_id == user.role_id,
            models.RoleModule.module_name.in_(["crud", "simulator", "itam"]),
            models.RoleModule.can_read == True
        ).first() is not None
        
        if has_permission:
            return user
        else:
            raise HTTPException(
                status_code=403, 
                detail="No tiene permisos de lectura para acceder a estos datos de infraestructura"
            )

    if path.startswith("/api/inventario") or path.startswith("/api/consumibles"):
        module_name = "itam"
    elif path.startswith("/api/simulator"):
        module_name = "simulator"
        is_write = False
    elif path.startswith("/api/marcas") or path.startswith("/api/estados") or path.startswith("/api/tipos-host") or path.startswith("/api/tipos-servidor"):
        module_name = "crud"
        is_write = False
    else:
        module_name = "crud"
        
    if not user.role:
        raise HTTPException(status_code=403, detail="El usuario no tiene un rol asignado")
        
    perm = db.query(models.RoleModule).filter(
        models.RoleModule.role_id == user.role_id,
        models.RoleModule.module_name == module_name
    ).first()
    
    if not perm:
        raise HTTPException(status_code=403, detail=f"No tiene permisos para el módulo {module_name}")
        
    if is_write and not perm.can_write:
        raise HTTPException(status_code=403, detail=f"No tiene permisos de escritura en el módulo {module_name}")
        
    if not perm.can_read:
        raise HTTPException(status_code=403, detail=f"No tiene permisos de lectura en el módulo {module_name}")
        
    return user

app = FastAPI(title=settings.PROJECT_NAME, dependencies=[Depends(check_global_permission)])

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed Database if empty
def seed_database(db: Session):
    # Check if we have subestaciones
    if db.query(models.Subestacion).count() > 0:
        return
        
    print("🌱 Seeding database...")
    
    # 1. Subestaciones (20 elements)
    subestaciones_list = []
    for i in range(1, 21):
        se = models.Subestacion(nombre=f"Subestación Sector {i}", capacidad_kva=500.0 + i*50., ubicacion=f"Nave {i} - Planta General")
        db.add(se)
        subestaciones_list.append(se)
    db.commit()
    for se in subestaciones_list:
        db.refresh(se)

    # 2. Blindobarras (20 elements, pointing to subestaciones)
    blindobarras_list = []
    for i in range(1, 21):
        se_id = subestaciones_list[(i - 1) % len(subestaciones_list)].id
        bb = models.Blindobarra(nombre=f"Blindobarra Alimentación {i}", subestacion_id=se_id, capacidad_amperios=400 + i*20)
        db.add(bb)
        blindobarras_list.append(bb)
    db.commit()
    for bb in blindobarras_list:
        db.refresh(bb)
        
    # Pre-create TipoHost, TipoServidor, Marcas, Estados
    ups_tipo_id = crud.get_or_create_tipo_host(db, "UPS")
    sw_tipo_id = crud.get_or_create_tipo_host(db, "Switch")
    host_tipo_id = crud.get_or_create_tipo_host(db, "Host")
    srv_tipo_id = crud.get_or_create_tipo_host(db, "Servidor")
    
    # Additional TipoHost elements to seed the dynamic list (at least 20 support metadata)
    router_tipo_id = crud.get_or_create_tipo_host(db, "Router")
    ap_tipo_id = crud.get_or_create_tipo_host(db, "AP")
    plc_tipo_id = crud.get_or_create_tipo_host(db, "PLC")
    camara_tipo_id = crud.get_or_create_tipo_host(db, "Cámara")
    hmi_tipo_id = crud.get_or_create_tipo_host(db, "HMI")
    impresora_tipo_id = crud.get_or_create_tipo_host(db, "Impresora")
    firewall_tipo_id = crud.get_or_create_tipo_host(db, "Firewall")
    virtualizador_tipo_id = crud.get_or_create_tipo_host(db, "Virtualizador")
    
    apc_marca_id = crud.get_or_create_marca(db, "APC")
    cisco_marca_id = crud.get_or_create_marca(db, "Cisco")
    siemens_marca_id = crud.get_or_create_marca(db, "Siemens")
    hp_marca_id = crud.get_or_create_marca(db, "HP")
    hikvision_marca_id = crud.get_or_create_marca(db, "Hikvision")
    dell_marca_id = crud.get_or_create_marca(db, "Dell")
    aruba_marca_id = crud.get_or_create_marca(db, "Aruba")
    fortinet_marca_id = crud.get_or_create_marca(db, "Fortinet")
    lenovo_marca_id = crud.get_or_create_marca(db, "Lenovo")
    
    ok_estado_id = crud.get_or_create_estado(db, "Ok")
    cambio_baterias_estado_id = crud.get_or_create_estado(db, "Cambio Requerido")
    critico_estado_id = crud.get_or_create_estado(db, "Crítico")
    maint_estado_id = crud.get_or_create_estado(db, "En Mantenimiento")
    
    vm_tipo_id = crud.get_or_create_tipo_servidor(db, "Virtual (VM)")
    fisico_tipo_id = crud.get_or_create_tipo_servidor(db, "Físico")
    contenedor_tipo_id = crud.get_or_create_tipo_servidor(db, "Contenedor")
    
    # 3. UPSs (20 elements)
    ups_list = []
    for i in range(1, 21):
        bb_id = blindobarras_list[(i - 1) % len(blindobarras_list)].id
        ups = models.Host(
            nombre=f"UPS-General-P{i}", 
            blindobarra_id=bb_id, 
            marca_id=apc_marca_id, 
            modelo=f"Smart-UPS PX-{i}K", 
            serial=f"APC992388{i:02d}", 
            capacidad_kva=10.0 + i*5.0, 
            estado_id=ok_estado_id if i % 3 != 0 else cambio_baterias_estado_id,
            tipo_host_id=ups_tipo_id
        )
        db.add(ups)
        ups_list.append(ups)
    db.commit()
    for ups in ups_list:
        db.refresh(ups)
        
    # 4. Racks (20 elements)
    racks_list = []
    for i in range(1, 21):
        ups_id = ups_list[(i - 1) % len(ups_list)].id
        rack = models.Rack(nombre=f"Rack_Sector_{i}_A", ups_id=ups_id)
        db.add(rack)
        racks_list.append(rack)
    db.commit()
    for rack in racks_list:
        db.refresh(rack)
        
    # 5. Switches (20 elements)
    switches_list = []
    for i in range(1, 21):
        rack_id = racks_list[(i - 1) % len(racks_list)].id
        sw = models.Host(
            nombre=f"SW-ACCESO-{i:02d}", 
            ip=f"10.20.30.{i}", 
            rack_id=rack_id, 
            marca_id=cisco_marca_id, 
            modelo="Catalyst 9300", 
            serial=f"FCW2210X{i:03d}", 
            vlan=str(10 + i),
            tipo_host_id=sw_tipo_id
        )
        db.add(sw)
        switches_list.append(sw)
    db.commit()
    for sw in switches_list:
        db.refresh(sw)
        
    # 6. Hosts (20 elements)
    hosts_list = []
    roles = ["AP", "PLC", "Cámara", "PC de Control", "HMI", "Impresora", "Router", "Firewall"]
    for i in range(1, 21):
        sw_id = switches_list[(i - 1) % len(switches_list)].id
        rol = roles[(i - 1) % len(roles)]
        # Map rol to the corresponding tipo_host_id
        if rol == "AP":
            th_id = ap_tipo_id
        elif rol == "PLC":
            th_id = plc_tipo_id
        elif rol == "Cámara":
            th_id = camara_tipo_id
        elif rol == "HMI":
            th_id = hmi_tipo_id
        elif rol == "Impresora":
            th_id = impresora_tipo_id
        elif rol == "Router":
            th_id = router_tipo_id
        elif rol == "Firewall":
            th_id = firewall_tipo_id
        else:
            th_id = host_tipo_id
            
        h = models.Host(
            nombre=f"EQUIPO-{rol}-{i:02d}", 
            ip=f"10.20.30.{100 + i}", 
            rol=rol, 
            switch_id=sw_id, 
            puerto_switch=f"Gi1/0/{i}", 
            marca_id=siemens_marca_id if rol=="PLC" else (hikvision_marca_id if rol=="Cámara" else hp_marca_id), 
            modelo="S7-1500" if rol=="PLC" else ("DS-2CD208" if rol=="Cámara" else "ProDesk 400"), 
            serial=f"SRL998233{i:02d}", 
            ubicacion=f"Área Industrial Planta Nave {i}",
            tipo_host_id=th_id
        )
        db.add(h)
        hosts_list.append(h)
    db.commit()
    for h in hosts_list:
        db.refresh(h)
        
    # 7. Servidores (20 elements)
    servidores_list = []
    for i in range(1, 21):
        sw_id = switches_list[(i - 1) % len(switches_list)].id
        srv = models.Host(
            nombre=f"SRV-MES-APP{i:02d}", 
            ip=f"10.100.5.{10 + i}", 
            sistema_operativo="Windows Server 2022" if i % 2 == 0 else "Linux RHEL", 
            tipo_servidor_id=vm_tipo_id if i % 3 != 0 else fisico_tipo_id, 
            marca_id=dell_marca_id, 
            modelo="PowerEdge R750", 
            serial=f"DELL9912{i:02d}", 
            switch_id=sw_id,
            tipo_host_id=srv_tipo_id
        )
        db.add(srv)
        servidores_list.append(srv)
    db.commit()
    for srv in servidores_list:
        db.refresh(srv)
        
    # 8. Aplicaciones (20 elements)
    aplicaciones_list = []
    for i in range(1, 21):
        app = models.Aplicacion(
            nombre=f"Aplicativo MES Tracker {i:02d}", 
            descripcion=f"Administra la línea de montaje {i} en tiempo real", 
            owner_negocio=f"Producción Planta Sector {i}"
        )
        db.add(app)
        aplicaciones_list.append(app)
    db.commit()
    for app in aplicaciones_list:
        db.refresh(app)
        
    # 9. Dependencias (20 elements)
    for i in range(1, 21):
        app_id = aplicaciones_list[(i - 1) % len(aplicaciones_list)].id
        srv_id = servidores_list[(i - 1) % len(servidores_list)].id
        dep = models.DependenciaAppHost(
            app_id=app_id, 
            host_id=srv_id, 
            rol_servidor="Base de Datos Oracle" if i % 2 == 0 else "Frontend Web IIS"
        )
        db.add(dep)
    db.commit()
    
    # 10. Procesos Planta (20 elements)
    for i in range(1, 21):
        app_id = aplicaciones_list[(i - 1) % len(aplicaciones_list)].id
        p = models.ProcesoPlanta(
            nombre_proceso=f"Proceso Secuenciado {i}", 
            linea_produccion=f"Montaje Línea {i}", 
            aplicacion_id=app_id
        )
        db.add(p)
    db.commit()
    
    # 11. Catalogo de Equipos (20 elements)
    catalogo_list = []
    for i in range(1, 21):
        cat = models.CatalogoEquipo(
            marca="Cisco" if i % 2 == 0 else "HP", 
            modelo=f"Modelo Catalogo {i}", 
            tipo="Switch" if i % 2 == 0 else "PC", 
            serializado=1
        )
        db.add(cat)
        catalogo_list.append(cat)
    db.commit()
    for cat in catalogo_list:
        db.refresh(cat)
        
    # 12. Stock Consumibles (20 elements)
    for i in range(1, 21):
        cat_id = catalogo_list[(i - 1) % len(catalogo_list)].id
        stock = models.StockConsumible(
            catalogo_id=cat_id, 
            cantidad=10 + i * 5, 
            ubicacion=f"Estantería {i} - Depósito IT", 
            stock_minimo=5
        )
        db.add(stock)
    db.commit()

    # 13. Seed Security Users and Roles
    if db.query(models.User).count() == 0:
        print("🌱 Seeding security users and roles...")
        
        # Create Default Roles
        admin_role = models.Role(nombre="Administrador", descripcion="Acceso total a la aplicación de red")
        operador_role = models.Role(nombre="Operador", descripcion="Acceso de lectura y escritura de ITAM/Inventario")
        lector_role = models.Role(nombre="Lector", descripcion="Solo lectura general")
        
        db.add(admin_role)
        db.add(operador_role)
        db.add(lector_role)
        db.commit()
        db.refresh(admin_role)
        db.refresh(operador_role)
        db.refresh(lector_role)
        
        # Add RoleModule permissions
        # Admin: access to all modules
        for mod in ["dashboard", "simulator", "itam", "crud"]:
            db.add(models.RoleModule(role_id=admin_role.id, module_name=mod, can_read=True, can_write=True))
            
        # Operador: write access only to itam, read to others
        db.add(models.RoleModule(role_id=operador_role.id, module_name="dashboard", can_read=True, can_write=False))
        db.add(models.RoleModule(role_id=operador_role.id, module_name="simulator", can_read=True, can_write=False))
        db.add(models.RoleModule(role_id=operador_role.id, module_name="itam", can_read=True, can_write=True))
        db.add(models.RoleModule(role_id=operador_role.id, module_name="crud", can_read=True, can_write=False))
        
        # Lector: read only
        for mod in ["dashboard", "simulator", "itam", "crud"]:
            db.add(models.RoleModule(role_id=lector_role.id, module_name=mod, can_read=True, can_write=False))
            
        db.commit()
        
        # Create Superadmin User
        admin_user = schemas.UserCreate(
            username=settings.SUPERADMIN_USER,
            nombre="Administrador NetTrack",
            password=settings.SUPERADMIN_PASSWORD,
            role_id=None,
            is_superadmin=True
        )
        crud.create_user(db, admin_user)
        
        # Create testing users for roles
        crud.create_user(db, schemas.UserCreate(
            username="operador",
            nombre="Operador de Planta",
            password="operadorpassword",
            role_id=operador_role.id,
            is_superadmin=False
        ))
        crud.create_user(db, schemas.UserCreate(
            username="lector",
            nombre="Visualizador Invitado",
            password="lectorpassword",
            role_id=lector_role.id,
            is_superadmin=False
        ))
    
    print("✅ Seed completed!")

# Seed call on startup
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    seed_database(db)

# Mount files
app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

# Health
@app.get("/api/health")
def health():
    return {"status": "ok", "project": settings.PROJECT_NAME}

# ==========================================
#    API ENDPOINTS: AUTENTICACIÓN Y SEGURIDAD
# ==========================================
@app.post("/api/auth/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=login_data.username)
    if not user or not crud.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    
    # Get user permissions/modules list
    modules_list = []
    if user.is_superadmin:
        # Superadmin has access to everything
        modules_list = [
            {"module_name": "dashboard", "can_read": True, "can_write": True},
            {"module_name": "simulator", "can_read": True, "can_write": True},
            {"module_name": "itam", "can_read": True, "can_write": True},
            {"module_name": "crud", "can_read": True, "can_write": True},
            {"module_name": "usuarios_roles", "can_read": True, "can_write": True}
        ]
    elif user.role:
        modules = db.query(models.RoleModule).filter(models.RoleModule.role_id == user.role_id).all()
        modules_list = [
            {"module_name": m.module_name, "can_read": m.can_read, "can_write": m.can_write}
            for m in modules
        ]
        
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "nombre": user.nombre,
        "is_superadmin": user.is_superadmin,
        "role_nombre": "Superadmin" if user.is_superadmin else (user.role.nombre if user.role else None),
        "modules": modules_list
    }

# --- GESTIÓN DE USUARIOS (Superadmin únicamente) ---
@app.get("/api/usuarios", response_model=List[schemas.UserResponse])
def read_users(db: Session = Depends(get_db), current_user: models.User = Depends(check_superadmin)):
    return crud.get_users(db)

@app.post("/api/usuarios", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(check_superadmin)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    return crud.create_user(db, user)

@app.put("/api/usuarios/{id}", response_model=schemas.UserResponse)
def update_user(id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(check_superadmin)):
    db_user = crud.update_user(db, id, user)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

@app.delete("/api/usuarios/{id}", response_model=schemas.Message)
def delete_user(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(check_superadmin)):
    # Prevent self-deletion
    if current_user.id == id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario")
    if not crud.delete_user(db, id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado con éxito"}

# --- GESTIÓN DE ROLES (Superadmin únicamente) ---
@app.get("/api/roles", response_model=List[schemas.RoleResponse])
def read_roles(db: Session = Depends(get_db), current_user: models.User = Depends(check_superadmin)):
    return crud.get_roles(db)

@app.post("/api/roles", response_model=schemas.RoleResponse)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(check_superadmin)):
    return crud.create_role(db, role)

@app.put("/api/roles/{id}", response_model=schemas.RoleResponse)
def update_role(id: int, role: schemas.RoleUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(check_superadmin)):
    db_role = crud.update_role(db, id, role)
    if not db_role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return db_role

@app.delete("/api/roles/{id}", response_model=schemas.Message)
def delete_role(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(check_superadmin)):
    if not crud.delete_role(db, id):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"message": "Rol eliminado con éxito"}

@app.put("/api/roles/{id}/permisos", response_model=List[schemas.RoleModuleResponse])
def update_role_permissions(id: int, modules: List[schemas.RoleModuleBase], db: Session = Depends(get_db), current_user: models.User = Depends(check_superadmin)):
    db_role = crud.get_role(db, id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return crud.update_role_modules(db, id, modules)

# ==========================================
#    API ENDPOINTS: CRUD FOR SUBESTACIONES
# ==========================================
@app.get("/api/subestaciones", response_model=List[schemas.SubestacionResponse])
def read_subestaciones(db: Session = Depends(get_db)):
    return crud.get_subestaciones(db)

@app.post("/api/subestaciones", response_model=schemas.SubestacionResponse)
def create_subestacion(sub: schemas.SubestacionCreate, db: Session = Depends(get_db)):
    return crud.create_subestacion(db, sub)

@app.put("/api/subestaciones/{id}", response_model=schemas.SubestacionResponse)
def update_subestacion(id: int, sub: schemas.SubestacionUpdate, db: Session = Depends(get_db)):
    db_sub = crud.update_subestacion(db, id, sub)
    if not db_sub:
        raise HTTPException(status_code=404, detail="Subestación no encontrada")
    return db_sub

@app.delete("/api/subestaciones/{id}", response_model=schemas.Message)
def delete_subestacion(id: int, db: Session = Depends(get_db)):
    if not crud.delete_subestacion(db, id):
        raise HTTPException(status_code=404, detail="Subestación no encontrada")
    return {"message": "Subestación eliminada con éxito"}

# ==========================================
#    API ENDPOINTS: CRUD FOR BLINDOBARRAS
# ==========================================
@app.get("/api/blindobarras", response_model=List[schemas.BlindobarraResponse])
def read_blindobarras(db: Session = Depends(get_db)):
    return crud.get_blindobarras(db)

@app.post("/api/blindobarras", response_model=schemas.BlindobarraResponse)
def create_blindobarra(bb: schemas.BlindobarraCreate, db: Session = Depends(get_db)):
    return crud.create_blindobarra(db, bb)

@app.put("/api/blindobarras/{id}", response_model=schemas.BlindobarraResponse)
def update_blindobarra(id: int, bb: schemas.BlindobarraUpdate, db: Session = Depends(get_db)):
    db_bb = crud.update_blindobarra(db, id, bb)
    if not db_bb:
        raise HTTPException(status_code=404, detail="Blindobarra no encontrada")
    return db_bb

@app.delete("/api/blindobarras/{id}", response_model=schemas.Message)
def delete_blindobarra(id: int, db: Session = Depends(get_db)):
    if not crud.delete_blindobarra(db, id):
        raise HTTPException(status_code=404, detail="Blindobarra no encontrada")
    return {"message": "Blindobarra eliminada con éxito"}

# ==========================================
#    API ENDPOINTS: CRUD FOR UPS
# ==========================================
@app.get("/api/ups", response_model=List[schemas.UPSResponse])
def read_ups(db: Session = Depends(get_db)):
    return crud.get_ups_all(db)

@app.post("/api/ups", response_model=schemas.UPSResponse)
def create_ups(ups: schemas.UPSCreate, db: Session = Depends(get_db)):
    return crud.create_ups(db, ups)

@app.put("/api/ups/{id}", response_model=schemas.UPSResponse)
def update_ups(id: int, ups: schemas.UPSUpdate, db: Session = Depends(get_db)):
    db_ups = crud.update_ups(db, id, ups)
    if not db_ups:
        raise HTTPException(status_code=404, detail="UPS no encontrada")
    return db_ups

@app.delete("/api/ups/{id}", response_model=schemas.Message)
def delete_ups(id: int, db: Session = Depends(get_db)):
    if not crud.delete_ups(db, id):
        raise HTTPException(status_code=404, detail="UPS no encontrada")
    return {"message": "UPS eliminada con éxito"}

# ==========================================
#    API ENDPOINTS: CRUD FOR RACKS
# ==========================================
@app.get("/api/racks", response_model=List[schemas.RackResponse])
def read_racks(db: Session = Depends(get_db)):
    return crud.get_racks(db)

@app.post("/api/racks", response_model=schemas.RackResponse)
def create_rack(r: schemas.RackCreate, db: Session = Depends(get_db)):
    return crud.create_rack(db, r)

@app.put("/api/racks/{id}", response_model=schemas.RackResponse)
def update_rack(id: int, r: schemas.RackUpdate, db: Session = Depends(get_db)):
    db_r = crud.update_rack(db, id, r)
    if not db_r:
        raise HTTPException(status_code=404, detail="Rack no encontrado")
    return db_r

@app.delete("/api/racks/{id}", response_model=schemas.Message)
def delete_rack(id: int, db: Session = Depends(get_db)):
    if not crud.delete_rack(db, id):
        raise HTTPException(status_code=404, detail="Rack no encontrado")
    return {"message": "Rack eliminado con éxito"}

# ==========================================
#    API ENDPOINTS: CRUD FOR SWITCHES
# ==========================================
@app.get("/api/switches", response_model=List[schemas.SwitchResponse])
def read_switches(db: Session = Depends(get_db)):
    return crud.get_switches(db)

@app.post("/api/switches", response_model=schemas.SwitchResponse)
def create_switch(sw: schemas.SwitchCreate, db: Session = Depends(get_db)):
    return crud.create_switch(db, sw)

@app.put("/api/switches/{id}", response_model=schemas.SwitchResponse)
def update_switch(id: int, sw: schemas.SwitchUpdate, db: Session = Depends(get_db)):
    db_sw = crud.update_switch(db, id, sw)
    if not db_sw:
        raise HTTPException(status_code=404, detail="Switch no encontrado")
    return db_sw

@app.delete("/api/switches/{id}", response_model=schemas.Message)
def delete_switch(id: int, db: Session = Depends(get_db)):
    if not crud.delete_switch(db, id):
        raise HTTPException(status_code=404, detail="Switch no encontrado")
    return {"message": "Switch eliminado con éxito"}

# ==========================================
#    API ENDPOINTS: CRUD FOR HOSTS
# ==========================================
@app.get("/api/hosts", response_model=List[schemas.HostResponse])
def read_hosts(db: Session = Depends(get_db)):
    return crud.get_hosts(db)

@app.post("/api/hosts", response_model=schemas.HostResponse)
def create_host(h: schemas.HostCreate, db: Session = Depends(get_db)):
    return crud.create_host(db, h)

@app.put("/api/hosts/{id}", response_model=schemas.HostResponse)
def update_host(id: int, h: schemas.HostUpdate, db: Session = Depends(get_db)):
    db_h = crud.update_host(db, id, h)
    if not db_h:
        raise HTTPException(status_code=404, detail="Host no encontrado")
    return db_h

@app.delete("/api/hosts/{id}", response_model=schemas.Message)
def delete_host(id: int, db: Session = Depends(get_db)):
    if not crud.delete_host(db, id):
        raise HTTPException(status_code=404, detail="Host no encontrado")
    return {"message": "Host eliminado con éxito"}

# ==========================================
#    API ENDPOINTS: CRUD FOR SERVIDORES
# ==========================================
@app.get("/api/servidores", response_model=List[schemas.ServidorResponse])
def read_servidores(db: Session = Depends(get_db)):
    return crud.get_servidores(db)

@app.post("/api/servidores", response_model=schemas.ServidorResponse)
def create_servidor(srv: schemas.ServidorCreate, db: Session = Depends(get_db)):
    return crud.create_servidor(db, srv)

@app.put("/api/servidores/{id}", response_model=schemas.ServidorResponse)
def update_servidor(id: int, srv: schemas.ServidorUpdate, db: Session = Depends(get_db)):
    db_srv = crud.update_servidor(db, id, srv)
    if not db_srv:
        raise HTTPException(status_code=404, detail="Servidor no encontrado")
    return db_srv

@app.delete("/api/servidores/{id}", response_model=schemas.Message)
def delete_servidor(id: int, db: Session = Depends(get_db)):
    if not crud.delete_servidor(db, id):
        raise HTTPException(status_code=404, detail="Servidor no encontrado")
    return {"message": "Servidor eliminado con éxito"}

# ==========================================
#   API ENDPOINTS: CRUD FOR APLICACIONES
# ==========================================
@app.get("/api/aplicaciones", response_model=List[schemas.AplicacionResponse])
def read_aplicaciones(db: Session = Depends(get_db)):
    return crud.get_aplicaciones(db)

@app.post("/api/aplicaciones", response_model=schemas.AplicacionResponse)
def create_aplicacion(app: schemas.AplicacionCreate, db: Session = Depends(get_db)):
    return crud.create_aplicacion(db, app)

@app.put("/api/aplicaciones/{id}", response_model=schemas.AplicacionResponse)
def update_aplicacion(id: int, app: schemas.AplicacionUpdate, db: Session = Depends(get_db)):
    db_app = crud.update_aplicacion(db, id, app)
    if not db_app:
        raise HTTPException(status_code=404, detail="Aplicación no encontrada")
    return db_app

@app.delete("/api/aplicaciones/{id}", response_model=schemas.Message)
def delete_aplicacion(id: int, db: Session = Depends(get_db)):
    if not crud.delete_aplicacion(db, id):
        raise HTTPException(status_code=404, detail="Aplicación no encontrada")
    return {"message": "Aplicación eliminada con éxito"}

# ==========================================
#   API ENDPOINTS: CRUD FOR DEPENDENCIAS
# ==========================================
@app.get("/api/dependencias", response_model=List[schemas.DependenciaResponse])
def read_dependencias(db: Session = Depends(get_db)):
    return crud.get_dependencias(db)

@app.post("/api/dependencias", response_model=schemas.DependenciaResponse)
def create_dependencia(dep: schemas.DependenciaCreate, db: Session = Depends(get_db)):
    return crud.create_dependencia(db, dep)

@app.put("/api/dependencias/{id}", response_model=schemas.DependenciaResponse)
def update_dependencia(id: int, dep: schemas.DependenciaUpdate, db: Session = Depends(get_db)):
    db_dep = crud.update_dependencia(db, id, dep)
    if not db_dep:
        raise HTTPException(status_code=404, detail="Dependencia no encontrada")
    return db_dep

@app.delete("/api/dependencias/{id}", response_model=schemas.Message)
def delete_dependencia(id: int, db: Session = Depends(get_db)):
    if not crud.delete_dependencia(db, id):
        raise HTTPException(status_code=404, detail="Dependencia no encontrada")
    return {"message": "Dependencia eliminada con éxito"}

# ==========================================
#   API ENDPOINTS: CRUD FOR PROCESOS
# ==========================================
@app.get("/api/procesos", response_model=List[schemas.ProcesoResponse])
def read_procesos(db: Session = Depends(get_db)):
    return crud.get_procesos(db)

@app.post("/api/procesos", response_model=schemas.ProcesoResponse)
def create_proceso(p: schemas.ProcesoCreate, db: Session = Depends(get_db)):
    return crud.create_proceso(db, p)

@app.put("/api/procesos/{id}", response_model=schemas.ProcesoResponse)
def update_proceso(id: int, p: schemas.ProcesoUpdate, db: Session = Depends(get_db)):
    db_p = crud.update_proceso(db, id, p)
    if not db_p:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    return db_p

@app.delete("/api/procesos/{id}", response_model=schemas.Message)
def delete_proceso(id: int, db: Session = Depends(get_db)):
    if not crud.delete_proceso(db, id):
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    return {"message": "Proceso eliminado con éxito"}

# ==========================================
#   API ENDPOINTS: CRUD FOR CATALOGOS
# ==========================================
@app.get("/api/catalogo", response_model=List[schemas.CatalogoResponse])
def read_catalogos(db: Session = Depends(get_db)):
    return crud.get_catalogos(db)

@app.post("/api/catalogo", response_model=schemas.CatalogoResponse)
def create_catalogo(cat: schemas.CatalogoCreate, db: Session = Depends(get_db)):
    return crud.create_catalogo(db, cat)

# ==========================================
#   API ENDPOINTS: CRUD FOR STOCK CONSUMIBLES
# ==========================================
@app.get("/api/consumibles", response_model=List[schemas.ConsumibleResponse])
def read_consumibles(db: Session = Depends(get_db)):
    return crud.get_consumibles(db)

@app.post("/api/consumibles", response_model=schemas.ConsumibleResponse)
def create_consumible(data: dict, db: Session = Depends(get_db)):
    res = crud.create_consumible_flat(db, data)
    # returns flat dictionary structure
    return {
        "id": res.id,
        "catalogo_id": res.catalogo_id,
        "marca": res.catalogo.marca,
        "modelo": res.catalogo.modelo,
        "tipo": res.catalogo.tipo,
        "cantidad": res.cantidad,
        "ubicacion": res.ubicacion,
        "stock_minimo": res.stock_minimo
    }

@app.put("/api/consumibles/{id}", response_model=schemas.ConsumibleResponse)
def update_consumible(id: int, data: dict, db: Session = Depends(get_db)):
    res = crud.update_consumible_flat(db, id, data)
    if not res:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return {
        "id": res.id,
        "catalogo_id": res.catalogo_id,
        "marca": res.catalogo.marca,
        "modelo": res.catalogo.modelo,
        "tipo": res.catalogo.tipo,
        "cantidad": res.cantidad,
        "ubicacion": res.ubicacion,
        "stock_minimo": res.stock_minimo
    }

@app.delete("/api/consumibles/{id}", response_model=schemas.Message)
def delete_consumible(id: int, db: Session = Depends(get_db)):
    if not crud.delete_consumible(db, id):
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return {"message": "Insumo eliminado con éxito"}

# ==========================================
#    API ENDPOINTS: HISTORIAL
# ==========================================
@app.get("/api/inventario/movimientos", response_model=List[schemas.HistorialResponse])
def read_movimientos(db: Session = Depends(get_db)):
    return crud.get_historial(db)

# ==========================================
#    API ENDPOINTS: ITAM CORE OPERATIONS
# ==========================================
@app.get("/api/inventario/consolidado", response_model=List[schemas.ConsolidadoAssetResponse])
def get_inventario_consolidado(db: Session = Depends(get_db)):
    assets = []
    
    # 1. Switches
    switches = db.query(models.Host).join(models.TipoHost).filter(models.TipoHost.nombre == "Switch").all()
    for sw in switches:
        assets.append({
            "tipo_equipo": "🔌 Switch",
            "nombre": sw.nombre,
            "marca": sw.marca.nombre if sw.marca else "",
            "modelo": sw.modelo,
            "serial": sw.serial,
            "ip": sw.ip,
            "ubicacion_estado": "🟢 En Producción" if sw.rack_id else "📦 En Depósito"
        })
        
    # 2. UPS
    ups_list = db.query(models.Host).join(models.TipoHost).filter(models.TipoHost.nombre == "UPS").all()
    for ups in ups_list:
        assets.append({
            "tipo_equipo": "🔋 UPS",
            "nombre": ups.nombre,
            "marca": ups.marca.nombre if ups.marca else "",
            "modelo": ups.modelo,
            "serial": ups.serial,
            "ip": ups.ip,
            "ubicacion_estado": "🟢 En Producción" if ups.blindobarra_id else "📦 En Depósito"
        })
        
    # 3. Hosts (Roles: AP, Cámara, PLC)
    hosts = db.query(models.Host).join(models.TipoHost).filter(
        models.TipoHost.nombre == "Host",
        models.Host.rol.in_(["AP", "Cámara", "PLC"])
    ).all()
    for h in hosts:
        tipo = "📶 Access Point" if h.rol == "AP" else ("📷 Cámara IP" if h.rol == "Cámara" else "⚙️ Host Industrial")
        assets.append({
            "tipo_equipo": tipo,
            "nombre": h.nombre,
            "marca": h.marca.nombre if h.marca else "",
            "modelo": h.modelo,
            "serial": h.serial,
            "ip": h.ip,
            "ubicacion_estado": "🟢 En Producción" if h.switch_id else "📦 En Depósito"
        })
        
    return assets

@app.post("/api/inventario/ingreso")
async def registrar_ingreso(
    tipo_activo: str = Form(...),
    nombre: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    serial: str = Form(...),
    archivo_remito: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    tipo_limpio = tipo_activo.replace("🔌 ", "").replace("🌐 ", "").replace("🔋 ", "").replace("🖥️ ", "").strip()
    
    # Save Upload File
    ruta_guardado = None
    if archivo_remito:
        extension = archivo_remito.filename.split(".")[-1]
        nombre_archivo = f"remito_ingreso_{serial}.{extension}"
        ruta_guardado = os.path.join(settings.UPLOAD_DIR, nombre_archivo)
        with open(ruta_guardado, "wb") as buffer:
            shutil.copyfileobj(archivo_remito.file, buffer)
            
    # Insert in hosts table with appropriate tipo_host
    marca_id = crud.get_or_create_marca(db, marca)
    
    if "Switch" in tipo_limpio:
        tipo_id = crud.get_or_create_tipo_host(db, "Switch")
        db_item = models.Host(
            nombre=nombre, 
            marca_id=marca_id, 
            modelo=modelo, 
            serial=serial, 
            ip="", 
            tipo_host_id=tipo_id
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        ref_id = db_item.id
        tabla_ref = "switches"
    else:
        tipo_id = crud.get_or_create_tipo_host(db, "Host")
        rol = "AP" if "Access Point" in tipo_limpio else ("UPS" if "UPS" in tipo_limpio else "Otro")
        if rol == "UPS":
            tipo_id = crud.get_or_create_tipo_host(db, "UPS")
        db_item = models.Host(
            nombre=nombre, 
            marca_id=marca_id, 
            modelo=modelo, 
            serial=serial, 
            ip="", 
            rol=rol, 
            tipo_host_id=tipo_id
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        ref_id = db_item.id
        tabla_ref = "hosts"
        
    detalle_log = f"Ingreso de equipo nuevo: {marca} {modelo} Serial: {serial}"
    if ruta_guardado:
        detalle_log += f" [Remito PDF: {ruta_guardado}]"
        
    crud.log_movimiento(
        db, 
        operador="Operador NetTrack", 
        tipo="Ingreso Depósito", 
        ref_id=ref_id, 
        tabla=tabla_ref, 
        detalle=detalle_log
    )
    
    return {"status": "success", "message": f"Equipo {nombre} ingresado a Depósito."}

@app.post("/api/inventario/desplegar")
def desplegar_activo(req: schemas.DeployAssetRequest, db: Session = Depends(get_db)):
    # 1. Find device
    db_item = db.query(models.Host).filter(models.Host.nombre == req.nombre).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
    if "Switch" in req.tipo_equipo:
        db_item.rack_id = req.destino_id
        tabla_ref = "switches"
        destino_str = f"Rack ID: {req.destino_id}"
    else:
        db_item.switch_id = req.destino_id
        tabla_ref = "hosts"
        destino_str = f"Switch ID: {req.destino_id}"
        
    db.commit()
    db.refresh(db_item)
    
    # 2. PDF generation
    nombre_limpio = db_item.nombre.replace(' ', '_')
    ruta_pdf = f"{settings.UPLOAD_DIR}/acta_entrega_{nombre_limpio}.pdf"
    
    marca_str = db_item.marca.nombre if db_item.marca else "Generico"
    
    datos_mov = {
        "tipo_equipo": req.tipo_equipo,
        "nombre": db_item.nombre,
        "marca": marca_str,
        "modelo": db_item.modelo or "",
        "serial": db_item.serial or "S/N",
        "operador": req.operador,
        "responsable": req.responsable,
        "destino_id": req.destino_id,
        "ruta_pdf": ruta_pdf
    }
    
    generated_pdf_path = pdf_generator.generar_pdf_acta_entrega(datos_mov)
    
    # 3. Log movement
    detalle_log = f"Despliegue de {req.tipo_equipo} a planta. Destino: {destino_str}. Retira: {req.responsable}."
    detalle_log += f" [Acta PDF: {generated_pdf_path}]"
    
    crud.log_movimiento(
        db,
        operador=req.operador,
        tipo="Salida a Planta",
        ref_id=db_item.id,
        tabla=tabla_ref,
        detalle=detalle_log
    )
    
    # Return file for download
    return FileResponse(generated_pdf_path, media_type='application/pdf', filename=os.path.basename(generated_pdf_path))

@app.post("/api/inventario/consumibles/salida")
def salida_consumible(req: schemas.SalidaConsumibleRequest, db: Session = Depends(get_db)):
    # 1. Fetch consumable
    c = db.query(models.StockConsumible).filter(models.StockConsumible.id == req.consumible_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consumible no encontrado")
        
    if c.cantidad < req.cantidad:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente. Disponible: {c.cantidad} unidades.")
        
    # 2. Update stock
    c.cantidad -= req.cantidad
    db.commit()
    db.refresh(c)
    
    # 3. Generate PDF
    datos_mov = {
        "marca": c.catalogo.marca,
        "modelo": c.catalogo.modelo,
        "tipo_material": c.catalogo.tipo,
        "cantidad_retirada": req.cantidad,
        "ubicacion_origen": c.ubicacion,
        "operador": req.operador,
        "responsable": req.responsable
    }
    
    generated_pdf_path = pdf_generator.generar_pdf_acta_consumible(datos_mov)
    
    # 4. Log movement
    detalle_log = (
        f"Egreso de Consumible: {req.cantidad} un. de {c.catalogo.marca} {c.catalogo.modelo} ({c.catalogo.tipo}) "
        f"desde {c.ubicacion}. Quedan en stock: {c.cantidad}. Retira: {req.responsable}."
    )
    detalle_log += f" [Acta PDF: {generated_pdf_path}]"
    
    crud.log_movimiento(
        db,
        operador=req.operador,
        tipo="Salida Consumible",
        ref_id=c.id,
        tabla="stock_consumibles",
        detalle=detalle_log
    )
    
    return FileResponse(generated_pdf_path, media_type='application/pdf', filename=os.path.basename(generated_pdf_path))


# ==========================================
#    API ENDPOINTS: SIMULATOR
# ==========================================
@app.post("/api/simulator/impact")
def run_simulation(req: schemas.SimulationRequest, db: Session = Depends(get_db)):
    if req.tipo_corte == "Subestación":
        res = simulator.simular_corte_subestacion(db, req.target_id)
        return {"tipo": "Subestación", "resultados": res}
    elif req.tipo_corte == "Blindobarra":
        res = simulator.simular_corte_blindobarra(db, req.target_id)
        return {"tipo": "Blindobarra", "resultados": res}
    elif req.tipo_corte == "UPS":
        res = simulator.simular_corte_ups(db, req.target_id)
        return {"tipo": "UPS", "resultados": res}
    elif req.tipo_corte == "Rack":
        res = simulator.simular_corte_rack(db, req.target_id)
        return {"tipo": "Rack", "resultados": res}
    elif "Servidor" in req.tipo_corte:
        res = simulator.simular_mantenimiento_servidor(db, req.target_id)
        return {"tipo": "Servidor", "resultados": res}
    else:
        raise HTTPException(status_code=400, detail="Tipo de corte no soportado")


# ==========================================
#    API ENDPOINTS: SUPPORT TABLES
# ==========================================
# Marcas
@app.get("/api/marcas", response_model=List[schemas.MarcaResponse])
def read_marcas(db: Session = Depends(get_db)):
    return crud.get_marcas(db)

@app.post("/api/marcas", response_model=schemas.MarcaResponse)
def create_marca(m: schemas.MarcaCreate, db: Session = Depends(get_db)):
    return crud.create_marca(db, m)

@app.put("/api/marcas/{id}", response_model=schemas.MarcaResponse)
def update_marca(id: int, m: schemas.MarcaUpdate, db: Session = Depends(get_db)):
    db_m = crud.update_marca(db, id, m)
    if not db_m:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return db_m

@app.delete("/api/marcas/{id}", response_model=schemas.Message)
def delete_marca(id: int, db: Session = Depends(get_db)):
    if not crud.delete_marca(db, id):
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return {"message": "Marca eliminada correctamente"}

# Estados
@app.get("/api/estados", response_model=List[schemas.EstadoResponse])
def read_estados(db: Session = Depends(get_db)):
    return crud.get_estados(db)

@app.post("/api/estados", response_model=schemas.EstadoResponse)
def create_estado(e: schemas.EstadoCreate, db: Session = Depends(get_db)):
    return crud.create_estado(db, e)

@app.put("/api/estados/{id}", response_model=schemas.EstadoResponse)
def update_estado(id: int, e: schemas.EstadoUpdate, db: Session = Depends(get_db)):
    db_e = crud.update_estado(db, id, e)
    if not db_e:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return db_e

@app.delete("/api/estados/{id}", response_model=schemas.Message)
def delete_estado(id: int, db: Session = Depends(get_db)):
    if not crud.delete_estado(db, id):
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return {"message": "Estado eliminado correctamente"}

# Tipos Host
@app.get("/api/tipos-host", response_model=List[schemas.TipoHostResponse])
def read_tipos_host(db: Session = Depends(get_db)):
    return crud.get_tipos_host(db)

@app.post("/api/tipos-host", response_model=schemas.TipoHostResponse)
def create_tipo_host(th: schemas.TipoHostCreate, db: Session = Depends(get_db)):
    return crud.create_tipo_host(db, th)

@app.put("/api/tipos-host/{id}", response_model=schemas.TipoHostResponse)
def update_tipo_host(id: int, th: schemas.TipoHostUpdate, db: Session = Depends(get_db)):
    db_th = crud.update_tipo_host(db, id, th)
    if not db_th:
        raise HTTPException(status_code=404, detail="Tipo Host no encontrado")
    return db_th

@app.delete("/api/tipos-host/{id}", response_model=schemas.Message)
def delete_tipo_host(id: int, db: Session = Depends(get_db)):
    if not crud.delete_tipo_host(db, id):
        raise HTTPException(status_code=404, detail="Tipo Host no encontrado")
    return {"message": "Tipo Host eliminado correctamente"}

# Tipos Servidor
@app.get("/api/tipos-servidor", response_model=List[schemas.TipoServidorResponse])
def read_tipos_servidor(db: Session = Depends(get_db)):
    return crud.get_tipos_servidor(db)

@app.post("/api/tipos-servidor", response_model=schemas.TipoServidorResponse)
def create_tipo_servidor(ts: schemas.TipoServidorCreate, db: Session = Depends(get_db)):
    return crud.create_tipo_servidor(db, ts)

@app.put("/api/tipos-servidor/{id}", response_model=schemas.TipoServidorResponse)
def update_tipo_servidor(id: int, ts: schemas.TipoServidorUpdate, db: Session = Depends(get_db)):
    db_ts = crud.update_tipo_servidor(db, id, ts)
    if not db_ts:
        raise HTTPException(status_code=404, detail="Tipo Servidor no encontrado")
    return db_ts

@app.delete("/api/tipos-servidor/{id}", response_model=schemas.Message)
def delete_tipo_servidor(id: int, db: Session = Depends(get_db)):
    if not crud.delete_tipo_servidor(db, id):
        raise HTTPException(status_code=404, detail="Tipo Servidor no encontrado")
    return {"message": "Tipo Servidor eliminado correctamente"}


# ==========================================
# ENDPOINTS DE PLANOS e INFRAESTRUCTURA
# ==========================================

@app.get("/api/planos", response_model=List[schemas.PlanoResponse])
def get_planos(db: Session = Depends(get_db)):
    return db.query(models.Plano).order_by(models.Plano.nombre.asc()).all()

@app.get("/api/planos/{id}", response_model=schemas.PlanoResponse)
def get_plano(id: int, db: Session = Depends(get_db)):
    plano = db.query(models.Plano).filter(models.Plano.id == id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    return plano

@app.post("/api/planos", response_model=schemas.PlanoResponse)
def create_plano(plano: schemas.PlanoCreate, db: Session = Depends(get_db)):
    db_plano = models.Plano(**plano.dict())
    db.add(db_plano)
    db.commit()
    db.refresh(db_plano)
    return db_plano

@app.put("/api/planos/{id}", response_model=schemas.PlanoResponse)
def update_plano(id: int, plano: schemas.PlanoUpdate, db: Session = Depends(get_db)):
    db_plano = db.query(models.Plano).filter(models.Plano.id == id).first()
    if not db_plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    for key, val in plano.dict(exclude_unset=True).items():
        setattr(db_plano, key, val)
    db.commit()
    db.refresh(db_plano)
    return db_plano

@app.delete("/api/planos/{id}", response_model=schemas.Message)
def delete_plano(id: int, db: Session = Depends(get_db)):
    db_plano = db.query(models.Plano).filter(models.Plano.id == id).first()
    if not db_plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
    
    # Dissociate hosts and racks
    db.query(models.Host).filter(models.Host.plano_id == id).update({
        models.Host.plano_id: None,
        models.Host.plano_x: None,
        models.Host.plano_y: None
    })
    db.query(models.Rack).filter(models.Rack.plano_id == id).update({
        models.Rack.plano_id: None,
        models.Rack.plano_x: None,
        models.Rack.plano_y: None
    })
    
    db.delete(db_plano)
    db.commit()
    return {"message": "Plano eliminado correctamente y equipos desvinculados"}

@app.post("/api/planos/{plano_id}/upload")
async def upload_plano_imagen(plano_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    plano = db.query(models.Plano).filter(models.Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
        
    extension = file.filename.split(".")[-1]
    nombre_archivo = f"plano_{plano_id}.{extension}"
    ruta_guardado = os.path.join(settings.UPLOAD_DIR, nombre_archivo)
    with open(ruta_guardado, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    plano.imagen_url = f"/static/{nombre_archivo}"
    db.commit()
    db.refresh(plano)
    return {"message": "Imagen subida exitosamente", "imagen_url": plano.imagen_url}

def serialize_host_for_plano(h):
    tipo = h.tipo_host.nombre if h.tipo_host else "Host"
    return {
        "id": h.id,
        "nombre": h.nombre,
        "ip": h.ip,
        "tipo": tipo,
        "x": h.plano_x,
        "y": h.plano_y,
        "plano_id": h.plano_id,
        "switch_id": h.switch_id,
        "rack_id": h.rack_id,
        "blindobarra_id": h.blindobarra_id
    }

def serialize_rack_for_plano(r):
    return {
        "id": r.id,
        "nombre": r.nombre,
        "tipo": "Rack",
        "x": r.plano_x,
        "y": r.plano_y,
        "plano_id": r.plano_id,
        "ups_id": r.ups_id
    }

@app.get("/api/planos/{plano_id}/items")
def get_plano_items(plano_id: int, db: Session = Depends(get_db)):
    plano = db.query(models.Plano).filter(models.Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
        
    # 1. Get all racks placed on this specific plano
    placed_racks = db.query(models.Rack).filter(models.Rack.plano_id == plano_id).all()
    racks_map = {r.id: serialize_rack_for_plano(r) for r in placed_racks}
    
    all_hosts = db.query(models.Host).all()
    placed_hosts_map = {}
    
    # First pass: explicitly placed hosts on this plano that do NOT have a parent Rack or Switch
    for h in all_hosts:
        if h.plano_id == plano_id and h.rack_id is None and h.switch_id is None:
            placed_hosts_map[h.id] = serialize_host_for_plano(h)
            
    # Iteratively resolve placements for this specific plano
    resolved_any = True
    iterations = 0
    while resolved_any and iterations < 10:
        resolved_any = False
        iterations += 1
        for h in all_hosts:
            if h.id in placed_hosts_map:
                continue
                
            # If parent Rack is placed on this plano, this Host is implicitly placed on this plano
            if h.rack_id and h.rack_id in racks_map:
                parent_rack = racks_map[h.rack_id]
                x = h.plano_x if h.plano_x is not None else (parent_rack["x"] or 100)
                y = h.plano_y if h.plano_y is not None else ((parent_rack["y"] or 100) + 60)
                
                serialized = serialize_host_for_plano(h)
                serialized["x"] = x
                serialized["y"] = y
                serialized["plano_id"] = plano_id
                placed_hosts_map[h.id] = serialized
                resolved_any = True
                
            # If connected Switch is placed on this plano, this Host is implicitly placed on this plano
            elif h.switch_id and h.switch_id in placed_hosts_map:
                parent_switch = placed_hosts_map[h.switch_id]
                x = h.plano_x if h.plano_x is not None else ((parent_switch["x"] or 100) + 60)
                y = h.plano_y if h.plano_y is not None else (parent_switch["y"] or 100)
                
                serialized = serialize_host_for_plano(h)
                serialized["x"] = x
                serialized["y"] = y
                serialized["plano_id"] = plano_id
                placed_hosts_map[h.id] = serialized
                resolved_any = True

    # 2. Find all Racks and Hosts placed on ANY plano to calculate unplaced lists
    all_racks = db.query(models.Rack).all()
    placed_rack_ids_any = {r.id for r in all_racks if r.plano_id is not None}
    
    placed_host_ids_any = {h.id for h in all_hosts if h.plano_id is not None}
    
    resolved_any_global = True
    iterations_global = 0
    while resolved_any_global and iterations_global < 10:
        resolved_any_global = False
        iterations_global += 1
        for h in all_hosts:
            if h.id in placed_host_ids_any:
                continue
            if h.rack_id and h.rack_id in placed_rack_ids_any:
                placed_host_ids_any.add(h.id)
                resolved_any_global = True
            elif h.switch_id and h.switch_id in placed_host_ids_any:
                placed_host_ids_any.add(h.id)
                resolved_any_global = True

    # Calculate unplaced lists (not placed on ANY plano, either explicitly or implicitly)
    unplaced_racks = [serialize_rack_for_plano(r) for r in all_racks if r.id not in placed_rack_ids_any]
    unplaced_hosts = [serialize_host_for_plano(h) for h in all_hosts if h.id not in placed_host_ids_any]
            
    return {
        "placed_hosts": list(placed_hosts_map.values()),
        "placed_racks": list(racks_map.values()),
        "unplaced_hosts": unplaced_hosts,
        "unplaced_racks": unplaced_racks,
    }

@app.post("/api/planos/{plano_id}/posicionar")
def posicionar_plano_items(plano_id: int, request: schemas.PlanoPosicionesRequest, db: Session = Depends(get_db)):
    plano = db.query(models.Plano).filter(models.Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano no encontrado")
        
    # Update racks positions
    for r_pos in request.racks:
        db_rack = db.query(models.Rack).filter(models.Rack.id == r_pos.id).first()
        if db_rack:
            if r_pos.x is None or r_pos.y is None:
                db_rack.plano_id = None
                db_rack.plano_x = None
                db_rack.plano_y = None
            else:
                db_rack.plano_id = plano_id
                db_rack.plano_x = r_pos.x
                db_rack.plano_y = r_pos.y
                
    # Update hosts positions
    for h_pos in request.hosts:
        db_host = db.query(models.Host).filter(models.Host.id == h_pos.id).first()
        if db_host:
            if h_pos.x is None or h_pos.y is None:
                db_host.plano_id = None
                db_host.plano_x = None
                db_host.plano_y = None
            else:
                db_host.plano_id = plano_id
                db_host.plano_x = h_pos.x
                db_host.plano_y = h_pos.y
                
    db.commit()
    return {"message": "Posiciones guardadas correctamente"}


