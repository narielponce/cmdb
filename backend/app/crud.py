# backend/app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from . import models, schemas
from typing import Optional, List

# ==================
#   SUPPORT HELPERS
# ==================
def get_or_create_marca(db: Session, nombre: str) -> Optional[int]:
    if not nombre or not nombre.strip():
        return None
    nombre = nombre.strip()
    db_marca = db.query(models.Marca).filter(func.lower(models.Marca.nombre) == func.lower(nombre)).first()
    if not db_marca:
        db_marca = models.Marca(nombre=nombre)
        db.add(db_marca)
        db.commit()
        db.refresh(db_marca)
    return db_marca.id

def get_or_create_estado(db: Session, nombre: str) -> Optional[int]:
    if not nombre or not nombre.strip():
        return None
    nombre = nombre.strip()
    db_estado = db.query(models.Estado).filter(func.lower(models.Estado.nombre) == func.lower(nombre)).first()
    if not db_estado:
        db_estado = models.Estado(nombre=nombre)
        db.add(db_estado)
        db.commit()
        db.refresh(db_estado)
    return db_estado.id

def get_or_create_tipo_host(db: Session, nombre: str) -> int:
    nombre = nombre.strip()
    db_type = db.query(models.TipoHost).filter(func.lower(models.TipoHost.nombre) == func.lower(nombre)).first()
    if not db_type:
        db_type = models.TipoHost(nombre=nombre)
        db.add(db_type)
        db.commit()
        db.refresh(db_type)
    return db_type.id

def get_or_create_tipo_servidor(db: Session, nombre: str) -> Optional[int]:
    if not nombre or not nombre.strip():
        return None
    nombre = nombre.strip()
    db_type = db.query(models.TipoServidor).filter(func.lower(models.TipoServidor.nombre) == func.lower(nombre)).first()
    if not db_type:
        db_type = models.TipoServidor(nombre=nombre)
        db.add(db_type)
        db.commit()
        db.refresh(db_type)
    return db_type.id

# ==================
#   SUPPORT CRUD
# ==================
# CRUD for Marca
def get_marcas(db: Session):
    return db.query(models.Marca).order_by(models.Marca.nombre.asc()).all()

def get_marca(db: Session, m_id: int):
    return db.query(models.Marca).filter(models.Marca.id == m_id).first()

def create_marca(db: Session, m: schemas.MarcaCreate):
    db_marca = models.Marca(**m.dict())
    db.add(db_marca)
    db.commit()
    db.refresh(db_marca)
    return db_marca

def update_marca(db: Session, m_id: int, m: schemas.MarcaUpdate):
    db_marca = get_marca(db, m_id)
    if not db_marca:
        return None
    for key, value in m.dict(exclude_unset=True).items():
        setattr(db_marca, key, value)
    db.commit()
    db.refresh(db_marca)
    return db_marca

def delete_marca(db: Session, m_id: int):
    db_marca = get_marca(db, m_id)
    if not db_marca:
        return False
    db.delete(db_marca)
    db.commit()
    return True

# CRUD for Estado
def get_estados(db: Session):
    return db.query(models.Estado).order_by(models.Estado.nombre.asc()).all()

def get_estado(db: Session, e_id: int):
    return db.query(models.Estado).filter(models.Estado.id == e_id).first()

def create_estado(db: Session, e: schemas.EstadoCreate):
    db_estado = models.Estado(**e.dict())
    db.add(db_estado)
    db.commit()
    db.refresh(db_estado)
    return db_estado

def update_estado(db: Session, e_id: int, e: schemas.EstadoUpdate):
    db_estado = get_estado(db, e_id)
    if not db_estado:
        return None
    for key, value in e.dict(exclude_unset=True).items():
        setattr(db_estado, key, value)
    db.commit()
    db.refresh(db_estado)
    return db_estado

def delete_estado(db: Session, e_id: int):
    db_estado = get_estado(db, e_id)
    if not db_estado:
        return False
    db.delete(db_estado)
    db.commit()
    return True

# CRUD for TipoHost
def get_tipos_host(db: Session):
    return db.query(models.TipoHost).order_by(models.TipoHost.nombre.asc()).all()

def get_tipo_host(db: Session, th_id: int):
    return db.query(models.TipoHost).filter(models.TipoHost.id == th_id).first()

def create_tipo_host(db: Session, th: schemas.TipoHostCreate):
    db_type = models.TipoHost(**th.dict())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

def update_tipo_host(db: Session, th_id: int, th: schemas.TipoHostUpdate):
    db_type = get_tipo_host(db, th_id)
    if not db_type:
        return None
    for key, value in th.dict(exclude_unset=True).items():
        setattr(db_type, key, value)
    db.commit()
    db.refresh(db_type)
    return db_type

def delete_tipo_host(db: Session, th_id: int):
    db_type = get_tipo_host(db, th_id)
    if not db_type:
        return False
    db.delete(db_type)
    db.commit()
    return True

# CRUD for TipoServidor
def get_tipos_servidor(db: Session):
    return db.query(models.TipoServidor).order_by(models.TipoServidor.nombre.asc()).all()

def get_tipo_servidor(db: Session, ts_id: int):
    return db.query(models.TipoServidor).filter(models.TipoServidor.id == ts_id).first()

def create_tipo_servidor(db: Session, ts: schemas.TipoServidorCreate):
    db_type = models.TipoServidor(**ts.dict())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

def update_tipo_servidor(db: Session, ts_id: int, ts: schemas.TipoServidorUpdate):
    db_type = get_tipo_servidor(db, ts_id)
    if not db_type:
        return None
    for key, value in ts.dict(exclude_unset=True).items():
        setattr(db_type, key, value)
    db.commit()
    db.refresh(db_type)
    return db_type

def delete_tipo_servidor(db: Session, ts_id: int):
    db_type = get_tipo_servidor(db, ts_id)
    if not db_type:
        return False
    db.delete(db_type)
    db.commit()
    return True

# ==================
#    SUBESTACIONES
# ==================
def get_subestaciones(db: Session):
    return db.query(models.Subestacion).order_by(models.Subestacion.nombre.asc()).all()

def get_subestacion(db: Session, sub_id: int):
    return db.query(models.Subestacion).filter(models.Subestacion.id == sub_id).first()

def create_subestacion(db: Session, sub: schemas.SubestacionCreate):
    db_sub = models.Subestacion(**sub.dict())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

def update_subestacion(db: Session, sub_id: int, sub: schemas.SubestacionUpdate):
    db_sub = get_subestacion(db, sub_id)
    if not db_sub:
        return None
    for key, value in sub.dict(exclude_unset=True).items():
        setattr(db_sub, key, value)
    db.commit()
    db.refresh(db_sub)
    return db_sub

def delete_subestacion(db: Session, sub_id: int):
    db_sub = get_subestacion(db, sub_id)
    if not db_sub:
        return False
    db.delete(db_sub)
    db.commit()
    return True


# ==================
#    BLINDOBARRAS
# ==================
def get_blindobarras(db: Session):
    results = db.query(models.Blindobarra).order_by(models.Blindobarra.nombre.asc()).all()
    for b in results:
        b.subestacion_nombre = b.subestacion.nombre if b.subestacion else None
    return results

def get_blindobarra(db: Session, bb_id: int):
    return db.query(models.Blindobarra).filter(models.Blindobarra.id == bb_id).first()

def create_blindobarra(db: Session, bb: schemas.BlindobarraCreate):
    db_bb = models.Blindobarra(**bb.dict())
    db.add(db_bb)
    db.commit()
    db.refresh(db_bb)
    db_bb.subestacion_nombre = db_bb.subestacion.nombre if db_bb.subestacion else None
    return db_bb

def update_blindobarra(db: Session, bb_id: int, bb: schemas.BlindobarraUpdate):
    db_bb = get_blindobarra(db, bb_id)
    if not db_bb:
        return None
    for key, value in bb.dict(exclude_unset=True).items():
        setattr(db_bb, key, value)
    db.commit()
    db.refresh(db_bb)
    db_bb.subestacion_nombre = db_bb.subestacion.nombre if db_bb.subestacion else None
    return db_bb

def delete_blindobarra(db: Session, bb_id: int):
    db_bb = get_blindobarra(db, bb_id)
    if not db_bb:
        return False
    db.delete(db_bb)
    db.commit()
    return True


# ==================
#        UPS
# ==================
def get_ups_all(db: Session):
    results = db.query(models.Host).join(models.TipoHost).filter(models.TipoHost.nombre == "UPS").order_by(models.Host.nombre.asc()).all()
    mapped = []
    for u in results:
        mapped.append({
            "id": u.id,
            "nombre": u.nombre,
            "blindobarra_id": u.blindobarra_id,
            "blindobarra_nombre": u.blindobarra.nombre if u.blindobarra else None,
            "marca": u.marca.nombre if u.marca else "",
            "modelo": u.modelo,
            "serial": u.serial,
            "fecha_fabricacion": u.fecha_fabricacion,
            "fecha_cambio_baterias": u.fecha_cambio_baterias,
            "ip": u.ip,
            "vlan": u.vlan,
            "capacidad_kva": u.capacidad_kva or 0.0,
            "estado_baterias": u.estado.nombre if u.estado else "Ok",
            "checkmk_host_id": u.checkmk_host_id,
            "proximo_cambio_baterias": u.proximo_cambio_baterias,
            "fecha_instalacion": u.fecha_instalacion,
            "ultimo_mantenimiento": u.ultimo_mantenimiento,
            "proximo_mantenimiento": u.proximo_mantenimiento,
            "fecha_eol": u.fecha_eol,
            "fin_garantia_contrato": u.fin_garantia_contrato,
            "proveedor_soporte": u.proveedor_soporte or "",
            "numero_contrato": u.numero_contrato or ""
        })
    return mapped

def get_ups(db: Session, ups_id: int):
    u = db.query(models.Host).filter(models.Host.id == ups_id).first()
    if u:
        return {
            "id": u.id,
            "nombre": u.nombre,
            "blindobarra_id": u.blindobarra_id,
            "blindobarra_nombre": u.blindobarra.nombre if u.blindobarra else None,
            "marca": u.marca.nombre if u.marca else "",
            "modelo": u.modelo,
            "serial": u.serial,
            "fecha_fabricacion": u.fecha_fabricacion,
            "fecha_cambio_baterias": u.fecha_cambio_baterias,
            "proximo_cambio_baterias": u.proximo_cambio_baterias,
            "fecha_instalacion": u.fecha_instalacion,
            "ultimo_mantenimiento": u.ultimo_mantenimiento,
            "proximo_mantenimiento": u.proximo_mantenimiento,
            "fecha_eol": u.fecha_eol,
            "fin_garantia_contrato": u.fin_garantia_contrato,
            "proveedor_soporte": u.proveedor_soporte or "",
            "numero_contrato": u.numero_contrato or "",
            "ip": u.ip,
            "vlan": u.vlan,
            "capacidad_kva": u.capacidad_kva or 0.0,
            "estado_baterias": u.estado.nombre if u.estado else "Ok",
            "checkmk_host_id": u.checkmk_host_id
        }
    return None

def create_ups(db: Session, ups: schemas.UPSCreate):
    tipo_id = get_or_create_tipo_host(db, "UPS")
    marca_id = get_or_create_marca(db, ups.marca)
    estado_id = get_or_create_estado(db, ups.estado_baterias)
    
    data = ups.dict(exclude={"marca", "estado_baterias"})
    db_ups = models.Host(
        **data,
        tipo_host_id=tipo_id,
        marca_id=marca_id,
        estado_id=estado_id
    )
    db.add(db_ups)
    db.commit()
    db.refresh(db_ups)
    return get_ups(db, db_ups.id)

def update_ups(db: Session, ups_id: int, ups: schemas.UPSUpdate):
    db_ups = db.query(models.Host).filter(models.Host.id == ups_id).first()
    if not db_ups:
        return None
    
    update_data = ups.dict(exclude_unset=True)
    if "marca" in update_data:
        db_ups.marca_id = get_or_create_marca(db, update_data.pop("marca"))
    if "estado_baterias" in update_data:
        db_ups.estado_id = get_or_create_estado(db, update_data.pop("estado_baterias"))
        
    for key, value in update_data.items():
        setattr(db_ups, key, value)
        
    db.commit()
    db.refresh(db_ups)
    return get_ups(db, db_ups.id)

def delete_ups(db: Session, ups_id: int):
    db_ups = db.query(models.Host).filter(models.Host.id == ups_id).first()
    if not db_ups:
        return False
    db.delete(db_ups)
    db.commit()
    return True


# ==================
#       RACKS
# ==================
def get_racks(db: Session):
    results = db.query(models.Rack).order_by(models.Rack.nombre.asc()).all()
    for r in results:
        r.ups_nombre = r.ups.nombre if r.ups else None
    return results

def get_rack(db: Session, rack_id: int):
    return db.query(models.Rack).filter(models.Rack.id == rack_id).first()

def create_rack(db: Session, r: schemas.RackCreate):
    db_r = models.Rack(**r.dict())
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    db_r.ups_nombre = db_r.ups.nombre if db_r.ups else None
    return db_r

def update_rack(db: Session, rack_id: int, r: schemas.RackUpdate):
    db_r = get_rack(db, rack_id)
    if not db_r:
        return None
    for key, value in r.dict(exclude_unset=True).items():
        setattr(db_r, key, value)
    db.commit()
    db.refresh(db_r)
    db_r.ups_nombre = db_r.ups.nombre if db_r.ups else None
    return db_r

def delete_rack(db: Session, rack_id: int):
    db_r = get_rack(db, rack_id)
    if not db_r:
        return False
    db.delete(db_r)
    db.commit()
    return True


# ==================
#     SWITCHES
# ==================
def get_switches(db: Session):
    results = db.query(models.Host).join(models.TipoHost).filter(models.TipoHost.nombre == "Switch").order_by(models.Host.nombre.asc()).all()
    mapped = []
    for s in results:
        mapped.append({
            "id": s.id,
            "nombre": s.nombre,
            "ip": s.ip,
            "rack_id": s.rack_id,
            "rack_nombre": s.rack.nombre if s.rack else "",
            "marca": s.marca.nombre if s.marca else "",
            "modelo": s.modelo,
            "serial": s.serial,
            "vlan_gestion": s.vlan,
            "checkmk_host_id": s.checkmk_host_id,
            "fecha_instalacion": s.fecha_instalacion,
            "ultimo_mantenimiento": s.ultimo_mantenimiento,
            "proximo_mantenimiento": s.proximo_mantenimiento,
            "fecha_eol": s.fecha_eol,
            "fin_garantia_contrato": s.fin_garantia_contrato,
            "proveedor_soporte": s.proveedor_soporte or "",
            "numero_contrato": s.numero_contrato or ""
        })
    return mapped

def get_switch(db: Session, sw_id: int):
    s = db.query(models.Host).filter(models.Host.id == sw_id).first()
    if s:
        return {
            "id": s.id,
            "nombre": s.nombre,
            "ip": s.ip,
            "rack_id": s.rack_id,
            "rack_nombre": s.rack.nombre if s.rack else "",
            "marca": s.marca.nombre if s.marca else "",
            "modelo": s.modelo,
            "serial": s.serial,
            "vlan_gestion": s.vlan,
            "checkmk_host_id": s.checkmk_host_id,
            "fecha_instalacion": s.fecha_instalacion,
            "ultimo_mantenimiento": s.ultimo_mantenimiento,
            "proximo_mantenimiento": s.proximo_mantenimiento,
            "fecha_eol": s.fecha_eol,
            "fin_garantia_contrato": s.fin_garantia_contrato,
            "proveedor_soporte": s.proveedor_soporte or "",
            "numero_contrato": s.numero_contrato or ""
        }
    return None

def create_switch(db: Session, sw: schemas.SwitchCreate):
    tipo_id = get_or_create_tipo_host(db, "Switch")
    marca_id = get_or_create_marca(db, sw.marca)
    
    data = sw.dict(exclude={"marca", "vlan_gestion"})
    db_sw = models.Host(
        **data,
        tipo_host_id=tipo_id,
        marca_id=marca_id,
        vlan=sw.vlan_gestion
    )
    db.add(db_sw)
    db.commit()
    db.refresh(db_sw)
    return get_switch(db, db_sw.id)

def update_switch(db: Session, sw_id: int, sw: schemas.SwitchUpdate):
    db_sw = db.query(models.Host).filter(models.Host.id == sw_id).first()
    if not db_sw:
        return None
    
    update_data = sw.dict(exclude_unset=True)
    if "marca" in update_data:
        db_sw.marca_id = get_or_create_marca(db, update_data.pop("marca"))
    if "vlan_gestion" in update_data:
        db_sw.vlan = update_data.pop("vlan_gestion")
        
    for key, value in update_data.items():
        setattr(db_sw, key, value)
        
    db.commit()
    db.refresh(db_sw)
    return get_switch(db, db_sw.id)

def delete_switch(db: Session, sw_id: int):
    db_sw = db.query(models.Host).filter(models.Host.id == sw_id).first()
    if not db_sw:
        return False
    db.delete(db_sw)
    db.commit()
    return True


# ==================
#       HOSTS
# ==================
def get_hosts(db: Session):
    results = db.query(models.Host).join(models.TipoHost).filter(~models.TipoHost.nombre.in_(["UPS", "Switch", "Servidor"])).order_by(models.Host.nombre.asc()).all()
    mapped = []
    for h in results:
        mapped.append({
            "id": h.id,
            "nombre": h.nombre,
            "ip": h.ip,
            "switch_id": h.switch_id,
            "switch_nombre": h.switch.nombre if h.switch else "",
            "marca": h.marca.nombre if h.marca else "",
            "modelo": h.modelo,
            "serial": h.serial,
            "ubicacion": h.ubicacion,
            "rol": h.tipo_host.nombre if h.tipo_host else "Host",
            "puerto_switch": h.puerto_switch,
            "sector_planta": h.ubicacion,
            "checkmk_host_id": h.checkmk_host_id,
            "fecha_instalacion": h.fecha_instalacion,
            "ultimo_mantenimiento": h.ultimo_mantenimiento,
            "proximo_mantenimiento": h.proximo_mantenimiento,
            "fecha_eol": h.fecha_eol,
            "fin_garantia_contrato": h.fin_garantia_contrato,
            "proveedor_soporte": h.proveedor_soporte or "",
            "numero_contrato": h.numero_contrato or ""
        })
    return mapped

def get_host(db: Session, host_id: int):
    h = db.query(models.Host).filter(models.Host.id == host_id).first()
    if h:
        return {
            "id": h.id,
            "nombre": h.nombre,
            "ip": h.ip,
            "switch_id": h.switch_id,
            "switch_nombre": h.switch.nombre if h.switch else "",
            "marca": h.marca.nombre if h.marca else "",
            "modelo": h.modelo,
            "serial": h.serial,
            "ubicacion": h.ubicacion,
            "rol": h.tipo_host.nombre if h.tipo_host else "Host",
            "puerto_switch": h.puerto_switch,
            "sector_planta": h.ubicacion,
            "checkmk_host_id": h.checkmk_host_id,
            "fecha_instalacion": h.fecha_instalacion,
            "ultimo_mantenimiento": h.ultimo_mantenimiento,
            "proximo_mantenimiento": h.proximo_mantenimiento,
            "fecha_eol": h.fecha_eol,
            "fin_garantia_contrato": h.fin_garantia_contrato,
            "proveedor_soporte": h.proveedor_soporte or "",
            "numero_contrato": h.numero_contrato or ""
        }
    return None

def create_host(db: Session, h: schemas.HostCreate):
    rol_val = h.rol or "Host"
    tipo_id = get_or_create_tipo_host(db, rol_val)
    marca_id = get_or_create_marca(db, h.marca)
    
    data = h.dict(exclude={"marca", "sector_planta", "rol"})
    db_h = models.Host(
        **data,
        tipo_host_id=tipo_id,
        marca_id=marca_id,
        rol=rol_val
    )
    db.add(db_h)
    db.commit()
    db.refresh(db_h)
    return get_host(db, db_h.id)

def update_host(db: Session, host_id: int, h: schemas.HostUpdate):
    db_h = db.query(models.Host).filter(models.Host.id == host_id).first()
    if not db_h:
        return None
    
    update_data = h.dict(exclude_unset=True)
    if "marca" in update_data:
        db_h.marca_id = get_or_create_marca(db, update_data.pop("marca"))
    if "sector_planta" in update_data:
        db_h.ubicacion = update_data.pop("sector_planta")
    if "rol" in update_data:
        rol_val = update_data.pop("rol")
        db_h.tipo_host_id = get_or_create_tipo_host(db, rol_val or "Host")
        db_h.rol = rol_val or "Host"
        
    for key, value in update_data.items():
        setattr(db_h, key, value)
        
    db.commit()
    db.refresh(db_h)
    return get_host(db, db_h.id)

def delete_host(db: Session, host_id: int):
    db_h = db.query(models.Host).filter(models.Host.id == host_id).first()
    if not db_h:
        return False
    db.delete(db_h)
    db.commit()
    return True


# ==================
#    SERVIDORES
# ==================
def get_servidores(db: Session):
    results = db.query(models.Host).join(models.TipoHost).filter(models.TipoHost.nombre == "Servidor").order_by(models.Host.nombre.asc()).all()
    mapped = []
    for s in results:
        mapped.append({
            "id": s.id,
            "nombre": s.nombre,
            "switch_id": s.switch_id,
            "switch_nombre": s.switch.nombre if s.switch else "",
            "marca": s.marca.nombre if s.marca else "",
            "modelo": s.modelo,
            "serial": s.serial,
            "ip": s.ip,
            "tipo_servidor": s.tipo_servidor.nombre if s.tipo_servidor else "Virtual (VM)",
            "sistema_operativo": s.sistema_operativo or "",
            "checkmk_host_id": s.checkmk_host_id,
            "fecha_instalacion": s.fecha_instalacion,
            "ultimo_mantenimiento": s.ultimo_mantenimiento,
            "proximo_mantenimiento": s.proximo_mantenimiento,
            "fecha_eol": s.fecha_eol,
            "fin_garantia_contrato": s.fin_garantia_contrato,
            "proveedor_soporte": s.proveedor_soporte or "",
            "numero_contrato": s.numero_contrato or ""
        })
    return mapped

def get_servidor(db: Session, srv_id: int):
    s = db.query(models.Host).filter(models.Host.id == srv_id).first()
    if s:
        return {
            "id": s.id,
            "nombre": s.nombre,
            "switch_id": s.switch_id,
            "switch_nombre": s.switch.nombre if s.switch else "",
            "marca": s.marca.nombre if s.marca else "",
            "modelo": s.modelo,
            "serial": s.serial,
            "ip": s.ip,
            "tipo_servidor": s.tipo_servidor.nombre if s.tipo_servidor else "Virtual (VM)",
            "sistema_operativo": s.sistema_operativo or "",
            "checkmk_host_id": s.checkmk_host_id,
            "fecha_instalacion": s.fecha_instalacion,
            "ultimo_mantenimiento": s.ultimo_mantenimiento,
            "proximo_mantenimiento": s.proximo_mantenimiento,
            "fecha_eol": s.fecha_eol,
            "fin_garantia_contrato": s.fin_garantia_contrato,
            "proveedor_soporte": s.proveedor_soporte or "",
            "numero_contrato": s.numero_contrato or ""
        }
    return None

def create_servidor(db: Session, srv: schemas.ServidorCreate):
    tipo_id = get_or_create_tipo_host(db, "Servidor")
    marca_id = get_or_create_marca(db, srv.marca)
    tipo_servidor_id = get_or_create_tipo_servidor(db, srv.tipo_servidor)
    
    data = srv.dict(exclude={"marca", "tipo_servidor"})
    db_srv = models.Host(
        **data,
        tipo_host_id=tipo_id,
        marca_id=marca_id,
        tipo_servidor_id=tipo_servidor_id
    )
    db.add(db_srv)
    db.commit()
    db.refresh(db_srv)
    return get_servidor(db, db_srv.id)

def update_servidor(db: Session, srv_id: int, srv: schemas.ServidorUpdate):
    db_srv = db.query(models.Host).filter(models.Host.id == srv_id).first()
    if not db_srv:
        return None
    
    update_data = srv.dict(exclude_unset=True)
    if "marca" in update_data:
        db_srv.marca_id = get_or_create_marca(db, update_data.pop("marca"))
    if "tipo_servidor" in update_data:
        db_srv.tipo_servidor_id = get_or_create_tipo_servidor(db, update_data.pop("tipo_servidor"))
        
    for key, value in update_data.items():
        setattr(db_srv, key, value)
        
    db.commit()
    db.refresh(db_srv)
    return get_servidor(db, db_srv.id)

def delete_servidor(db: Session, srv_id: int):
    db_srv = db.query(models.Host).filter(models.Host.id == srv_id).first()
    if not db_srv:
        return False
    db.delete(db_srv)
    db.commit()
    return True


# ==================
#   APLICACIONES
# ==================
def get_aplicaciones(db: Session):
    return db.query(models.Aplicacion).order_by(models.Aplicacion.nombre.asc()).all()

def get_aplicacion(db: Session, app_id: int):
    return db.query(models.Aplicacion).filter(models.Aplicacion.id == app_id).first()

def create_aplicacion(db: Session, app: schemas.AplicacionCreate):
    db_app = models.Aplicacion(**app.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

def update_aplicacion(db: Session, app_id: int, app: schemas.AplicacionUpdate):
    db_app = get_aplicacion(db, app_id)
    if not db_app:
        return None
    for key, value in app.dict(exclude_unset=True).items():
        setattr(db_app, key, value)
    db.commit()
    db.refresh(db_app)
    return db_app

def delete_aplicacion(db: Session, app_id: int):
    db_app = get_aplicacion(db, app_id)
    if not db_app:
        return False
    db.delete(db_app)
    db.commit()
    return True


# ==================
#   DEPENDENCIAS
# ==================
def get_dependencias(db: Session):
    results = db.query(models.DependenciaAppHost).all()
    mapped = []
    for d in results:
        mapped.append({
            "id": d.id,
            "app_id": d.app_id,
            "app_nombre": d.aplicacion.nombre if d.aplicacion else "",
            "servidor_id": d.host_id,
            "servidor_nombre": d.host.nombre if d.host else "",
            "rol_servidor": d.rol_servidor
        })
    return mapped

def get_dependencia(db: Session, dep_id: int):
    d = db.query(models.DependenciaAppHost).filter(models.DependenciaAppHost.id == dep_id).first()
    if d:
        return {
            "id": d.id,
            "app_id": d.app_id,
            "app_nombre": d.aplicacion.nombre if d.aplicacion else "",
            "servidor_id": d.host_id,
            "servidor_nombre": d.host.nombre if d.host else "",
            "rol_servidor": d.rol_servidor
        }
    return None

def create_dependencia(db: Session, dep: schemas.DependenciaCreate):
    db_dep = models.DependenciaAppHost(
        app_id=dep.app_id,
        host_id=dep.servidor_id,
        rol_servidor=dep.rol_servidor
    )
    db.add(db_dep)
    db.commit()
    db.refresh(db_dep)
    return get_dependencia(db, db_dep.id)

def update_dependencia(db: Session, dep_id: int, dep: schemas.DependenciaUpdate):
    db_dep = db.query(models.DependenciaAppHost).filter(models.DependenciaAppHost.id == dep_id).first()
    if not db_dep:
        return None
    
    update_data = dep.dict(exclude_unset=True)
    if "servidor_id" in update_data:
        db_dep.host_id = update_data.pop("servidor_id")
        
    for key, value in update_data.items():
        setattr(db_dep, key, value)
        
    db.commit()
    db.refresh(db_dep)
    return get_dependencia(db, db_dep.id)

def delete_dependencia(db: Session, dep_id: int):
    db_dep = db.query(models.DependenciaAppHost).filter(models.DependenciaAppHost.id == dep_id).first()
    if not db_dep:
        return False
    db.delete(db_dep)
    db.commit()
    return True


# ==================
#    PROCESOS
# ==================
def get_procesos(db: Session):
    results = db.query(models.ProcesoPlanta).order_by(models.ProcesoPlanta.nombre_proceso.asc()).all()
    for p in results:
        p.app_nombre = p.aplicacion.nombre if p.aplicacion else ""
    return results

def get_proceso(db: Session, proc_id: int):
    return db.query(models.ProcesoPlanta).filter(models.ProcesoPlanta.id == proc_id).first()

def create_proceso(db: Session, p: schemas.ProcesoCreate):
    db_p = models.ProcesoPlanta(**p.dict())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    db_p.app_nombre = db_p.aplicacion.nombre if db_p.aplicacion else ""
    return db_p

def update_proceso(db: Session, proc_id: int, p: schemas.ProcesoUpdate):
    db_p = get_proceso(db, proc_id)
    if not db_p:
        return None
    for key, value in p.dict(exclude_unset=True).items():
        setattr(db_p, key, value)
    db.commit()
    db.refresh(db_p)
    db_p.app_nombre = db_p.aplicacion.nombre if db_p.aplicacion else ""
    return db_p

def delete_proceso(db: Session, proc_id: int):
    db_p = get_proceso(db, proc_id)
    if not db_p:
        return False
    db.delete(db_p)
    db.commit()
    return True


# ==================
#    CATALOGO
# ==================
def get_catalogos(db: Session):
    return db.query(models.CatalogoEquipo).order_by(models.CatalogoEquipo.marca.asc()).all()

def create_catalogo(db: Session, cat: schemas.CatalogoCreate):
    db_cat = models.CatalogoEquipo(**cat.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

def get_o_crear_catalogo(db: Session, marca: str, modelo: str, tipo: str) -> int:
    cat = db.query(models.CatalogoEquipo).filter(
        func.lower(models.CatalogoEquipo.marca) == func.lower(marca.strip()),
        func.lower(models.CatalogoEquipo.modelo) == func.lower(modelo.strip())
    ).first()
    
    if cat:
        return cat.id
    else:
        new_cat = models.CatalogoEquipo(
            marca=marca.strip(),
            modelo=modelo.strip(),
            tipo=tipo.strip(),
            serializado=0
        )
        db.add(new_cat)
        db.commit()
        db.refresh(new_cat)
        return new_cat.id


# ==================
#   CONSUMIBLES
# ==================
def get_consumibles(db: Session):
    results = db.query(models.StockConsumible).join(models.CatalogoEquipo).order_by(
        models.CatalogoEquipo.marca.asc(),
        models.CatalogoEquipo.modelo.asc()
    ).all()
    
    output = []
    for c in results:
        output.append({
            "id": c.id,
            "catalogo_id": c.catalogo_id,
            "marca": c.catalogo.marca,
            "modelo": c.catalogo.modelo,
            "tipo": c.catalogo.tipo,
            "custom_table": c.catalogo.tipo,  # just in case
            "cantidad": c.cantidad,
            "ubicacion": c.ubicacion,
            "stock_minimo": c.stock_minimo
        })
    return output

def get_consumible(db: Session, cons_id: int):
    return db.query(models.StockConsumible).filter(models.StockConsumible.id == cons_id).first()

def create_consumible(db: Session, c: schemas.ConsumibleCreate):
    db_c = models.StockConsumible(**c.dict())
    db.add(db_c)
    db.commit()
    db.refresh(db_c)
    return db_c

def update_consumible_flat(db: Session, cons_id: int, data: dict):
    db_c = get_consumible(db, cons_id)
    if not db_c:
        return None
        
    if any(k in data for k in ["marca", "modelo", "tipo"]):
        marca_act = data.get("marca", db_c.catalogo.marca)
        modelo_act = data.get("modelo", db_c.catalogo.modelo)
        tipo_act = data.get("tipo", db_c.catalogo.tipo)
        
        nuevo_cat_id = get_o_crear_catalogo(db, marca_act, modelo_act, tipo_act)
        db_c.catalogo_id = nuevo_cat_id
        
    for key in ["cantidad", "ubicacion", "stock_minimo"]:
        if key in data:
            setattr(db_c, key, data[key])
            
    db.commit()
    db.refresh(db_c)
    return db_c

def create_consumible_flat(db: Session, data: dict):
    marca = data.get("marca", "Genérico")
    modelo = data.get("modelo", "Pendiente")
    tipo = data.get("tipo", "Patchcord")
    
    catalogo_id = get_o_crear_catalogo(db, marca, modelo, tipo)
    
    db_c = models.StockConsumible(
        catalogo_id=catalogo_id,
        cantidad=data.get("cantidad", 0),
        ubicacion=data.get("ubicacion", "Depósito Principal"),
        stock_minimo=data.get("stock_minimo", 5)
    )
    db.add(db_c)
    db.commit()
    db.refresh(db_c)
    return db_c

def delete_consumible(db: Session, cons_id: int):
    db_c = get_consumible(db, cons_id)
    if not db_c:
        return False
    db.delete(db_c)
    db.commit()
    return True


# ==================
#   HISTORIAL
# ==================
def get_historial(db: Session):
    return db.query(models.HistoricoMovimiento).order_by(models.HistoricoMovimiento.fecha.desc()).all()

def log_movimiento(db: Session, operador: str, tipo: str, ref_id: int, tabla: str, detalle: str):
    log = models.HistoricoMovimiento(
        operador=operador,
        tipo_movimiento=tipo,
        referencia_id=ref_id,
        tabla_referencia=tabla,
        detalle=detalle
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

# ==========================================
# SEGURIDAD, USUARIOS Y ROLES
# ==========================================
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- USUARIOS ---
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session):
    results = db.query(models.User).order_by(models.User.username.asc()).all()
    for u in results:
        u.role_nombre = u.role.nombre if u.role else None
    return results

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        nombre=user.nombre,
        hashed_password=hashed_pw,
        role_id=user.role_id,
        is_superadmin=user.is_superadmin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_user.role_nombre = db_user.role.nombre if db_user.role else None
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    data = user.dict(exclude_unset=True)
    if "password" in data and data["password"]:
        data["hashed_password"] = get_password_hash(data["password"])
        del data["password"]
    for key, val in data.items():
        setattr(db_user, key, val)
    db.commit()
    db.refresh(db_user)
    db_user.role_nombre = db_user.role.nombre if db_user.role else None
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

# --- ROLES ---
def get_roles(db: Session):
    return db.query(models.Role).order_by(models.Role.nombre.asc()).all()

def get_role(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()

def create_role(db: Session, role: schemas.RoleCreate):
    db_role = models.Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: int, role: schemas.RoleUpdate):
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    for key, val in role.dict(exclude_unset=True).items():
        setattr(db_role, key, val)
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int):
    db_role = get_role(db, role_id)
    if not db_role:
        return False
    db.delete(db_role)
    db.commit()
    return True

# --- PERMISOS / MÓDULOS DE ROL ---
def update_role_modules(db: Session, role_id: int, modules: List[schemas.RoleModuleBase]):
    # 1. Delete existing modules mapping
    db.query(models.RoleModule).filter(models.RoleModule.role_id == role_id).delete()
    
    # 2. Add new permissions
    for mod in modules:
        db_mod = models.RoleModule(
            role_id=role_id,
            module_name=mod.module_name,
            can_read=mod.can_read,
            can_write=mod.can_write
        )
        db.add(db_mod)
    db.commit()
    return db.query(models.RoleModule).filter(models.RoleModule.role_id == role_id).all()

