from google import genai
import os
from dotenv import load_dotenv
from pdf2image import convert_from_path
import json
from typing import List, Dict
import csv
from datetime import datetime
import io
import base64

"""
MÓDULO OCR DE BILLS CON GEMINI 2.5 FLASH
MODELO: gemini-2.5-flash
RATE LIMITS (FREE TIER): 15 RPM, 500 RPD, 1M TPM
SDK: google-genai (nuevo)
"""

load_dotenv()

api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
if not api_key:
    raise ValueError("❌ GOOGLE_GEMINI_API_KEY no encontrada en .env")

GEMINI_CLIENT = genai.Client(api_key=api_key)


def extraer_bills_de_pdf(pdf_path: str) -> List[Dict]:
    """Extrae bills de PDF usando Gemini 2.5 Flash."""

    print(f"\n📄 Procesando PDF: {os.path.basename(pdf_path)}")
    print(f"   Ruta completa: {pdf_path}")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ PDF no encontrado: {pdf_path}")

    print("🔄 Convirtiendo PDF a imágenes...")
    try:
        images = convert_from_path(pdf_path, dpi=300)
        print(f"✓ {len(images)} páginas convertidas")
    except Exception as e:
        raise Exception(f"❌ Error convirtiendo PDF: {e}")

    prompt = """
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

    print("🤖 Analizando con Gemini 2.5 Flash...")
    print("   (Esto puede tomar 10-30 segundos)")

    content_parts = [{"text": prompt}]

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
        response = GEMINI_CLIENT.models.generate_content(
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

        print(f"\n✅ {len(bills_data)} invoices extraídos:")
        for i, bill in enumerate(bills_data, 1):
            print(f"   {i}. Invoice #{bill.get('invoice_number')} - "
                  f"{bill.get('customer_name')} - "
                  f"${bill.get('total_amount', 0):,.2f}")

        return bills_data

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


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        if os.path.exists("Pending bills"):
            pending_pdfs = [f for f in os.listdir("Pending bills") if f.endswith('.pdf')]
            if pending_pdfs:
                pdf_file = os.path.join("Pending bills", pending_pdfs[0])
            else:
                print("❌ No hay PDFs en 'Pending bills/'")
                exit(1)
        else:
            print("❌ Carpeta 'Pending bills' no existe")
            exit(1)

    if os.path.exists(pdf_file):
        bills = extraer_bills_de_pdf(pdf_file)

        if bills:
            csv_path = generar_csv_preview(bills)

            print(f"\n📊 RESUMEN:")
            print(f"   Total invoices: {len(bills)}")
            total_general = sum(b.get('total_amount', 0) for b in bills)
            print(f"   Total general: ${total_general:,.2f}")
        else:
            print("❌ No se pudieron extraer bills")
    else:
        print(f"❌ Archivo no encontrado: {pdf_file}")
