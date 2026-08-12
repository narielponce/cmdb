import datetime
from sqlalchemy import text
from backend.app.database import engine, get_db
from backend.app import models

def test_lifecycle():
    db = next(get_db())
    
    # Locate SW-001
    sw = db.query(models.Host).filter(models.Host.nombre == "SW-001").first()
    if not sw:
        print("🔴 SW-001 not found, cannot seed dates.")
        return
        
    print(f"🌱 Seeding lifecycle dates for {sw.nombre}...")
    today = datetime.date.today()
    
    # 1. expired maintenance (Critical)
    sw.ultimo_mantenimiento = today - datetime.timedelta(days=180)
    sw.proximo_mantenimiento = today - datetime.timedelta(days=5) # 5 days ago (Expired)
    
    # 2. warranty expiring soon (Warning - 45 days from now)
    sw.fin_garantia_contrato = today + datetime.timedelta(days=45)
    sw.proveedor_soporte = "Cisco Partner Gold"
    sw.numero_contrato = "CON-SW-0092"
    
    # 3. EOL expiring soon (Warning - 70 days from now)
    sw.fecha_eol = today + datetime.timedelta(days=70)
    
    db.commit()
    print("🟢 Seeding completed successfully. Running database query verify...")
    
    # Query SW-001 again
    db.refresh(sw)
    print(f"   Último Mantenimiento: {sw.ultimo_mantenimiento}")
    print(f"   Próximo Mantenimiento: {sw.proximo_mantenimiento}")
    print(f"   Fin de Garantía: {sw.fin_garantia_contrato}")
    print(f"   EOL: {sw.fecha_eol}")

if __name__ == "__main__":
    test_lifecycle()
