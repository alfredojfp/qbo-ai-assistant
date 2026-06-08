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
Analiza este documento que contiene múltiples INVOICES/BILLS.

Para CADA invoice encontrado, extrae:

CAMPOS OBLIGATORIOS:
- invoice_number: Número del invoice
- invoice_date: Fecha en formato YYYY-MM-DD
- vendor_name: Nombre completo del vendor/proveedor
- customer_name: Nombre del cliente
- total_amount: Monto total final (número sin $)
- balance: Balance pendiente

CAMPOS OPCIONALES (usa null si no existen):
- subtotal: Subtotal antes de impuestos
- tax_amount: Monto de impuestos
- po_number: Número de Purchase Order
- terms: Términos de pago

REGLAS:
1. Retorna array JSON con TODOS los invoices
2. Montos como números (float), NO strings
3. Fechas en formato YYYY-MM-DD
4. Si campo opcional no existe, usa null
5. No dupliques invoices

Retorna SOLO JSON válido.
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
    Procesa todos los PDFs de una carpeta en lote.

    Args:
        carpeta: Carpeta con PDFs a procesar
        mover_exitosos: Si True, mueve PDFs procesados a carpeta_procesados
        carpeta_procesados: Destino de PDFs exitosos
        carpeta_fallidos: Destino de PDFs fallidos (None = no mover)

    Returns:
        Dict con resumen: total_pdfs, bills_extraidos, errores, detalles, csv_path
    """
    print(f"\n📁 PROCESAMIENTO EN LOTE: {carpeta}")
    print("=" * 70)

    pdfs = listar_pdfs_en_carpeta(carpeta)

    if not pdfs:
        print(f"⚠️  No se encontraron PDFs en '{carpeta}'")
        return {
            "total_pdfs": 0,
            "bills_extraidos": 0,
            "errores": 0,
            "detalles": [],
            "detalles_errores": [],
            "csv_path": None
        }

    print(f"📄 {len(pdfs)} PDF(s) encontrado(s)\n")

    todos_los_bills: List[Dict] = []
    detalles: List[Dict] = []
    detalles_errores: List[Dict] = []

    for i, pdf_path in enumerate(pdfs, 1):
        nombre = os.path.basename(pdf_path)
        print(f"[{i}/{len(pdfs)}] {nombre}")

        try:
            bills = extraer_bills_de_pdf(pdf_path)
            todos_los_bills.extend(bills)
            detalles.append({
                "pdf": nombre,
                "status": "ok",
                "bills": len(bills)
            })

            if mover_exitosos:
                _mover_pdf(pdf_path, carpeta_procesados)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            detalles_errores.append({
                "pdf": nombre,
                "error": str(e)
            })
            if carpeta_fallidos:
                _mover_pdf(pdf_path, carpeta_fallidos)

        print()

    csv_path = None
    if todos_los_bills:
        csv_path = generar_csv_preview(todos_los_bills)

    total = len(pdfs)
    errores = len(detalles_errores)
    exitosos = total - errores

    print("=" * 70)
    print("📊 RESUMEN DEL LOTE")
    print("=" * 70)
    print(f"Total PDFs:           {total}")
    print(f"✅ Exitosos:          {exitosos}")
    print(f"❌ Con errores:       {errores}")
    print(f"📋 Bills extraídos:   {len(todos_los_bills)}")
    if csv_path:
        print(f"📊 CSV consolidado:   {csv_path}")
    print("=" * 70)

    return {
        "total_pdfs": total,
        "bills_extraidos": len(todos_los_bills),
        "errores": errores,
        "detalles": detalles,
        "detalles_errores": detalles_errores,
        "csv_path": csv_path
    }


def _mover_pdf(origen: str, destino_carpeta: str) -> None:
    """Mueve un PDF a una carpeta destino, creándola si no existe."""
    os.makedirs(destino_carpeta, exist_ok=True)
    destino = os.path.join(destino_carpeta, os.path.basename(origen))
    if os.path.exists(destino):
        base, ext = os.path.splitext(destino)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = f"{base}_{timestamp}{ext}"
    shutil.move(origen, destino)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--help", "-h"):
            print("Uso:")
            print("  python ocr_bills.py                          # procesa Pending bills/")
            print("  python ocr_bills.py <pdf>                    # procesa un PDF")
            print("  python ocr_bills.py --lote [carpeta]         # procesa toda la carpeta")
            print("  python ocr_bills.py --lote --mover [carpeta] # mueve exitosos a Processed bills/")
        elif arg == "--lote":
            carpeta = sys.argv[2] if len(sys.argv) > 2 else "Pending bills"
            mover = "--mover" in sys.argv
            procesar_lote_ocr(
                carpeta=carpeta,
                mover_exitosos=mover,
                carpeta_fallidos="_failed" if mover else None
            )
        else:
            if os.path.exists(arg):
                bills = extraer_bills_de_pdf(arg)
                if bills:
                    generar_csv_preview(bills)
            else:
                print(f"❌ Archivo no encontrado: {arg}")
    else:
        carpeta = "Pending bills"
        if os.path.exists(carpeta):
            pdfs = listar_pdfs_en_carpeta(carpeta)
            if pdfs:
                procesar_lote_ocr(carpeta=carpeta, mover_exitosos=False)
            else:
                print("❌ No hay PDFs en 'Pending bills/'")
        else:
            print("❌ Carpeta 'Pending bills' no existe")


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
