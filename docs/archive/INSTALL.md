# 🚀 Guía de Instalación Detallada

Instrucciones paso a paso para instalar y configurar QuickBooks AI Assistant (Dexter).

---

## 📋 Prerrequisitos

| Requisito | Versión | Cómo verificar |
|-----------|---------|----------------|
| Python | 3.9 o superior | `python --version` |
| pip | 21+ | `pip --version` |
| Git | 2.30+ | `git --version` |
| Cuenta QuickBooks Online | Sandbox o Producción | [developer.intuit.com](https://developer.intuit.com) |
| API Key de OpenRouter | Activa | [openrouter.ai](https://openrouter.ai) |
| API Key de Google Gemini | Activa | [aistudio.google.com](https://aistudio.google.com) (para OCR) |

---

## 🪜 Instalación paso a paso

### Paso 1: Clonar o descargar el proyecto

```bash
git clone <url-del-repo>
cd "Qbo Scripts"
```

Si ya tienes el proyecto, solo navega al directorio:

```bash
cd "/ruta/a/Qbo Scripts"
```

### Paso 2: Crear entorno virtual

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Paso 3: Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Configurar credenciales

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales (ver sección [Variables de entorno](#-variables-de-entorno)).

### Paso 5: Configurar OAuth 2.0 con QuickBooks

1. Ve a [developer.intuit.com](https://developer.intuit.com) y crea una app
2. En la sección "Keys & OAuth", obtén tu `Client ID` y `Client Secret`
3. Configura redirect URI: `http://localhost:8000/callback` (o el que prefieras)
4. Autoriza la app contra tu empresa QBO: el script `scripts/refresh_token.py` te guiará
5. Tras autorizar, copia el `access_token` y `refresh_token` al `.env`

### Paso 6: Verificar instalación

```bash
python scripts/verify_setup.py
```

Salida esperada: todos los checks en verde ✅.

### Paso 7: Primer arranque

```bash
python main.py
```

Al iniciar, si tienes múltiples empresas configuradas, Dexter te preguntará con cuál trabajar.

---

## 🔐 Variables de entorno

| Variable | Descripción | Obligatoria |
|----------|-------------|-------------|
| `QB_ACCESS_TOKEN` | Token de acceso QBO (se refresca automáticamente) | Sí |
| `QB_REFRESH_TOKEN` | Token para refrescar el access token | Sí |
| `QB_CLIENT_ID` | Client ID de tu app QBO | Sí |
| `QB_CLIENT_SECRET` | Client Secret de tu app QBO | Sí |
| `QB_REALM_ID` | ID de la empresa QBO (Company ID) | Sí |
| `OPENROUTER_API_KEY` | API key de OpenRouter para DeepSeek V3 | Sí |
| `GEMINI_API_KEY` | API key de Google Gemini (solo si usas OCR) | No (recomendada) |

**Importante:**
- ❌ NUNCA subas `.env` a Git
- ✅ El archivo `.gitignore` ya excluye `.env`
- ✅ Para múltiples empresas, usa `company_manager.py` que gestiona los tokens por empresa

---

## 🐛 Troubleshooting de instalación

### Error: "No module named 'requests'"

```bash
# Asegúrate de tener el venv activado
source .venv/bin/activate  # o equivalente en Windows
pip install -r requirements.txt
```

### Error: "QB_ACCESS_TOKEN is missing"

Edita `.env` y agrega las credenciales. Ver [Paso 4](#paso-4-configurar-credenciales).

### Error: "Invalid client_id or client_secret"

Verifica que copiaste correctamente las credenciales desde developer.intuit.com, sin espacios extra.

### Error: "Token expired" persistente

```bash
python scripts/refresh_token.py
```

Si persiste, regenera el refresh token desde la app de Intuit.

### Error: "OPENROUTER_API_KEY is missing"

Crea una cuenta en [openrouter.ai](https://openrouter.ai) y obtén tu API key.

---

## ✅ Verificación final

Tras seguir todos los pasos, deberías poder:

- [x] Ejecutar `python main.py` sin errores
- [x] Ver el saludo de Dexter
- [x] Hacer una búsqueda de prueba: `"busca el cliente de prueba"`
- [x] Ver el chart de cuentas cargado

Si todo funciona, ¡ya estás listo para usar Dexter!

---

**Siguiente paso:** Lee [`USER_GUIDE.md`](USER_GUIDE.md) para aprender a usar el asistente.
