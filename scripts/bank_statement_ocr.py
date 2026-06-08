"""
Bank Statement OCR — convierte PDFs de estados de cuenta bancarios a CSV.

Bancos típicos y sus formatos:
  - Santander: columnas en español, balance running
  - BBVA: layout con encabezados azules
  - Chase: formato US, fechas MM/DD/YYYY
  - Banorte: formato MX, comisiones incluidas
  - HSBC: multi-columna con referencia

El módulo usa Gemini 2.0 Flash para extraer transacciones de cualquier
formato de PDF y las convierte a CSV compatible con el reconciliation engine.
"""
import base64
import csv
import io
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ── Configurable ────────────────────────────────────────────────────
DEFAULT_INPUT_DIR = "Pending bank statements"
DEFAULT_OUTPUT_DIR = "data"
# ─────────────────────────────────────────────────────────────────────

# Prompt especializado para extracción de estados de cuenta bancarios
BANK_STATEMENT_PROMPT = """
Analiza este extracto bancario (estado de cuenta). Extrae TODAS las
transacciones visibles en cada pagina, linea por linea.

Para CADA transaccion encontrada, extrae:

CAMPOS OBLIGATORIOS:
- date: Fecha de la transaccion en formato YYYY-MM-DD
- description: Descripcion completa (incluye referencia si existe)
- amount: Monto de la transaccion como numero (positivo=credito, negativo=debito)

CAMPOS OPCIONALES (usa null si no existen):
- debit: Monto del debito/cargo (numero positivo o null)
- credit: Monto del credito/abono (numero positivo o null)
- balance: Saldo despues de la transaccion (numero o null)
- reference: Numero de referencia, cheque o ID (string o null)
- category: Categoria sugerida por el banco (string o null)

MANEJO DE CASOS REALES DE BANCOS:
- MULTIPLES COLUMNAS: identifica correctamente fecha, descripcion, cargo,
  abono y saldo, sin importar el orden de las columnas.
- PAGINAS CON ENCABEZADOS: ignora encabezados repetidos. No los trates
  como transacciones.
- SALDOS INTERMEDIOS: si aparece un balance despues de cada linea,
  incluilo en el campo 'balance'.
- COMISIONES BANCARIAS: tratalas como transacciones normales.
  description='Comision bancaria' u description original del banco.
- INTERESES GANADOS: creditos con description='Intereses' o similar.
- TRANSFERENCIAS: inclui el nombre del destinatario/remitente en description.
- CHEQUES: inclui el numero de cheque en 'reference'.
- FORMATO DE FECHA: convierte a YYYY-MM-DD sin importar si el banco usa
  DD/MM/YYYY, MM/DD/YYYY, DD-Mon-YYYY, etc.
- MONTOS CON SIMBOLOS: extrae solo el numero, sin $, USD, MXN, etc.
- MONTOS ENTRE PARENTESIS: (500.00) significa -500.00 (debito).
- LINEAS CONTINUACION: si una transaccion ocupa 2+ lineas, unilas en
  una sola. La segunda linea suele estar indentada o sin fecha.
- PAGINAS EN BLANCO: si una pagina esta en blanco, simplemente ignora.
- MEMO/NOTAS: inclui cualquier nota o memo en la descripcion.

REGLAS:
1. Retorna array JSON con TODAS las transacciones, en orden cronologico
2. Montos como numeros (float), NO strings. Ej: 1500.00 no "1,500.00"
3. Fechas en YYYY-MM-DD
4. Si el PDF no contiene transacciones, retorna array vacio []
5. Ignora lineas de encabezado, totales de pagina, y pies de pagina
6. No dupliques transacciones entre paginas
7. El balance debe ser consistente: si la pagina siguiente empieza con
   el mismo balance que termino la anterior, es correcto

Retorna SOLO JSON valido, sin explicaciones.
Formato: [{"date": "2026-06-01", "description": "Pago nomina", "amount": -5000.00, "balance": 45000.00, "reference": "CHK-1001"}, ...]
"""


def _get_gemini_client():
    """Lazy init del cliente Gemini."""
    try:
        from google import genai
    except ImportError:
        raise ImportError("pip install google-genai")
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_GEMINI_API_KEY no encontrada en .env")
    return genai.Client(api_key=api_key)


def extract_transactions_from_pdf(pdf_path: str, bank_name: str = None,
                                  provider_tips: List[str] = None) -> List[Dict]:
    """Extrae transacciones de un PDF de estado de cuenta bancario.

    Args:
        pdf_path: Ruta al PDF del banco
        bank_name: Nombre del banco (Santander, BBVA, etc.) para tips específicos
        provider_tips: Tips de extracción para este banco (del sistema de aprendizaje)

    Returns:
        Lista de transacciones extraídas
    """
    from pdf2image import convert_from_path

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")

    print(f"📄 Procesando: {pdf_path.name}")
    print(f"   Convirtiendo {pdf_path.stat().st_size // 1024}KB a imágenes...")

    images = convert_from_path(str(pdf_path), dpi=250)
    print(f"   ✓ {len(images)} páginas convertidas")

    # Construir prompt con tips específicos del banco si existen
    prompt = BANK_STATEMENT_PROMPT
    if bank_name and provider_tips:
        tip_text = "\n".join(f"  • {bank_name}: {t}" for t in provider_tips)
        prompt += f"\n\nTIPS ESPECIFICOS PARA {bank_name}:\n{tip_text}"

    # Preparar imágenes para Gemini
    client = _get_gemini_client()
    content_parts = [{"text": prompt}]

    for img in images:
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        content_parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": base64.b64encode(img_bytes.read()).decode("utf-8"),
            }
        })

    print(f"   🤖 Analizando con Gemini 2.0 Flash...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=content_parts,
    )

    # Parsear respuesta JSON
    raw = response.text.strip()
    # Limpiar markdown code blocks si Gemini los agrega
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3]

    try:
        transactions = json.loads(raw)
    except json.JSONDecodeError:
        # Intentar extraer el array JSON de la respuesta
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            transactions = json.loads(raw[start:end])
        else:
            raise ValueError(f"No se pudo parsear JSON de Gemini: {raw[:200]}")

    if not isinstance(transactions, list):
        raise ValueError(f"Gemini no retornó una lista: {type(transactions)}")

    print(f"   ✅ {len(transactions)} transacciones extraídas")
    return transactions


def normalize_transactions(transactions: List[Dict]) -> List[Dict]:
    """Normaliza transacciones al formato estándar del reconciliation engine.

    Asegura que cada transacción tenga:
      - date (YYYY-MM-DD)
      - description (string)
      - debit (float positivo o None)
      - credit (float positivo o None)
      - balance (float o None)
      - reference (string o None)
    """
    normalized = []
    for txn in transactions:
        amount = txn.get("amount", 0) or 0
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            amount = 0

        debit = txn.get("debit")
        credit = txn.get("credit")

        # Si no hay debit/credit explícito, derivar del amount
        if debit is None and credit is None:
            if amount < 0:
                debit = abs(amount)
                credit = None
            elif amount > 0:
                debit = None
                credit = amount
            else:
                debit = None
                credit = None
        else:
            try:
                debit = float(debit) if debit else None
            except (TypeError, ValueError):
                debit = None
            try:
                credit = float(credit) if credit else None
            except (TypeError, ValueError):
                credit = None

        balance = txn.get("balance")
        try:
            balance = float(balance) if balance else None
        except (TypeError, ValueError):
            balance = None

        normalized.append({
            "date": txn.get("date", ""),
            "description": (txn.get("description") or "").strip(),
            "debit": debit,
            "credit": credit,
            "balance": balance,
            "reference": txn.get("reference") or None,
        })

    return normalized


def transactions_to_csv(transactions: List[Dict], output_path: str = None) -> str:
    """Convierte transacciones normalizadas a CSV compatible con BNK-RECON.

    Formato de salida:
      date,description,debit,credit,balance,reference
    """
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/bank_statement_{timestamp}.csv"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "date", "description", "debit", "credit", "balance", "reference"
        ])
        writer.writeheader()
        for txn in transactions:
            writer.writerow({
                "date": txn.get("date", ""),
                "description": txn.get("description", ""),
                "debit": txn.get("debit", "") if txn.get("debit") is not None else "",
                "credit": txn.get("credit", "") if txn.get("credit") is not None else "",
                "balance": txn.get("balance", "") if txn.get("balance") is not None else "",
                "reference": txn.get("reference", "") if txn.get("reference") else "",
            })

    print(f"📊 CSV generado: {output_path}")
    return output_path


def process_bank_statement(pdf_path: str, bank_name: str = None,
                           provider_tips: List[str] = None) -> Dict:
    """Procesa un PDF de estado de cuenta bancario completo.

    Flujo: PDF → Gemini OCR → normalizar → CSV

    Returns:
        Dict con resumen: total, csv_path, transactions, etc.
    """
    raw = extract_transactions_from_pdf(pdf_path, bank_name, provider_tips)
    normalized = normalize_transactions(raw)
    csv_path = transactions_to_csv(normalized)

    total_credits = sum(t["credit"] for t in normalized if t["credit"])
    total_debits = sum(t["debit"] for t in normalized if t["debit"])

    return {
        "success": True,
        "total": len(normalized),
        "csv_path": csv_path,
        "transactions": normalized[:5],  # primeras 5 como preview
        "summary": {
            "creditos": round(total_credits, 2),
            "debitos": round(total_debits, 2),
            "neto": round(total_credits - total_debits, 2),
        },
    }
