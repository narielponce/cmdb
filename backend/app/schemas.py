# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# Generic message schema
class Message(BaseModel):
    message: str

# ==================
#    SUBESTACIONES
# ==================
class SubestacionBase(BaseModel):
    nombre: str
    capacidad_kva: Optional[float] = 1000.0
    ubicacion: Optional[str] = "Sector Industrial"

class SubestacionCreate(SubestacionBase):
    pass

class SubestacionUpdate(SubestacionBase):
    nombre: Optional[str] = None

class SubestacionResponse(SubestacionBase):
    id: int
    class Config:
        from_attributes = True

# ==================
#    BLINDOBARRAS
# ==================
class BlindobarraBase(BaseModel):
    nombre: str
    subestacion_id: int
    capacidad_amperios: Optional[int] = 400

class BlindobarraCreate(BlindobarraBase):
    pass

class BlindobarraUpdate(BaseModel):
    nombre: Optional[str] = None
    subestacion_id: Optional[int] = None
    capacidad_amperios: Optional[int] = None

class BlindobarraResponse(BaseModel):
    id: int
    nombre: str
    subestacion_id: int
    subestacion_nombre: Optional[str] = None
    capacidad_amperios: int
    class Config:
        from_attributes = True

# ==================
#        UPS
# ==================
class UPSBase(BaseModel):
    nombre: str
    blindobarra_id: int
    checkmk_host_id: Optional[str] = None
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    serial: Optional[str] = ""
    fecha_fabricacion: Optional[date] = None
    fecha_cambio_baterias: Optional[date] = None
    proximo_cambio_baterias: Optional[date] = None
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = ""
    numero_contrato: Optional[str] = ""
    ip: Optional[str] = ""
    vlan: Optional[str] = ""
    capacidad_kva: Optional[float] = 10.0
    estado_baterias: Optional[str] = "Ok"

class UPSCreate(UPSBase):
    pass

class UPSUpdate(BaseModel):
    nombre: Optional[str] = None
    blindobarra_id: Optional[int] = None
    checkmk_host_id: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serial: Optional[str] = None
    fecha_fabricacion: Optional[date] = None
    fecha_cambio_baterias: Optional[date] = None
    proximo_cambio_baterias: Optional[date] = None
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = None
    numero_contrato: Optional[str] = None
    ip: Optional[str] = None
    vlan: Optional[str] = None
    capacidad_kva: Optional[float] = None
    estado_baterias: Optional[str] = None

class UPSResponse(BaseModel):
    id: int
    nombre: str
    blindobarra_id: Optional[int] = None
    blindobarra_nombre: Optional[str] = None
    checkmk_host_id: Optional[str] = None
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    serial: Optional[str] = ""
    fecha_fabricacion: Optional[date] = None
    fecha_cambio_baterias: Optional[date] = None
    proximo_cambio_baterias: Optional[date] = None
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = ""
    numero_contrato: Optional[str] = ""
    ip: Optional[str] = ""
    vlan: Optional[str] = ""
    capacidad_kva: Optional[float] = 0.0
    estado_baterias: Optional[str] = "Ok"
    class Config:
        from_attributes = True

# ==================
#       RACKS
# ==================
class RackBase(BaseModel):
    nombre: str
    ups_id: int

class RackCreate(RackBase):
    pass

class RackUpdate(BaseModel):
    nombre: Optional[str] = None
    ups_id: Optional[int] = None

class RackResponse(BaseModel):
    id: int
    nombre: str
    ups_id: int
    ups_nombre: Optional[str] = None
    class Config:
        from_attributes = True

# ==================
#     SWITCHES
# ==================
class SwitchBase(BaseModel):
    nombre: str
    ip: Optional[str] = "0.0.0.0"
    checkmk_host_id: Optional[str] = None
    rack_id: Optional[int] = None
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    serial: Optional[str] = ""
    vlan_gestion: Optional[str] = "1"
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = ""
    numero_contrato: Optional[str] = ""

class SwitchCreate(SwitchBase):
    pass

class SwitchUpdate(BaseModel):
    nombre: Optional[str] = None
    ip: Optional[str] = None
    checkmk_host_id: Optional[str] = None
    rack_id: Optional[int] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serial: Optional[str] = None
    vlan_gestion: Optional[str] = None
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = None
    numero_contrato: Optional[str] = None

class SwitchResponse(BaseModel):
    id: int
    nombre: str
    ip: Optional[str] = "0.0.0.0"
    checkmk_host_id: Optional[str] = None
    rack_id: Optional[int] = None
    rack_nombre: Optional[str] = None
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    serial: Optional[str] = ""
    vlan_gestion: Optional[str] = "1"
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = ""
    numero_contrato: Optional[str] = ""
    class Config:
        from_attributes = True

# ==================
#       HOSTS
# ==================
class HostBase(BaseModel):
    nombre: str
    ip: Optional[str] = "0.0.0.0"
    checkmk_host_id: Optional[str] = None
    switch_id: Optional[int] = None
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    serial: Optional[str] = ""
    ubicacion: Optional[str] = ""
    rol: Optional[str] = "Otro"
    puerto_switch: Optional[str] = ""
    sector_planta: Optional[str] = ""
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = ""
    numero_contrato: Optional[str] = ""

class HostCreate(HostBase):
    pass

class HostUpdate(BaseModel):
    nombre: Optional[str] = None
    ip: Optional[str] = None
    checkmk_host_id: Optional[str] = None
    switch_id: Optional[int] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serial: Optional[str] = None
    ubicacion: Optional[str] = None
    rol: Optional[str] = None
    puerto_switch: Optional[str] = None
    sector_planta: Optional[str] = None
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = None
    numero_contrato: Optional[str] = None

class HostResponse(BaseModel):
    id: int
    nombre: str
    ip: Optional[str] = "0.0.0.0"
    checkmk_host_id: Optional[str] = None
    switch_id: Optional[int] = None
    switch_nombre: Optional[str] = None
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    serial: Optional[str] = ""
    ubicacion: Optional[str] = ""
    rol: Optional[str] = "Otro"
    puerto_switch: Optional[str] = None
    sector_planta: Optional[str] = None
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = ""
    numero_contrato: Optional[str] = ""
    class Config:
        from_attributes = True

# ==================
#    SERVIDORES
# ==================
class ServidorBase(BaseModel):
    nombre: str
    switch_id: Optional[int] = None
    checkmk_host_id: Optional[str] = None
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    serial: Optional[str] = ""
    ip: Optional[str] = "0.0.0.0"
    tipo_servidor: Optional[str] = "Virtual (VM)"
    sistema_operativo: Optional[str] = "Linux RHEL"
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = ""
    numero_contrato: Optional[str] = ""

class ServidorCreate(ServidorBase):
    pass

class ServidorUpdate(BaseModel):
    nombre: Optional[str] = None
    switch_id: Optional[int] = None
    checkmk_host_id: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serial: Optional[str] = None
    ip: Optional[str] = None
    tipo_servidor: Optional[str] = None
    sistema_operativo: Optional[str] = None
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = None
    numero_contrato: Optional[str] = None

class ServidorResponse(BaseModel):
    id: int
    nombre: str
    switch_id: Optional[int] = None
    switch_nombre: Optional[str] = None
    checkmk_host_id: Optional[str] = None
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    serial: Optional[str] = ""
    ip: Optional[str] = "0.0.0.0"
    tipo_servidor: Optional[str] = "Virtual (VM)"
    sistema_operativo: Optional[str] = "Linux RHEL"
    fecha_instalacion: Optional[date] = None
    ultimo_mantenimiento: Optional[date] = None
    proximo_mantenimiento: Optional[date] = None
    fecha_eol: Optional[date] = None
    fin_garantia_contrato: Optional[date] = None
    proveedor_soporte: Optional[str] = ""
    numero_contrato: Optional[str] = ""
    class Config:
        from_attributes = True

# ==================
#   APLICACIONES
# ==================
class AplicacionBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = ""
    owner_negocio: Optional[str] = ""

class AplicacionCreate(AplicacionBase):
    pass

class AplicacionUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    owner_negocio: Optional[str] = None

class AplicacionResponse(AplicacionBase):
    id: int
    class Config:
        from_attributes = True

# ==================
#   DEPENDENCIAS
# ==================
class DependenciaBase(BaseModel):
    app_id: int
    servidor_id: int
    rol_servidor: Optional[str] = ""

class DependenciaCreate(DependenciaBase):
    pass

class DependenciaUpdate(BaseModel):
    app_id: Optional[int] = None
    servidor_id: Optional[int] = None
    rol_servidor: Optional[str] = None

class DependenciaResponse(BaseModel):
    id: int
    app_id: int
    app_nombre: Optional[str] = None
    servidor_id: int
    servidor_nombre: Optional[str] = None
    rol_servidor: Optional[str] = ""
    class Config:
        from_attributes = True

# ==================
#    PROCESOS
# ==================
class ProcesoBase(BaseModel):
    nombre_proceso: str
    linea_produccion: Optional[str] = ""
    aplicacion_id: int

class ProcesoCreate(ProcesoBase):
    pass

class ProcesoUpdate(BaseModel):
    nombre_proceso: Optional[str] = None
    linea_produccion: Optional[str] = None
    aplicacion_id: Optional[int] = None

class ProcesoResponse(BaseModel):
    id: int
    nombre_proceso: str
    linea_produccion: str
    aplicacion_id: int
    app_nombre: Optional[str] = None
    class Config:
        from_attributes = True

# ==================
#    CATALOGO
# ==================
class CatalogoBase(BaseModel):
    marca: str
    modelo: str
    tipo: str
    serializado: Optional[int] = 1

class CatalogoCreate(CatalogoBase):
    pass

class CatalogoResponse(CatalogoBase):
    id: int
    class Config:
        from_attributes = True

# ==================
#   CONSUMIBLES
# ==================
class ConsumibleBase(BaseModel):
    catalogo_id: int
    cantidad: Optional[int] = 0
    ubicacion: Optional[str] = "Depósito Principal"
    stock_minimo: Optional[int] = 5

class ConsumibleCreate(ConsumibleBase):
    pass

class ConsumibleUpdate(BaseModel):
    catalogo_id: Optional[int] = None
    cantidad: Optional[int] = None
    ubicacion: Optional[str] = None
    stock_minimo: Optional[int] = None

# Custom response showing flat items directly to match streamlit df
class ConsumibleResponse(BaseModel):
    id: int
    catalogo_id: int
    marca: str
    modelo: str
    tipo: str
    cantidad: int
    ubicacion: str
    stock_minimo: int
    class Config:
        from_attributes = True

# ==================
#   HISTORIAL
# ==================
class HistorialResponse(BaseModel):
    id: int
    fecha: datetime
    operador: str
    tipo_movimiento: str
    referencia_id: int
    tabla_referencia: str
    detalle: Optional[str] = ""
    class Config:
        from_attributes = True

# ==================
#   ITAM CUSTOM SCHEMAS
# ==================
class ConsolidadoAssetResponse(BaseModel):
    tipo_equipo: str
    nombre: str
    marca: str
    modelo: str
    serial: str
    ip: str
    ubicacion_estado: str

class DeployAssetRequest(BaseModel):
    tipo_equipo: str  # "🔌 Switch", "🔋 UPS", "📶 Access Point", "📷 Cámara IP", "⚙️ Host Industrial"
    nombre: str
    destino_id: int
    operador: str
    responsable: str

class SalidaConsumibleRequest(BaseModel):
    consumible_id: int
    cantidad: int
    operador: str
    responsable: str

# ==================
#  SIMULATOR SCHEMAS
# ==================
class SimuUPSResult(BaseModel):
    racks: List[dict]
    switches: List[dict]
    hosts: List[dict]

class SimuRackResult(BaseModel):
    switches: List[dict]
    hosts: List[dict]

class SimuServidorResult(BaseModel):
    aplicaciones: List[dict]
    procesos: List[dict]

class SimulationRequest(BaseModel):
    tipo_corte: str # "UPS", "Rack", "Servidor (Mantenimiento TI)"
    target_id: int

# ==================
#   SUPPORT TABLES
# ==================
class MarcaCreate(BaseModel):
    nombre: str

class MarcaUpdate(BaseModel):
    nombre: str

class MarcaResponse(BaseModel):
    id: int
    nombre: str
    class Config:
        from_attributes = True

class EstadoCreate(BaseModel):
    nombre: str

class EstadoUpdate(BaseModel):
    nombre: str

class EstadoResponse(BaseModel):
    id: int
    nombre: str
    class Config:
        from_attributes = True

class TipoHostCreate(BaseModel):
    nombre: str

class TipoHostUpdate(BaseModel):
    nombre: str

class TipoHostResponse(BaseModel):
    id: int
    nombre: str
    class Config:
        from_attributes = True

class TipoServidorCreate(BaseModel):
    nombre: str

class TipoServidorUpdate(BaseModel):
    nombre: str

class TipoServidorResponse(BaseModel):
    id: int
    nombre: str
    class Config:
        from_attributes = True

# ==================
#    SEGURIDAD
# ==================
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    nombre: str
    is_superadmin: bool
    role_nombre: Optional[str] = None
    modules: List[dict]

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    nombre: str
    password: str
    role_id: Optional[int] = None
    is_superadmin: Optional[bool] = False

class UserUpdate(BaseModel):
    username: Optional[str] = None
    nombre: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    is_superadmin: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    nombre: str
    role_id: Optional[int] = None
    role_nombre: Optional[str] = None
    is_superadmin: bool
    class Config:
        from_attributes = True

class RoleModuleBase(BaseModel):
    module_name: str
    can_read: Optional[bool] = True
    can_write: Optional[bool] = False

class RoleModuleCreate(RoleModuleBase):
    pass

class RoleModuleUpdate(BaseModel):
    can_read: Optional[bool] = None
    can_write: Optional[bool] = None

class RoleModuleResponse(RoleModuleBase):
    id: int
    role_id: int
    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = ""

class RoleUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class RoleResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = ""
    modules: List[RoleModuleResponse] = []
    class Config:
        from_attributes = True


# ==================
#       PLANOS
# ==================
class PlanoBase(BaseModel):
    nombre: str
    ancho: Optional[int] = 800
    alto: Optional[int] = 600

class PlanoCreate(PlanoBase):
    pass

class PlanoUpdate(BaseModel):
    nombre: Optional[str] = None
    ancho: Optional[int] = None
    alto: Optional[int] = None

class PlanoResponse(PlanoBase):
    id: int
    imagen_url: Optional[str] = None
    class Config:
        from_attributes = True

class ItemPosition(BaseModel):
    id: int
    x: Optional[float] = None
    y: Optional[float] = None

class PlanoPosicionesRequest(BaseModel):
    racks: List[ItemPosition] = []
    hosts: List[ItemPosition] = []


