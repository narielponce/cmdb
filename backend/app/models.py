from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Plano(Base):
    __tablename__ = "planos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    imagen_url = Column(String, nullable=True)
    ancho = Column(Integer, default=800)
    alto = Column(Integer, default=600)
    
    hosts = relationship("Host", back_populates="plano", foreign_keys="Host.plano_id")
    racks = relationship("Rack", back_populates="plano", foreign_keys="Rack.plano_id")

class Marca(Base):
    __tablename__ = "marcas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

class Estado(Base):
    __tablename__ = "estados"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

class TipoHost(Base):
    __tablename__ = "tipos_host"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False) # "UPS", "Switch", "Host", "Servidor"

class TipoServidor(Base):
    __tablename__ = "tipos_servidor"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False) # "Físico", "Virtual (VM)", "Contenedor"

class Subestacion(Base):
    __tablename__ = "subestaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    capacidad_kva = Column(Float, default=1000.0)
    ubicacion = Column(String, default="Sector Industrial")
    
    blindobarras = relationship("Blindobarra", back_populates="subestacion", cascade="all, delete-orphan")

class Blindobarra(Base):
    __tablename__ = "blindobarras"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    subestacion_id = Column(Integer, ForeignKey("subestaciones.id", ondelete="CASCADE"), nullable=False)
    capacidad_amperios = Column(Integer, default=400)
    
    subestacion = relationship("Subestacion", back_populates="blindobarras")
    hosts = relationship("Host", back_populates="blindobarra")

class Host(Base):
    __tablename__ = "hosts"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    checkmk_host_id = Column(String, unique=True, index=True, nullable=True)
    
    # FKs to support tables
    tipo_host_id = Column(Integer, ForeignKey("tipos_host.id", ondelete="RESTRICT"), nullable=False)
    marca_id = Column(Integer, ForeignKey("marcas.id", ondelete="SET NULL"), nullable=True)
    estado_id = Column(Integer, ForeignKey("estados.id", ondelete="SET NULL"), nullable=True)
    tipo_servidor_id = Column(Integer, ForeignKey("tipos_servidor.id", ondelete="SET NULL"), nullable=True)
    
    # Generic and specific fields (all inside unified hosts table)
    modelo = Column(String, default="")
    serial = Column(String, default="")
    ip = Column(String, default="0.0.0.0")
    vlan = Column(String, default="1")
    
    # Physical/Logical associations
    rack_id = Column(Integer, ForeignKey("racks.id", ondelete="SET NULL", use_alter=True, name="fk_host_rack_id"), nullable=True)
    switch_id = Column(Integer, ForeignKey("hosts.id", ondelete="SET NULL"), nullable=True)
    puerto_switch = Column(String, default="")
    blindobarra_id = Column(Integer, ForeignKey("blindobarras.id", ondelete="SET NULL"), nullable=True)
    
    # Plano positioning fields
    plano_id = Column(Integer, ForeignKey("planos.id", ondelete="SET NULL"), nullable=True)
    plano_x = Column(Float, nullable=True)
    plano_y = Column(Float, nullable=True)
    
    # Specific fields
    capacidad_kva = Column(Float, nullable=True) # for UPS
    fecha_fabricacion = Column(Date, nullable=True) # for UPS
    fecha_cambio_baterias = Column(Date, nullable=True) # for UPS
    proximo_cambio_baterias = Column(Date, nullable=True) # for UPS
    fecha_instalacion = Column(Date, nullable=True)
    ultimo_mantenimiento = Column(Date, nullable=True)
    proximo_mantenimiento = Column(Date, nullable=True)
    fecha_eol = Column(Date, nullable=True)
    fin_garantia_contrato = Column(Date, nullable=True)
    proveedor_soporte = Column(String, default="")
    numero_contrato = Column(String, default="")
    sistema_operativo = Column(String, nullable=True) # for Servidor
    ubicacion = Column(String, default="") # for Host/UPS
    rol = Column(String, default="Otro") # for Host
    dominio = Column(String, default="NETWORK", nullable=False)
    
    # Relationships
    tipo_host = relationship("TipoHost")
    marca = relationship("Marca")
    estado = relationship("Estado")
    tipo_servidor = relationship("TipoServidor")
    rack = relationship("Rack", back_populates="hosts", foreign_keys=[rack_id])
    blindobarra = relationship("Blindobarra", back_populates="hosts")
    plano = relationship("Plano", back_populates="hosts", foreign_keys=[plano_id])
    
    # Self referential switch connection
    switch = relationship("Host", remote_side=[id], backref="hosts_conectados", foreign_keys=[switch_id])
    
    # Dependencias
    dependencias = relationship("DependenciaAppHost", back_populates="host", cascade="all, delete-orphan")

class Rack(Base):
    __tablename__ = "racks"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    ups_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False)
    
    # Plano positioning fields
    plano_id = Column(Integer, ForeignKey("planos.id", ondelete="SET NULL"), nullable=True)
    plano_x = Column(Float, nullable=True)
    plano_y = Column(Float, nullable=True)
    
    # A rack is fed by a Host (which must be a UPS)
    ups = relationship("Host", foreign_keys=[ups_id])
    hosts = relationship("Host", back_populates="rack", foreign_keys=[Host.rack_id])
    plano = relationship("Plano", back_populates="racks", foreign_keys=[plano_id])

class Aplicacion(Base):
    __tablename__ = "aplicaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    descripcion = Column(String, default="")
    owner_negocio = Column(String, default="")
    
    hosts_dep = relationship("DependenciaAppHost", back_populates="aplicacion", cascade="all, delete-orphan")
    procesos = relationship("ProcesoPlanta", back_populates="aplicacion", cascade="all, delete-orphan")

class DependenciaAppHost(Base):
    __tablename__ = "dependencias_app_servidor"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("aplicaciones.id", ondelete="CASCADE"), nullable=False)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False)
    rol_servidor = Column(String, nullable=True)
    
    aplicacion = relationship("Aplicacion", back_populates="hosts_dep")
    host = relationship("Host", back_populates="dependencias")

class ProcesoPlanta(Base):
    __tablename__ = "procesos_planta"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_proceso = Column(String, nullable=False)
    linea_produccion = Column(String, default="")
    aplicacion_id = Column(Integer, ForeignKey("aplicaciones.id", ondelete="CASCADE"), nullable=False)
    
    aplicacion = relationship("Aplicacion", back_populates="procesos")

class CatalogoEquipo(Base):
    __tablename__ = "catalogo_equipos"
    
    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    serializado = Column(Integer, default=1)
    
    consumibles = relationship("StockConsumible", back_populates="catalogo", cascade="all, delete-orphan")

class StockConsumible(Base):
    __tablename__ = "stock_consumibles"
    
    id = Column(Integer, primary_key=True, index=True)
    catalogo_id = Column(Integer, ForeignKey("catalogo_equipos.id", ondelete="CASCADE"), nullable=False)
    cantidad = Column(Integer, default=0)
    ubicacion = Column(String, default="Depósito Principal")
    stock_minimo = Column(Integer, default=5)
    dominio = Column(String, default="NETWORK", nullable=False)
    
    catalogo = relationship("CatalogoEquipo", back_populates="consumibles")

class HistoricoMovimiento(Base):
    __tablename__ = "historico_movimientos"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=func.now())
    operador = Column(String, nullable=False)
    tipo_movimiento = Column(String, nullable=False)
    referencia_id = Column(Integer, nullable=False)
    tabla_referencia = Column(String, nullable=False)
    detalle = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    is_superadmin = Column(Boolean, default=False)
    dominio_asignado = Column(String, default="ALL", nullable=False)
    
    role = relationship("Role", back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    descripcion = Column(String, nullable=True)
    
    users = relationship("User", back_populates="role")
    modules = relationship("RoleModule", back_populates="role", cascade="all, delete-orphan")

class RoleModule(Base):
    __tablename__ = "role_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    module_name = Column(String, nullable=False)
    can_read = Column(Boolean, default=True)
    can_write = Column(Boolean, default=False)
    
    role = relationship("Role", back_populates="modules")

class Mantenimiento(Base):
    __tablename__ = "mantenimientos"
    
    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tipo = Column(String, nullable=False) # 'PREVENTIVO', 'CORRECTIVO', 'CAMBIO_BATERIA'
    fecha_ejecucion = Column(DateTime, default=func.now())
    descripcion_trabajo = Column(String, nullable=False)
    tecnico_responsable = Column(String, nullable=False)
    costo = Column(Float, nullable=True)
    proxima_fecha_sugerida = Column(Date, nullable=True)
    
    host = relationship("Host")
    usuario = relationship("User")
