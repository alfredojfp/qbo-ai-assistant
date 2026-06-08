# Política de Privacidad — Dexter QBO Agent

**Última actualización:** Junio 2026

---

## 1. Información General

Dexter ("la Aplicación") es un software de automatización contable desarrollado y operado por Alfredo ("el Desarrollador"). Esta Política de Privacidad describe cómo se manejan los datos cuando usás Dexter.

---

## 2. Datos que Dexter NO Recopila

Dexter **no envía, transmite ni almacena** en servidores externos ningún dato contable. Todo el procesamiento ocurre localmente en tu computadora.

**Dexter NO recopila:**
- Datos de tu empresa (facturas, clientes, balances, transacciones)
- Credenciales de QuickBooks (Client ID, Client Secret, tokens)
- Archivos procesados (PDFs, CSVs, estados de cuenta)
- Información personal de clientes o proveedores
- Datos bancarios

---

## 3. Datos que Dexter SÍ Procesa (Localmente)

Para funcionar, Dexter accede **solo en tu máquina** a:

| Dato | Ubicación | Propósito |
|---|---|---|
| Tokens OAuth QBO | `.env` + `companies/{nombre}/meta.json` | Autenticación con QuickBooks API |
| API Key OpenRouter | `.env` | Llamadas al modelo LLM (DeepSeek) |
| API Key Gemini | `.env` | OCR de facturas y estados de cuenta |
| Chart of Accounts | `data/chart_of_accounts.json` | Caché local para búsquedas rápidas |
| Historial de clasificaciones | `companies/{nombre}/classification_history.json` | Aprendizaje de patrones bank feed |
| Memoria del agente | `companies/{nombre}/MEMORY.md` | Preferencias y aprendizajes |
| Logs de errores | `logs/dexter_errors.log` | Diagnóstico y depuración |

---

## 4. Servicios de Terceros

Dexter se comunica con los siguientes servicios externos. Cada uno tiene su propia política de privacidad:

| Servicio | Qué datos envía | Política de Privacidad |
|---|---|---|
| **Intuit (QuickBooks API)** | Operaciones contables (crear facturas, buscar clientes, etc.) | [Intuit Privacy](https://www.intuit.com/privacy/) |
| **OpenRouter** | Mensajes de conversación para procesamiento LLM | [OpenRouter Privacy](https://openrouter.ai/privacy) |
| **Google Gemini** | Imágenes de PDFs para OCR | [Google Privacy](https://policies.google.com/privacy) |

**Importante:** Las API keys de estos servicios se almacenan ÚNICAMENTE en tu archivo `.env` local. Dexter nunca las comparte ni las transmite a terceros no autorizados.

---

## 5. Seguridad

- Las credenciales se almacenan en `~/.config/dexter/CREDENTIALS` con permisos `chmod 600` (solo lectura para el propietario)
- El archivo `.env` está en `.gitignore` y nunca se sube al repositorio
- El pre-commit hook escanea en busca de filtraciones de API keys
- Los tokens OAuth se refrescan automáticamente y se almacenan por empresa
- No se utiliza ninguna base de datos externa — todo es archivos locales

---

## 6. Retención de Datos

Todos los datos residen en tu computadora. Vos controlás:
- **Eliminar una empresa:** borrá la carpeta `companies/{nombre}/`
- **Eliminar logs:** usá el comando `limpiar_log_errores` en Dexter
- **Eliminar memoria:** borrá `companies/{nombre}/MEMORY.md`
- **Eliminar todo:** desinstalá el software y borrá la carpeta del proyecto

---

## 7. Tus Derechos

Como todos los datos residen en tu máquina, vos tenés control total:
- **Acceso:** todos los archivos están en la carpeta del proyecto
- **Rectificación:** editá cualquier archivo `.md` o `.json` directamente
- **Eliminación:** borrá los archivos o la carpeta del proyecto
- **Portabilidad:** copiá la carpeta `companies/` a otra instalación de Dexter

---

## 8. Cambios a esta Política

Esta política puede actualizarse. La versión más reciente estará disponible en el repositorio del proyecto.

---

## 9. Contacto

Para preguntas sobre esta política de privacidad:
- Abrí un issue en el repositorio del proyecto
- Contactá al Desarrollador directamente

---

**Al usar Dexter, confirmás que entendés y aceptás esta Política de Privacidad.**
