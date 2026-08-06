# backend/app/pdf_generator.py
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from .config import settings

def generar_pdf_acta_entrega(datos_movimiento: dict) -> str:
    """Genera un archivo PDF formal de entrega de hardware para que firme el responsable."""
    serial_limpio = datos_movimiento.get('serial', 'S/N')
    if not serial_limpio or serial_limpio == "":
        serial_limpio = "S/N"

    nombre_archivo = f"acta_entrega_{datos_movimiento['nombre'].replace(' ', '_')}.pdf"
    ruta_pdf = os.path.join(settings.UPLOAD_DIR, nombre_archivo)

    doc = SimpleDocTemplate(
        ruta_pdf, 
        pagesize=letter, 
        rightMargin=50, 
        leftMargin=50, 
        topMargin=50, 
        bottomMargin=50
    )
    story = []
    styles = getSampleStyleSheet()

    # Encabezado formal
    story.append(Paragraph("<b>NETTRACK ARGENTINA - DEPARTAMENTO DE INFRAESTRUCTURA</b>", styles['Heading2']))
    story.append(Paragraph("ACTA DE ENTREGA Y TRANSFERENCIA DE ACTIVO DE RED", styles['Normal']))
    story.append(Spacer(1, 15))

    # Contenido del acta
    texto_cuerpo = """
    Por medio de la presente, se hace entrega formal del activo tecnológico que se detalla a continuación,
    desde el Depósito de Planta hacia su ubicación de despliegue final en producción. El firmante asume la 
    responsabilidad del traslado, instalación y resguardo físico del mismo.
    """
    story.append(Paragraph(texto_cuerpo, styles['BodyText']))
    story.append(Spacer(1, 15))

    # Tabla de especificaciones
    datos_tabla = [
        ["Concepto", "Detalle"],
        ["Tipo de Dispositivo", datos_movimiento.get("tipo_equipo", "N/A")],
        ["Equipo / Nombre", datos_movimiento.get("nombre", "N/A")],
        ["Marca / Modelo", f"{datos_movimiento.get('marca', 'Generico')} {datos_movimiento.get('modelo', '')}"],
        ["Número de Serie", serial_limpio],
        ["Entregado por (Operador)", datos_movimiento["operador"]],
        ["Retirado por (Responsable)", datos_movimiento["responsable"]],
    ]

    t = Table(datos_tabla, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#0b1c3f")),  # Azul Corporativo
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(t)
    story.append(Spacer(1, 40))

    # Bloque de firmas
    firmas = [
        ["____________________________", "____________________________"],
        ["Firma Entregador (IT)", "Firma Receptor (Responsable)"],
        [f"Usuario: {datos_movimiento['operador']}", f"Nombre: {datos_movimiento['responsable']}"]
    ]
    tf = Table(firmas, colWidths=[250, 250])
    tf.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
    ]))
    story.append(tf)

    doc.build(story)
    return ruta_pdf

def generar_pdf_acta_consumible(datos_movimiento: dict) -> str:
    """Genera un archivo PDF formal de entrega de consumibles por cantidad."""
    nombre_limpio = f"{datos_movimiento['marca']}_{datos_movimiento['modelo']}".replace(' ', '_').replace('/', '_')
    nombre_archivo = f"acta_consumible_{nombre_limpio}.pdf"
    ruta_pdf = os.path.join(settings.UPLOAD_DIR, nombre_archivo)

    doc = SimpleDocTemplate(
        ruta_pdf, 
        pagesize=letter, 
        rightMargin=50, 
        leftMargin=50, 
        topMargin=50, 
        bottomMargin=50
    )
    story = []
    styles = getSampleStyleSheet()

    # Encabezado Corporativo
    story.append(Paragraph("<b>NETTRACK ARGENTINA - DEPARTAMENTO DE INFRAESTRUCTURA</b>", styles['Heading2']))
    story.append(Paragraph("REMITO DE EGRESO DE MATERIALES Y CONSUMIBLES DE IT", styles['Normal']))
    story.append(Spacer(1, 15))

    texto_cuerpo = """
    Por medio de la presente, se certifica la entrega del material de consumo informático detallado a continuación.
    El firmante declara recibir los insumos en conformidad para las tareas de infraestructura asignadas en planta.
    """
    story.append(Paragraph(texto_cuerpo, styles['BodyText']))
    story.append(Spacer(1, 15))

    # Tabla de especificaciones
    datos_tabla = [
        ["Concepto / Insumo", "Detalle"],
        ["Material / Categoría", datos_movimiento["tipo_material"]],
        ["Descripción (Marca/Modelo)", f"{datos_movimiento['marca']} {datos_movimiento['modelo']}"],
        ["Cantidad Entregada", f"{datos_movimiento['cantidad_retirada']} Unidades"],
        ["Depósito de Origen", datos_movimiento["ubicacion_origen"]],
        ["Despachado por (IT)", datos_movimiento["operador"]],
        ["Recibido por (Responsable)", datos_movimiento["responsable"]],
    ]

    t = Table(datos_tabla, colWidths=[200, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#0b1c3f")),  # Azul Corporativo
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(t)
    story.append(Spacer(1, 40))

    # Firmas
    firmas = [
        ["____________________________", "____________________________"],
        ["Firma Entregador (IT)", "Firma Receptor (Responsable)"],
        [f"Usuario: {datos_movimiento['operador']}", f"Nombre: {datos_movimiento['responsable']}"]
    ]
    tf = Table(firmas, colWidths=[250, 250])
    tf.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
    ]))
    story.append(tf)

    doc.build(story)
    return ruta_pdf
