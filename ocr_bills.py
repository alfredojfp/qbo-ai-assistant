# -*- coding: utf-8 -*-
"""
MÓDULO OCR DE BILLS CON GEMINI 2.5 FLASH
MODELO: gemini-2.5-flash
RATE LIMITS (FREE TIER): 15 RPM, 500 RPD, 1M TPM
SDK: google-genai

API pública:
- extraer_bills_de_pdf(pdf_path) -> List[Dict]   (1 PDF)
- procesar_lote_ocr(carpeta) -> Dict              (todos los PDFs)
- listar_pdfs_en_carpeta(carpeta) -> List[str]
- validar_bill_minimo(bill) -> bool
- generar_csv_preview(bills, output_path) -> str
"""
import os
import sys
import io
import csv
import json
import base64
import shutil
import tempfile
from datetime import datetime
from typing import List, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

GEMINI_CLIENT = None


def _get_gemini_client():
    """Lazy init del cliente Gemini (para que el módulo sea importable sin la dep)."""
    global GEMINI_CLIENT
    if GEMINI_CLIENT is None:
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "❌ Falta dependencia: pip install google-genai\n"
                "Esta es necesaria solo para la extracción OCR."
            )
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            raise ValueError("❌ GOOGLE_GEMINI_API_KEY no encontrada en .env")
        GEMINI_CLIENT = genai.Client(api_key=api_key)
    return GEMINI_CLIENT


OCR_PROMPT = """
Analiza este documento PDF (puede tener múltiples páginas) que contiene
INVOICES, BILLS o FACTURAS. Busca TODOS los documentos contables presentes.

Para CADA invoice/bill encontrado, extrae:

CAMPOS OBLIGATORIOS:
- invoice_number: Numero del invoice (si no tiene numero, usar "S/N")
- invoice_date: Fecha en formato YYYY-MM-DD
- vendor_name: Nombre completo del vendor/proveedor/emisor
- customer_name: Nombre del cliente/receptor (si no aparece, usar "")
- total_amount: Monto total final como numero (sin $, sin comas)
- balance: Balance pendiente (0 si esta pagado)

CAMPOS OPCIONALES (usa null si no existen):
- subtotal: Subtotal antes de impuestos
- tax_amount: Monto de impuestos (IVA, GST, etc.)
- po_number: Numero de Purchase Order / Orden de Compra
- terms: Terminos de pago (ej: "Net 30", "Contado")
- account_name: Sugerencia de cuenta contable

MANEJO DE CASOS REALES:
- PAGINAS MULTIPLES: un mismo invoice puede ocupar 2+ paginas. Si ves una
  pagina que dice "continuacion" o no tiene un nuevo invoice number,
  pertenece al invoice anterior. NO la trates como un invoice separado.
- SALTOS DE PAGINA: si una factura esta cortada a mitad de pagina y
  continua en la siguiente, reconstruila como UN solo invoice.
- MULTIPLES INVOICES EN UN PDF: identifica cada uno por su invoice number
  distinto. Si no hay invoice number, usa la fecha + vendor como
  identificador unico.
- FACTURAS MANUSCRITAS: si hay texto escrito a mano, leelo con cuidado.
  Prioriza numeros claramente legibles.
- BILINGUE (ES/EN): si la factura tiene columnas en dos idiomas, usa los
  valores en espanol. Si esta en ingles, usa los valores en ingles.
- TOTAL CONFUSO: si hay multiples totales, usa el TOTAL FINAL (el mas
  grande, el que esta en negrita o recuadrado).
- MONEDA: si ves simbolos de moneda ($, USD, MXN), extrae el numero
  sin el simbolo. Asumi USD a menos que se indique otra moneda.

REGLAS:
1. Retorna array JSON con TODOS los invoices encontrados
2. Montos como numeros (float), NO strings. Ej: 1500.00 no "1,500.00"
3. Fechas en formato YYYY-MM-DD. Si el anio tiene 2 digitos, asumi 20XX
4. Si un campo opcional no existe, usa null
5. No dupliques invoices. Si ves el mismo invoice number dos veces,
   es el mismo documento (probablemente pagina 1 y 2)
6. Si un PDF no contiene ningun invoice, retorna array vacio []

Retorna SOLO JSON valido, sin explicaciones ni markdown.
Formato: [{"invoice_number": "...", ...}, {...}]
"""


def listar_pdfs_en_carpeta(carpeta: str = "Pending bills") -> List[str]:
    """
    Lista todos los PDFs en una carpeta, ordenados alfabéticamente.

    Args:
        carpeta: Ruta a la carpeta. Default: "Pending bills"

    Returns:
        Lista de rutas absolutas a PDFs. Vacía si la carpeta no existe o está vacía.
    """
    if not os.path.exists(carpeta):
        return []
    if not os.path.isdir(carpeta):
        return []
    try:
        entries = os.listdir(carpeta)
    except OSError:
        return []
    pdfs = sorted(
        os.path.join(carpeta, name)
        for name in entries
        if name.lower().endswith(".pdf")
    )
    return pdfs


def validar_bill_minimo(bill: Optional[Dict]) -> bool:
    """
    Valida que un bill extraído tenga los campos mínimos requeridos.

    Args:
        bill: Dict con datos del invoice

    Returns:
        True si tiene invoice_number, invoice_date, vendor_name, y total_amount
    """
    if not bill or not isinstance(bill, dict):
        return False
    required = ["invoice_number", "invoice_date", "vendor_name", "total_amount"]
    for field in required:
        value = bill.get(field)
        if value is None or value == "":
            return False
    return True


def extraer_bills_de_pdf(pdf_path: str) -> List[Dict]:
    """Extrae bills de PDF usando Gemini 2.5 Flash."""

    print(f"\n📄 Procesando PDF: {os.path.basename(pdf_path)}")
    print(f"   Ruta completa: {pdf_path}")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ PDF no encontrado: {pdf_path}")

    print("🔄 Convirtiendo PDF a imágenes...")
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, dpi=300)
        print(f"✓ {len(images)} páginas convertidas")
    except Exception as e:
        raise Exception(f"❌ Error convirtiendo PDF: {e}")

    print("🤖 Analizando con Gemini 2.5 Flash...")
    print("   (Esto puede tomar 10-30 segundos)")

    content_parts = [{"text": OCR_PROMPT}]

    for img in images:
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        img_data = img_bytes.read()

        content_parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": base64.b64encode(img_data).decode('utf-8')
            }
        })

    try:
        client = _get_gemini_client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=content_parts,
            config={
                "temperature": 0.1,
                "response_modalities": ["TEXT"],
                "response_mime_type": "application/json"
            }
        )
    except Exception as e:
        raise Exception(f"❌ Error llamando a Gemini: {e}")

    try:
        bills_data = json.loads(response.text)

        if isinstance(bills_data, dict):
            if 'invoices' in bills_data:
                bills_data = bills_data['invoices']
            elif 'bills' in bills_data:
                bills_data = bills_data['bills']

        if not isinstance(bills_data, list):
            bills_data = [bills_data]

        validos = [b for b in bills_data if validar_bill_minimo(b)]
        invalidos = len(bills_data) - len(validos)
        if invalidos > 0:
            print(f"   ⚠️  {invalidos} bill(s) descartado(s) por validación")

        print(f"\n✅ {len(validos)} invoices extraídos:")
        for i, bill in enumerate(validos, 1):
            print(f"   {i}. Invoice #{bill.get('invoice_number')} - "
                  f"{bill.get('vendor_name')} - "
                  f"${bill.get('total_amount', 0):,.2f}")

        return validos

    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON: {e}")
        print(f"Respuesta raw: {response.text[:500]}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def generar_csv_preview(bills: List[Dict], output_path: str = "bills_preview.csv") -> str:
    """Genera CSV preview de bills."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_path.replace(".csv", f"_{timestamp}.csv")

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'Status', 'Invoice_Number', 'Invoice_Date', 'Vendor_Name',
            'Customer_Name', 'Total_Amount', 'Tax_Amount', 'Account_Name',
            'Terms', 'Notes'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for bill in bills:
            writer.writerow({
                'Status': '✓',
                'Invoice_Number': bill.get('invoice_number', ''),
                'Invoice_Date': bill.get('invoice_date', ''),
                'Vendor_Name': bill.get('vendor_name', ''),
                'Customer_Name': bill.get('customer_name', ''),
                'Total_Amount': bill.get('total_amount', 0),
                'Tax_Amount': bill.get('tax_amount', ''),
                'Account_Name': 'Prepaid Material',
                'Terms': bill.get('terms', ''),
                'Notes': ''
            })

    print(f"\n📊 CSV preview generado: {output_path}")
    return output_path


def procesar_lote_ocr(
    carpeta: str = "Pending bills",
    mover_exitosos: bool = False,
    carpeta_procesados: str = "Processed bills",
    carpeta_fallidos: Optional[str] = None
) -> Dict:
    """
    Procesa todos los PDFs en una carpeta con OCR Gemini.

    Si ≤5 bills: muestra cada uno en terminal para revisión inline.
    Si >5 bills: genera CSV preview para editar en Excel.
    """
    if not os.path.exists(carpeta):
        return {"error": f"Carpeta '{carpeta}' no existe"}

    pdfs = listar_pdfs_en_carpeta(carpeta)
    if not pdfs:
        return {"error": f"No se encontraron PDFs en '{carpeta}'"}

    todos_los_bills = []
    errores = []

    for pdf_filename in pdfs:
        pdf_path = os.path.join(carpeta, pdf_filename)
        try:
            bills = extraer_bills_de_pdf(pdf_path)
            if bills:
                todos_los_bills.extend(bills)
                print(f"  ✅ {pdf_filename}: {len(bills)} bill(s) extraídos")
            else:
                raise ValueError("No se pudo extraer información")
        except Exception as e:
            error_msg = f"❌ {pdf_filename}: {e}"
            print(f"  {error_msg}")
            errores.append(error_msg)

    if not todos_los_bills:
        return {"error": "No se pudo extraer información de ningún PDF", "errores": errores}

    total_bills = len(todos_los_bills)

    # ≤5 bills: mostrar en terminal para revisión inline
    if total_bills <= 5:
        print(f"\n📋 {total_bills} bill(s) extraídos. Revisión inline:\n")
        for i, bill in enumerate(todos_los_bills, 1):
            print(f"  ┌─ Bill #{i} ─────────────────────────────")
            for key in ['vendor_name', 'invoice_number', 'invoice_date',
                        'total_amount', 'tax_amount', 'account_name']:
                val = bill.get(key, '')
                if val:
                    print(f"  │ {key}: {val}")
            print(f"  └──────────────────────────────────────────")

        print(f"\n💡 Corregí los datos diciendo: 'bill #2 es de CFE, cuenta Equipment'")
        print(f"   Cuando estén correctos: 'crea los {total_bills} bills'")

        return {
            "success": True,
            "total_bills": total_bills,
            "bills": todos_los_bills,
            "mode": "inline",
            "errores": errores if errores else None,
        }

    # >5 bills: generar CSV para editar en Excel
    csv_path = generar_csv_preview(todos_los_bills)
    print(f"\n📊 {total_bills} bills extraídos. CSV generado para editar:")
    print(f"   {csv_path}")
    print(f"\n💡 Editalo en Excel, luego decí: 'procesa el CSV corregido {csv_path}'")

    return {
        "success": True,
        "total_bills": total_bills,
        "csv_path": csv_path,
        "mode": "csv",
        "errores": errores if errores else None,
    }

# ═══════════════════════════════════════════════════════════════════════
# PROCESAR CSV CORREGIDO — flujo post-edición
# ═══════════════════════════════════════════════════════════════════════
# PROCESAR CSV CORREGIDO — flujo post-edición
# ═══════════════════════════════════════════════════════════════════════

def procesar_csv_corregido(csv_path: str, cuenta_default: str = None) -> Dict:
    """Lee el CSV editado por el usuario y extrae los bills corregidos.

    Columnas esperadas en el CSV:
      Status, Invoice_Number, Invoice_Date, Vendor_Name,
      Customer_Name, Total_Amount, Tax_Amount, Account_Name,
      Terms, Notes

    Para cada fila donde Status != '✓' (corregida), registra un
    provider tip con las diferencias encontradas.

    Returns:
        Dict con bills listos para crear y tips de aprendizaje.
    """
    import csv as csv_module
    from pathlib import Path

    if not Path(csv_path).exists():
        return {"success": False, "error": f"CSV no encontrado: {csv_path}"}

    bills = []
    tips_learned = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv_module.DictReader(f)
        for row in reader:
            status = row.get('Status', '').strip()
            vendor = row.get('Vendor_Name', '').strip()
            amount = float(row.get('Total_Amount', 0))
            account = row.get('Account_Name', '').strip() or cuenta_default or ''
            customer = row.get('Customer_Name', '').strip()
            invoice_num = row.get('Invoice_Number', '').strip()
            invoice_date = row.get('Invoice_Date', '').strip()
            notes = row.get('Notes', '').strip()

            if not vendor or not amount:
                continue

            # Detectar campos corregidos por el usuario (Status != ✓)
            if status and status != '✓':
                corrections = []
                if account:
                    corrections.append(f"Cuenta contable: {account}")
                if customer:
                    corrections.append(f"Cliente: {customer}")
                if notes:
                    corrections.append(f"Notas: {notes}")
                if corrections:
                    tip = " | ".join(corrections)
                    tips_learned.append({"provider": vendor, "tip": tip})

            bills.append({
                "vendor_name": vendor,
                "invoice_number": invoice_num,
                "invoice_date": invoice_date,
                "total_amount": amount,
                "tax_amount": row.get('Tax_Amount', ''),
                "account_name": account,
                "customer_name": customer,
                "terms": row.get('Terms', ''),
                "notes": notes,
                "status": status,
            })

    return {
        "success": True,
        "bills": bills,
        "total": len(bills),
        "tips_learned": tips_learned,
        "tips_count": len(tips_learned),
    }
