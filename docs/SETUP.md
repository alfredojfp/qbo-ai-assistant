# 🧠 Dexter — Guía de Configuración Completa

> **Versión:** 4.1.0-dev | **Tests:** 692 | **Tools:** 105
>
> Esta guía cubre todo lo necesario para instalar, configurar y usar Dexter desde cero.

---

## 1. Requisitos Previos

- **Python 3.10+** instalado
- **Git** (para clonar el repo)
- Una cuenta de **Intuit Developer** (https://developer.intuit.com)
- Una cuenta de **OpenRouter** (https://openrouter.ai) para el LLM
- (Opcional) Una cuenta de **Google AI** para OCR de facturas

---

## 2. Instalación

```bash
# Clonar el repositorio
git clone https://github.com/alfredojfp/qbo-ai-assistant.git
cd qbo-ai-assistant

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 3. APIs y Credenciales

Dexter necesita **3 APIs** para funcionar. Conseguilas en este orden:

### 3.1 QuickBooks Online API (OBLIGATORIO)

1. Entrá a https://developer.intuit.com y crea una cuenta
2. Andá a **Dashboard → My Apps → Create an App**
3. Seleccioná **QuickBooks Online and Payments**
4. En **Keys & Credentials**, copiá:
   - `Client ID`
   - `Client Secret`
5. En **Redirect URIs**, agregá: `http://localhost:8000/callback`
6. Guardá estos datos

### 3.2 OpenRouter API (OBLIGATORIO — para el LLM)

1. Entrá a https://openrouter.ai y crea una cuenta
2. Andá a **Settings → API Keys**
3. Creá una nueva key y copiala
4. Dexter usa DeepSeek V3 ($0.14/1M tokens input)
5. Cargá saldo mínimo de $5 en OpenRouter

### 3.3 Google Gemini API (OPCIONAL — para OCR de facturas)

1. Entrá a https://aistudio.google.com/apikey
2. Creá una API key
3. Solo necesaria si vas a procesar PDFs de facturas

---

## 4. Archivo .env

Creá un archivo `.env` en la raíz del proyecto:

```bash
# ── QuickBooks Online ──
QB_CLIENT_ID=ABdHimJO...        # De Intuit Developer
QB_CLIENT_SECRET=tu_secret...    # De Intuit Developer
QB_REDIRECT_URI=http://localhost:8000/callback
QB_ENV=development
QB_MINOR_VERSION=70

# ── LLM (Proveedor de IA) ──
LLM_PROVIDER=openrouter         # openrouter | openai | deepseek | gemini | groq | custom
LLM_API_KEY=sk-or-v1-...        # Tu API key del proveedor elegido
LLM_MODEL=                      # Opcional: modelo específico (default del proveedor)

# ── Google Gemini (OCR, opcional) ──
GOOGLE_GEMINI_API_KEY=AIza...    # De Google AI Studio

# ── TSheets (marcador de tiempo, opcional) ──
TSHEETS_ACCESS_TOKEN=...         # De TSheets API Add-on
TSHEETS_REFRESH_TOKEN=...

# ── Configuración avanzada ──
QB_REQUEST_TIMEOUT=30
MAX_REPORT_BYTES=250000
```

---

## 5. OAuth — Conectar Dexter a QBO

La primera vez necesitás autorizar a Dexter para acceder a tu QBO:

```bash
python3 scripts/oauth_flow.py
```

Esto:
1. Abre tu navegador en la página de login de Intuit
2. Inicia sesión y autoriza la app
3. Espera el callback en `localhost:8000`
4. Guarda los tokens automáticamente en `.env`

Si el token expira, Dexter te ofrece re-autenticar automáticamente.

---

## 6. Iniciar Dexter

```bash
./run_dexter.sh
```

La primera vez verás:

```
┌──────────────────────────────────────────┐
│   🧠  DEXTER  ·  QBO Assistant           │
│            v4.1.0-dev                     │
└──────────────────────────────────────────┘

📁 Empresa activa: (ninguna)
  ¿Deseas registrar una? (s/N): s

  Nombre de la empresa: Mi Empresa
  Link de QBO o Realm ID: https://app.qbo.intuit.com/app/companyfile?id=123456789

🔑 Tokens cargados para Mi Empresa
  Cargando contexto...
  Contexto: 91 cuentas · 0 reportes · 0 reglas · ES

  🔍 Primera carga detectada. Estudiando la empresa...
  ✅ Perfil generado: companies/Mi Empresa/PROFILE.md

  ✓ Conexión establecida

  DEXTER listo. 'menu' para ayuda, 'salir' para terminar.

❯ Tú: hola

  Dexter · ¡Hola Alfredo! ¿En qué puedo ayudarte?
```

---

## 7. Comandos Básicos

| Comando | Qué hace |
|---|---|
| `busca el cliente X` | Buscar cliente en QBO |
| `crea un cliente con nombre Y` | Crear cliente nuevo |
| `dame el P&L de este mes` | Reporte de pérdidas y ganancias |
| `crea un estimate para X por $1,000` | Crear cotización |
| `procesa los bills pendientes` | OCR de PDFs en Pending bills/ |
| `menu` | Mostrar todos los comandos |
| `salir` | Cerrar sesión |

---

## 8. Funciones Avanzadas

### 8.1 Dry-Run (Simulación)
Agregá `--dry-run` al final para simular sin tocar QBO:
```
❯ Tú: crea un estimate para X por $1,000 --dry-run
  → Simulado. Nada se creó.
❯ Tú: ejecutalo
  → Creado de verdad.
```

### 8.2 Múltiples Empresas
```
❯ Tú: /gestionar_empresas accion=registrar nombre="Otra Empresa" link_o_id="URL o realm"
```

Cada empresa tiene sus propios tokens, chart, memoria y clasificaciones. Cambiá con:
```
❯ Tú: /gestionar_empresas accion=cambiar nombre="Otra Empresa"
```

### 8.3 Memoria Persistente
Dexter recuerda entre sesiones. Después de cada interacción guarda automáticamente. Podés ver:
```
cat companies/Mi\ Empresa/MEMORY.md
```

### 8.4 Perfil de Empresa
Dexter estudia QBO y genera un perfil automático. Regenerá con:
```
❯ Tú: /estudiar empresa
```

### 8.5 OCR de Facturas y Estados de Cuenta
```
# 1. Poné PDFs en Pending bills/
# 2.
❯ Tú: procesa los bills pendientes
# 3. ≤5 bills: revisá en terminal
#    >5 bills: editá el CSV en Excel
# 4.
❯ Tú: procesa el CSV corregido ...
# 5.
❯ Tú: crea los bills
```

---

## 9. Solución de Problemas

| Problema | Solución |
|---|---|
| Token expirado | Dexter ofrece re-auth automático. Si falla: `python3 scripts/oauth_flow.py` |
| Error de conexión | Verificar internet. Si QBO está caído, esperar. |
| LLM no responde | Verificar saldo en OpenRouter |
| OCR no funciona | `pip install google-genai pdf2image` + `GEMINI_API_KEY` en .env |
| Error 401 | `python3 scripts/refresh_token.py` o re-OAuth |
| Tests fallan | `python3 -m unittest discover tests/` |

---

## 10. Archivos Importantes

| Archivo | Propósito |
|---|---|
| `.env` | Credenciales (NUNCA commitear) |
| `run_dexter.sh` | Launcher |
| `logs/dexter_errors.log` | Log de errores (JSONL rotado) |
| `companies/{nombre}/meta.json` | Tokens por empresa |
| `companies/{nombre}/MEMORY.md` | Memoria por empresa |
| `companies/{nombre}/PROFILE.md` | Perfil automático |
| `companies/{nombre}/classification_history.json` | Clasificaciones bank feed |
