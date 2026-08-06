# backend/app/simulator.py
from sqlalchemy.orm import Session
from . import models

def simular_corte_subestacion(db: Session, subestacion_id: int):
    """
    Simula el impacto de un corte en una Subestación.
    Retorna blindobarras, ups, racks, switches, hosts, servidores, aplicaciones y procesos afectados.
    """
    # 1. Blindobarras alimentadas por esta Subestación
    blindobarras = db.query(models.Blindobarra).filter(models.Blindobarra.subestacion_id == subestacion_id).all()
    blindobarra_ids = [b.id for b in blindobarras]
    if not blindobarra_ids:
        return {
            "blindobarras": [], "ups": [], "racks": [], "switches": [], 
            "hosts": [], "servidores": [], "aplicaciones": [], "procesos": []
        }
        
    # 2. UPSs alimentadas por estas blindobarras
    ups_hosts = db.query(models.Host).join(models.TipoHost).filter(
        models.TipoHost.nombre == "UPS",
        models.Host.blindobarra_id.in_(blindobarra_ids)
    ).all()
    ups_ids = [u.id for u in ups_hosts]
    
    # 3. Racks alimentados por estas UPSs
    racks = []
    rack_ids = []
    if ups_ids:
        racks = db.query(models.Rack).filter(models.Rack.ups_id.in_(ups_ids)).all()
        rack_ids = [r.id for r in racks]
        
    # 4. Switches en estos racks
    switches = []
    switch_ids = []
    if rack_ids:
        switches = db.query(models.Host).join(models.TipoHost).filter(
            models.TipoHost.nombre == "Switch",
            models.Host.rack_id.in_(rack_ids)
        ).all()
        switch_ids = [s.id for s in switches]
        
    # 5. Hosts y Servidores conectados a estos switches
    hosts = []
    servidores = []
    servidor_ids = []
    if switch_ids:
        hosts = db.query(models.Host).join(models.TipoHost).filter(
            ~models.TipoHost.nombre.in_(["UPS", "Switch", "Servidor"]),
            models.Host.switch_id.in_(switch_ids)
        ).all()
        servidores = db.query(models.Host).join(models.TipoHost).filter(
            models.TipoHost.nombre == "Servidor",
            models.Host.switch_id.in_(switch_ids)
        ).all()
        servidor_ids = [s.id for s in servidores]
        
    # 6. Aplicaciones que dependen de estos servidores
    aplicaciones = []
    procesos = []
    if servidor_ids:
        deps = db.query(models.DependenciaAppHost).filter(models.DependenciaAppHost.host_id.in_(servidor_ids)).all()
        app_ids = list(set([d.app_id for d in deps]))
        if app_ids:
            aplicaciones = db.query(models.Aplicacion).filter(models.Aplicacion.id.in_(app_ids)).all()
            procesos = db.query(models.ProcesoPlanta).filter(models.ProcesoPlanta.aplicacion_id.in_(app_ids)).all()
            
    return {
        "blindobarras": [{"id": b.id, "nombre": b.nombre} for b in blindobarras],
        "ups": [{"id": u.id, "nombre": u.nombre} for u in ups_hosts],
        "racks": [{"id": r.id, "nombre": r.nombre} for r in racks],
        "switches": [{"id": s.id, "nombre": s.nombre, "ip": s.ip} for s in switches],
        "hosts": [{"nombre": h.nombre, "ip": h.ip, "rol": h.rol, "ubicacion": h.ubicacion} for h in hosts],
        "servidores": [{"id": s.id, "nombre": s.nombre, "ip": s.ip} for s in servidores],
        "aplicaciones": [{"id": a.id, "nombre": a.nombre, "descripcion": a.descripcion} for a in aplicaciones],
        "procesos": [
            {
                "nombre_proceso": p.nombre_proceso, 
                "linea_produccion": p.linea_produccion, 
                "app_responsable": p.aplicacion.nombre if p.aplicacion else ""
            } 
            for p in procesos
        ]
    }

def simular_corte_blindobarra(db: Session, blindobarra_id: int):
    """
    Simula el impacto de un corte en una Blindobarra.
    Retorna ups, racks, switches, hosts, servidores, aplicaciones y procesos afectados.
    """
    # 1. UPSs alimentadas por esta blindobarra
    ups_hosts = db.query(models.Host).join(models.TipoHost).filter(
        models.TipoHost.nombre == "UPS",
        models.Host.blindobarra_id == blindobarra_id
    ).all()
    ups_ids = [u.id for u in ups_hosts]
    
    if not ups_ids:
        return {
            "ups": [], "racks": [], "switches": [], 
            "hosts": [], "servidores": [], "aplicaciones": [], "procesos": []
        }
        
    # 2. Racks alimentados por estas UPSs
    racks = db.query(models.Rack).filter(models.Rack.ups_id.in_(ups_ids)).all()
    rack_ids = [r.id for r in racks]
    
    # 3. Switches en estos racks
    switches = []
    switch_ids = []
    if rack_ids:
        switches = db.query(models.Host).join(models.TipoHost).filter(
            models.TipoHost.nombre == "Switch",
            models.Host.rack_id.in_(rack_ids)
        ).all()
        switch_ids = [s.id for s in switches]
        
    # 4. Hosts y Servidores conectados a estos switches
    hosts = []
    servidores = []
    servidor_ids = []
    if switch_ids:
        hosts = db.query(models.Host).join(models.TipoHost).filter(
            ~models.TipoHost.nombre.in_(["UPS", "Switch", "Servidor"]),
            models.Host.switch_id.in_(switch_ids)
        ).all()
        servidores = db.query(models.Host).join(models.TipoHost).filter(
            models.TipoHost.nombre == "Servidor",
            models.Host.switch_id.in_(switch_ids)
        ).all()
        servidor_ids = [s.id for s in servidores]
        
    # 5. Aplicaciones que dependen de estos servidores
    aplicaciones = []
    procesos = []
    if servidor_ids:
        deps = db.query(models.DependenciaAppHost).filter(models.DependenciaAppHost.host_id.in_(servidor_ids)).all()
        app_ids = list(set([d.app_id for d in deps]))
        if app_ids:
            aplicaciones = db.query(models.Aplicacion).filter(models.Aplicacion.id.in_(app_ids)).all()
            procesos = db.query(models.ProcesoPlanta).filter(models.ProcesoPlanta.aplicacion_id.in_(app_ids)).all()
            
    return {
        "ups": [{"id": u.id, "nombre": u.nombre} for u in ups_hosts],
        "racks": [{"id": r.id, "nombre": r.nombre} for r in racks],
        "switches": [{"id": s.id, "nombre": s.nombre, "ip": s.ip} for s in switches],
        "hosts": [{"nombre": h.nombre, "ip": h.ip, "rol": h.rol, "ubicacion": h.ubicacion} for h in hosts],
        "servidores": [{"id": s.id, "nombre": s.nombre, "ip": s.ip} for s in servidores],
        "aplicaciones": [{"id": a.id, "nombre": a.nombre, "descripcion": a.descripcion} for a in aplicaciones],
        "procesos": [
            {
                "nombre_proceso": p.nombre_proceso, 
                "linea_produccion": p.linea_produccion, 
                "app_responsable": p.aplicacion.nombre if p.aplicacion else ""
            } 
            for p in procesos
        ]
    }

def simular_corte_ups(db: Session, ups_id: int):
    """
    Simula el impacto de un corte en una UPS.
    Retorna racks, switches, hosts, servidores, aplicaciones y procesos afectados.
    """
    # 1. Racks alimentados por esta UPS
    racks = db.query(models.Rack).filter(models.Rack.ups_id == ups_id).all()
    rack_ids = [r.id for r in racks]
    
    if not rack_ids:
        return {
            "racks": [], "switches": [], 
            "hosts": [], "servidores": [], "aplicaciones": [], "procesos": []
        }
        
    # 2. Switches en esos racks
    switches = db.query(models.Host).join(models.TipoHost).filter(
        models.TipoHost.nombre == "Switch",
        models.Host.rack_id.in_(rack_ids)
    ).all()
    switch_ids = [s.id for s in switches]
    
    # 3. Hosts y Servidores conectados a esos switches
    hosts = []
    servidores = []
    servidor_ids = []
    if switch_ids:
        hosts = db.query(models.Host).join(models.TipoHost).filter(
            ~models.TipoHost.nombre.in_(["UPS", "Switch", "Servidor"]),
            models.Host.switch_id.in_(switch_ids)
        ).all()
        servidores = db.query(models.Host).join(models.TipoHost).filter(
            models.TipoHost.nombre == "Servidor",
            models.Host.switch_id.in_(switch_ids)
        ).all()
        servidor_ids = [s.id for s in servidores]
        
    # 4. Aplicaciones y procesos de planta afectados
    aplicaciones = []
    procesos = []
    if servidor_ids:
        deps = db.query(models.DependenciaAppHost).filter(models.DependenciaAppHost.host_id.in_(servidor_ids)).all()
        app_ids = list(set([d.app_id for d in deps]))
        if app_ids:
            aplicaciones = db.query(models.Aplicacion).filter(models.Aplicacion.id.in_(app_ids)).all()
            procesos = db.query(models.ProcesoPlanta).filter(models.ProcesoPlanta.aplicacion_id.in_(app_ids)).all()
        
    return {
        "racks": [{"id": r.id, "nombre": r.nombre} for r in racks],
        "switches": [{"id": s.id, "nombre": s.nombre, "ip": s.ip} for s in switches],
        "hosts": [{"nombre": h.nombre, "ip": h.ip, "rol": h.rol, "ubicacion": h.ubicacion} for h in hosts],
        "servidores": [{"id": s.id, "nombre": s.nombre, "ip": s.ip} for s in servidores],
        "aplicaciones": [{"id": a.id, "nombre": a.nombre, "descripcion": a.descripcion} for a in aplicaciones],
        "procesos": [
            {
                "nombre_proceso": p.nombre_proceso, 
                "linea_produccion": p.linea_produccion, 
                "app_responsable": p.aplicacion.nombre if p.aplicacion else ""
            } 
            for p in procesos
        ]
    }

def simular_corte_rack(db: Session, rack_id: int):
    """
    Simula el impacto de la caída de un Rack.
    Retorna switches, hosts, servidores, aplicaciones y procesos afectados.
    """
    # 1. Switches en el rack
    switches = db.query(models.Host).join(models.TipoHost).filter(
        models.TipoHost.nombre == "Switch",
        models.Host.rack_id == rack_id
    ).all()
    switch_ids = [s.id for s in switches]
    
    # 2. Hosts y Servidores conectados a estos switches
    hosts = []
    servidores = []
    servidor_ids = []
    if switch_ids:
        hosts = db.query(models.Host).join(models.TipoHost).filter(
            ~models.TipoHost.nombre.in_(["UPS", "Switch", "Servidor"]),
            models.Host.switch_id.in_(switch_ids)
        ).all()
        servidores = db.query(models.Host).join(models.TipoHost).filter(
            models.TipoHost.nombre == "Servidor",
            models.Host.switch_id.in_(switch_ids)
        ).all()
        servidor_ids = [s.id for s in servidores]
        
    # 3. Aplicaciones y procesos de planta afectados
    aplicaciones = []
    procesos = []
    if servidor_ids:
        deps = db.query(models.DependenciaAppHost).filter(models.DependenciaAppHost.host_id.in_(servidor_ids)).all()
        app_ids = list(set([d.app_id for d in deps]))
        if app_ids:
            aplicaciones = db.query(models.Aplicacion).filter(models.Aplicacion.id.in_(app_ids)).all()
            procesos = db.query(models.ProcesoPlanta).filter(models.ProcesoPlanta.aplicacion_id.in_(app_ids)).all()
        
    return {
        "switches": [{"id": s.id, "nombre": s.nombre, "ip": s.ip} for s in switches],
        "hosts": [{"nombre": h.nombre, "ip": h.ip, "rol": h.rol, "ubicacion": h.ubicacion} for h in hosts],
        "servidores": [{"id": s.id, "nombre": s.nombre, "ip": s.ip} for s in servidores],
        "aplicaciones": [{"id": a.id, "nombre": a.nombre, "descripcion": a.descripcion} for a in aplicaciones],
        "procesos": [
            {
                "nombre_proceso": p.nombre_proceso, 
                "linea_produccion": p.linea_produccion, 
                "app_responsable": p.aplicacion.nombre if p.aplicacion else ""
            } 
            for p in procesos
        ]
    }

def simular_mantenimiento_servidor(db: Session, servidor_id: int):
    """
    Simula el impacto del mantenimiento de un servidor.
    Retorna aplicaciones y procesos de planta afectados.
    """
    deps = db.query(models.DependenciaAppHost).filter(
        models.DependenciaAppHost.host_id == servidor_id
    ).all()
    app_ids = [d.app_id for d in deps]
    
    if not app_ids:
        return {"aplicaciones": [], "procesos": []}
        
    aplicaciones = db.query(models.Aplicacion).filter(models.Aplicacion.id.in_(app_ids)).all()
    procesos = db.query(models.ProcesoPlanta).filter(models.ProcesoPlanta.aplicacion_id.in_(app_ids)).all()
    
    return {
        "aplicaciones": [
            {"id": a.id, "nombre": a.nombre, "descripcion": a.descripcion} 
            for a in aplicaciones
        ],
        "procesos": [
            {
                "nombre_proceso": p.nombre_proceso, 
                "linea_produccion": p.linea_produccion, 
                "app_responsable": p.aplicacion.nombre if p.aplicacion else ""
            } 
            for p in procesos
        ]
    }
