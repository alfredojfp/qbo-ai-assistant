# 🚀 QuickBooks AI Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)
![Status](https://img.shields.io/badge/status-Active-success.svg)

**Asistente conversacional inteligente para automatizar tareas contables en QuickBooks Online**

Desarrollado con DeepSeek V3 • OAuth 2.0 • Python

[Instalación Rápida](#-instalación-rápida) • [Características](#-características) • [Documentación](#-documentación) • [Ejemplos](#-ejemplos-de-uso)

</div>

---

## 📖 Descripción

QuickBooks AI Assistant es un asistente conversacional en español que te permite gestionar QuickBooks Online mediante comandos en lenguaje natural. Elimina la necesidad de navegar por la interfaz web para tareas contables repetitivas.

### ¿Qué puedes hacer?

- 💰 **Crear depósitos** de anticipos y prepagos de clientes
- 📄 **Generar facturas y bills** con comandos simples
- 📊 **Obtener reportes** (P&L, Balance Sheet) conversacionalmente
- 📁 **Procesar lotes CSV** de transacciones
- 🔍 **Buscar clientes, vendors y cuentas** con fuzzy matching
- 💵 **Registrar pagos** y aplicarlos a facturas
- 📈 **Monitorear costos** de uso del LLM en tiempo real

---

## ✨ Características

### 🤖 IA Conversacional
- **DeepSeek V3** vía OpenRouter con function calling
- **18 tools especializados** para QuickBooks
- **Comprende terminología** contable latinoamericana (anticipo, prepago, retainer)
- **Iteraciones automáticas** hasta completar tareas complejas

### 📊 Chart of Accounts Inteligente
- Carga automática desde QuickBooks Online
- Caché local con actualización diaria
- Fuzzy matching con 60% de similitud mínima
- Categorización automática: ACTIVO/PASIVO/INGRESO/GASTO

### 💰 Tracking de Costos
- Contador de tokens en tiempo real
- CSV histórico (nunca sobrescribe)
- Informe Excel con 4 hojas de análisis
- Costo promedio: ~$0.01 USD por sesión de 45 min

### 🔐 Autenticación Robusta
- OAuth 2.0 con QuickBooks
- Refresh automático de tokens
- Actualización segura de `.env`

### 📁 Procesamiento Batch
- Carga CSV con múltiples depósitos
- Validación automática de clientes y cuentas
- Reporte de errores por fila

---

## 🚀 Instalación Rápida

### Prerrequisitos

- Python 3.9+
- Cuenta QuickBooks Online (Sandbox o Producción)
- API Key de OpenRouter

### Paso 1: Clonar o descargar el proyecto

```bash
cd quickbooks-ai-assistant
```

### Paso 2: Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar credenciales

```bash
cp .env.example .env
# Edita .env con tus credenciales
```

### Paso 5: Verificar configuración

```bash
python scripts/verify_setup.py
```

### Paso 6: ¡Ejecutar!

```bash
python main.py
```

---

## 🎯 Uso Básico

```
👤 Tú: Muéveme $2500 de Client Retainers de Acme Corp a Checking Account

🤖 Asistente: 
   ✅ Depósito creado:
      • Acme Corp: $2,500.00 desde Client Retainers
      • Total depositado en Checking: $2,500.00
      • Fecha: 2026-01-20
```

### Comandos Rápidos (sin consumo de tokens)

```bash
¿cuánto he gastado?        # Estadísticas de la sesión
informe de tokens          # Genera Excel con análisis
refrescar chart            # Actualiza Chart of Accounts
template csv               # Crea plantilla de depósitos
listar reportes            # Muestra reportes guardados
salir                      # Termina la sesión
```

---

## 📚 Documentación

- 📘 **[QUICKSTART.md](QUICKSTART.md)** - Guía de inicio rápido (5 minutos)
- 📗 **[EXAMPLES.md](EXAMPLES.md)** - 10+ casos de uso detallados
- 📕 **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solución de problemas
- 📙 **[CONTEXT.md](CONTEXT.md)** - Contexto completo para LLMs
- 📔 **[CHANGELOG.md](CHANGELOG.md)** - Historial de versiones

---

## 💡 Ejemplos de Uso

### Crear Depósito Multi-Cliente
```
Muéveme $1500 de Client Retainers de Tech Inc y $2300 de 
Prepaid Labour de Design Co a Checking Account
```

### Generar Reporte P&L
```
Dame un Profit & Loss del 1 al 15 de enero y guárdalo como "Quincenal Ene"
```

### Procesar CSV Batch
```
Procesa el archivo deposits_january.csv
```

### Buscar Cuenta con Fuzzy Matching
```
Busca la cuenta "prepaid"
→ Retorna: Prepaid Expenses (95%), Prepaid Labour (87%)
```

---

## 🏗️ Arquitectura

```
QuickBooks AI Assistant
├── main.py (1,867 líneas)          # Aplicación principal
├── refresh_token.py                 # Script de refresh OAuth
├── .env                             # Credenciales (NO subir a Git)
├── requirements.txt                 # Dependencias Python
│
├── Archivos generados automáticamente:
│   ├── chart_of_accounts.json      # Caché del Chart of Accounts
│   ├── saved_reports.json          # Configuraciones de reportes
│   ├── token_usage.csv             # Histórico de consumo
│   └── token_usage_report.xlsx     # Informe Excel (sobrescribe)
│
└── scripts/
    └── verify_setup.py              # Verificación de configuración
```

---

## 🔧 Tecnologías

| Tecnología | Uso |
|------------|-----|
| **Python 3.9+** | Lenguaje principal |
| **QuickBooks Online API v3** | Integración contable |
| **OpenRouter API** | Acceso a DeepSeek V3 |
| **pandas** | Procesamiento de datos y CSV |
| **openpyxl** | Generación de reportes Excel |
| **requests** | HTTP requests |
| **python-dotenv** | Manejo de variables de entorno |

---

## 📊 Métricas

### Costos Promedio

| Operación | Tokens | Costo USD |
|-----------|--------|-----------|
| Búsqueda simple | ~1,000 | $0.0003 |
| Crear depósito | ~1,550 | $0.0005 |
| Reporte P&L | ~3,300 | $0.0012 |
| CSV batch (10 registros) | ~4,100 | $0.0012 |

### Sesión Promedio
- **Duración:** 30-45 minutos
- **Tokens:** 25,000 - 35,000
- **Costo:** $0.008 - $0.012 USD

### Proyección Mensual
- **20 sesiones/mes** → ~$0.20 USD/mes

---

## 🔒 Seguridad

✅ Credenciales en `.env` (no versionado)  
✅ Refresh automático de tokens  
✅ Validación de existencia antes de crear transacciones  
✅ Detección de duplicados potenciales  
✅ Validación de categorías de cuentas  

---

## 🐛 Troubleshooting Rápido

**Error: Token expirado**
```bash
# El sistema refresca automáticamente
# Si persiste, ejecuta:
python scripts/refresh_token.py
```

**Error: Cuenta no encontrada**
```
# El asistente usa fuzzy matching y sugiere alternativas
# Ejemplo: "prepaid" → Prepaid Expenses (95% similitud)
```

**Error: CSV mal formateado**
```bash
# Genera plantilla con formato correcto:
template csv
```

Ver [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para más detalles.

---

## 📈 Roadmap

- [ ] Interfaz web con Streamlit
- [ ] Reportes PDF automáticos
- [ ] Integración con Google Sheets
- [ ] Notificaciones Slack/Email
- [ ] Dashboard de analytics
- [ ] Soporte multi-empresa
- [ ] Comandos por voz

---

## 👨‍💻 Desarrollo

### Estructura del Código

```python
# main.py - Organización modular clara
# ==================== CONFIGURACIÓN ====================
# ==================== UTILIDADES GENERALES ====================
# ==================== AUTENTICACIÓN QUICKBOOKS ====================
# ==================== CHART OF ACCOUNTS ====================
# ==================== TRACKING DE TOKENS ====================
# ==================== BÚSQUEDAS EN QUICKBOOKS ====================
# ==================== CREACIÓN DE TRANSACCIONES ====================
# ==================== REPORTES ====================
# ==================== PROCESAMIENTO CSV ====================
# ==================== LLM INTEGRATION ====================
# ==================== TOOLS PARA EL LLM ====================
# ==================== COMANDOS RÁPIDOS ====================
# ==================== LOOP PRINCIPAL ====================
```

---

## 📄 Licencia

Proyecto privado desarrollado por **Alfredo** para automatización contable interna.

---

## 🙏 Créditos

- **Desarrollador:** Alfredo
- **LLM:** DeepSeek V3 vía OpenRouter
- **APIs:** QuickBooks Online API v3
- **Fecha:** Enero 2026

---

## 📞 Soporte

Para preguntas o problemas, consulta:
1. [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. [EXAMPLES.md](EXAMPLES.md)
3. [CONTEXT.md](CONTEXT.md)

---

<div align="center">

**Hecho con ❤️ para automatizar la contabilidad**

[⬆ Volver arriba](#-quickbooks-ai-assistant)

</div>
