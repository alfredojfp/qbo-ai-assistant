# 🔧 QuickBooks AI Assistant - Troubleshooting

Guía completa de resolución de problemas comunes.

---

## 📑 Índice Rápido

1. [Problemas de Autenticación](#1-problemas-de-autenticación)
2. [Errores de Conexión](#2-errores-de-conexión)
3. [Problemas con el LLM](#3-problemas-con-el-llm)
4. [Errores en Transacciones](#4-errores-en-transacciones)
5. [Problemas con CSV](#5-problemas-con-csv)
6. [Errores de Chart of Accounts](#6-errores-de-chart-of-accounts)
7. [Problemas de Performance](#7-problemas-de-performance)
8. [Errores Generales](#8-errores-generales)
9. [Problemas Multi-Empresa (v3.5)](#9-problemas-multi-empresa-v35)

---

## 1. Problemas de Autenticación

### ❌ Error: "401 Unauthorized"

**Síntomas:**
```
❌ Error conectando a QuickBooks: 401 Unauthorized
```

**Causa:** Token de acceso expirado

**Solución Automática:**
El sistema intenta refrescar automáticamente. Espera unos segundos.

**Solución Manual:**
```bash
python scripts/refresh_token.py
```

**Si persiste:**
1. Verifica que `QB_REFRESH_TOKEN` en `.env` sea válido
2. Los refresh tokens expiran cada 100 días
3. Genera nuevos tokens desde QuickBooks Playground:
   https://developer.intuit.com/app/developer/playground

---

### ❌ Error: "Invalid Client Credentials"

**Síntomas:**
```
Error al refrescar token: invalid_client
```

**Causa:** `QB_CLIENT_ID` o `QB_CLIENT_SECRET` incorrectos

**Solución:**
1. Ve a: https://developer.intuit.com/app/developer/myapps
2. Selecciona tu app
3. Ve a "Keys & credentials"
4. Copia **Client ID** y **Client Secret**
5. Actualiza `.env`:
   ```env
   QB_CLIENT_ID=tu_client_id_correcto
   QB_CLIENT_SECRET=tu_client_secret_correcto
   ```

---

### ❌ Error: "Invalid Realm ID"

**Síntomas:**
```
Error: Realm 123456789 not found
```

**Causa:** `QB_REALM_ID` incorrecto

**Solución:**
1. Inicia sesión en QuickBooks Online
2. Observa la URL: `https://app.qbo.intuit.com/app/homepage?realmId=123456789`
3. El número después de `realmId=` es tu Realm ID
4. Actualiza `.env`:
   ```env
   QB_REALM_ID=123456789
   ```

---

## 2. Errores de Conexión

### ❌ Error: "Connection Timeout"

**Síntomas:**
```
requests.exceptions.ConnectTimeout: Connection to api.intuit.com timed out
```

**Causa:** Problemas de red o firewall

**Solución:**
1. Verifica tu conexión a internet
2. Intenta acceder a: https://developer.intuit.com
3. Si usas VPN, intenta desactivarla temporalmente
4. Verifica que no haya firewall bloqueando Python

---

### ❌ Error: "SSL Certificate Verification Failed"

**Síntomas:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solución (Linux/Mac):**
```bash
pip install --upgrade certifi
```

**Solución (Windows):**
```bash
pip install --upgrade certifi requests
```

---

### ❌ Error: "OpenRouter API Key Invalid"

**Síntomas:**
```
401: Invalid API key
```

**Solución:**
1. Ve a: https://openrouter.ai/keys
2. Verifica que tu key comience con `sk-or-v1-`
3. Si está revocada, crea una nueva
4. Actualiza `.env`:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-tu_nueva_key
   ```

---

## 3. Problemas con el LLM

### ❌ Error: "Rate Limit Exceeded"

**Síntomas:**
```
429: Too Many Requests - Rate limit exceeded
```

**Causa:** Demasiadas llamadas al LLM en poco tiempo

**Solución:**
1. Espera 1-2 minutos
2. OpenRouter tiene límites por minuto
3. Si persiste, verifica tu plan en: https://openrouter.ai/account

---

### ❌ Error: "Context Length Exceeded"

**Síntomas:**
```
Error: Context length exceeded (max 32000 tokens)
```

**Causa:** Conversación muy larga

**Solución:**
1. Reinicia el asistente: `salir` y vuelve a ejecutar `python main.py`
2. El historial se limpia al reiniciar
3. Para sesiones largas, reinicia cada 2-3 horas

---

### ❌ El LLM no responde o da respuestas incoherentes

**Síntomas:**
- Respuestas genéricas sin usar los tools
- No ejecuta las acciones solicitadas

**Causa:** Problema con el system prompt o iteraciones

**Solución:**
1. Sé más específico en tu comando
2. Divide tareas complejas en pasos
3. Verifica que el Chart of Accounts esté cargado:
   ```
   refrescar chart
   ```

---

## 4. Errores en Transacciones

### ❌ Error: "Cliente no encontrado"

**Síntomas:**
```
❌ Cliente 'XYZ Corp' no encontrado
```

**Solución:**
1. **Verifica el nombre exacto en QuickBooks**
2. Usa fuzzy search:
   ```
   Busca cliente XYZ
   ```
3. Si no existe, créalo en QuickBooks primero

---

### ❌ Error: "Cuenta no encontrada"

**Síntomas:**
```
⚠️ No se encontró cuenta para 'Prepaid'
```

**Solución:**
1. El asistente sugiere alternativas automáticamente
2. Usa el nombre completo: "Prepaid Expenses"
3. O usa el número de cuenta: "1200"
4. Verifica que la cuenta esté activa en QuickBooks

---

### ❌ Error: "Cuenta de categoría incorrecta"

**Síntomas:**
```
⚠️ Advertencia: Estás usando una cuenta de INGRESO en un Bill (debe ser GASTO)
```

**Causa:** Intentas usar cuenta de categoría incorrecta

**Solución:**
- **Bills:** Usa cuentas de categoría GASTO
- **Depósitos origen:** Usa PASIVO (Client Retainers) o ACTIVO (Prepaid)
- **Depósitos destino:** Usa ACTIVO (Checking Account)
- Verifica con: `Busca la cuenta [nombre]`

---

### ❌ Error: "Duplicate Transaction Detected"

**Síntomas:**
```
⚠️ Posible duplicado: mismo cliente, monto y fecha que transacción ID 12345
```

**Causa:** Protección contra duplicados

**Solución:**
1. Verifica si ya creaste esta transacción
2. Si es intencional, cambia la fecha ligeramente
3. O agrega un memo diferente

---

## 5. Problemas con CSV

### ❌ Error: "Columnas faltantes en CSV"

**Síntomas:**
```
❌ Columnas faltantes: ['date', 'memo']
```

**Causa:** CSV no tiene las columnas requeridas

**Solución:**
1. Genera el template:
   ```
   template csv
   ```
2. Usa este formato:
   ```csv
   customer_name,amount,from_account,to_account,date,memo
   ```
3. Todas las columnas son obligatorias

---

### ❌ Error: "CSV mal codificado"

**Síntomas:**
```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**Causa:** Archivo CSV con codificación incorrecta

**Solución:**
1. Abre el CSV en Excel
2. "Guardar como" → UTF-8 CSV
3. O en Google Sheets: Archivo → Descargar → CSV

---

### ❌ Algunos registros del CSV fallan

**Síntomas:**
```
Exitosos: 8/10
Errores:
  • Fila 3: Cliente no encontrado
  • Fila 7: Cuenta no encontrada
```

**Solución:**
1. **Revisa el reporte de errores** - especifica la fila exacta
2. Corrige solo esas filas en el CSV
3. Procesa nuevamente
4. Los registros exitosos no se duplican (ya están creados)

---

## 6. Errores de Chart of Accounts

### ❌ Error: "Chart of Accounts vacío"

**Síntomas:**
```
⚠️ No hay cuentas disponibles en memoria
```

**Causa:** Fallo al cargar Chart of Accounts

**Solución:**
```
refrescar chart
```

Si persiste:
```bash
# Elimina el caché corrupto
rm chart_of_accounts.json

# Reinicia el asistente
python main.py
```

---

### ❌ Error: "Caché desactualizado"

**Síntomas:**
- Cuentas nuevas no aparecen
- Balances incorrectos

**Solución:**
```
refrescar chart
```

El caché se actualiza automáticamente cada 24 horas, pero puedes forzarlo.

---

## 7. Problemas de Performance

### ❌ El asistente es muy lento

**Causas posibles:**
1. Internet lento
2. QuickBooks API lento
3. Muchas cuentas en Chart of Accounts

**Soluciones:**
1. **Verifica velocidad de internet**
2. **Usa caché:** El Chart of Accounts se carga 1 vez al día
3. **Comandos rápidos:** Usa comandos sin LLM cuando sea posible:
   ```
   ¿cuánto he gastado?
   listar reportes
   template csv
   ```

---

### ❌ Consumo alto de tokens

**Síntomas:**
```
Costo de sesión: $0.05 (esperado: $0.01)
```

**Causas:**
- Conversaciones muy largas
- Preguntas repetitivas
- Contexto innecesario

**Soluciones:**
1. **Usa comandos rápidos** (no consumen tokens)
2. **Reinicia sesiones largas**
3. **Sé específico** en tus preguntas
4. **Revisa el informe:**
   ```
   informe de tokens
   ```

---

## 8. Errores Generales

### ❌ Error: "ModuleNotFoundError"

**Síntomas:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Causa:** Dependencias no instaladas

**Solución:**
```bash
pip install -r requirements.txt
```

Verifica que estés en el entorno virtual:
```bash
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate    # Windows
```

---

### ❌ Error: "Permission Denied"

**Síntomas:**
```
PermissionError: [Errno 13] Permission denied: '.env'
```

**Causa:** Problemas de permisos de archivo

**Solución (Linux/Mac):**
```bash
chmod 644 .env
```

**Solución (Windows):**
- Click derecho en `.env` → Propiedades → Desmarcar "Solo lectura"

---

### ❌ Error: "File not found: .env"

**Síntomas:**
```
FileNotFoundError: .env
```

**Causa:** Archivo `.env` no existe

**Solución:**
```bash
cp .env.example .env
# Edita .env con tus credenciales
```

---

## 🧪 Herramienta de Diagnóstico

### Ejecutar Verificación Completa

```bash
python scripts/verify_setup.py
```

**Esta herramienta verifica:**
✅ Dependencias Python instaladas  
✅ Variables de entorno configuradas  
✅ Conexión a QuickBooks Online  
✅ Conexión a OpenRouter  
✅ Chart of Accounts accesible  

**Salida esperada:**
```
================================================================================
🔍 QUICKBOOKS AI ASSISTANT - VERIFICACIÓN DE CONFIGURACIÓN
================================================================================

✅ 1. Dependencias Python
✅ 2. Variables de entorno
✅ 3. Conexión a QuickBooks Online
✅ 4. Conexión a OpenRouter

================================================================================
🎉 ¡CONFIGURACIÓN COMPLETA Y CORRECTA!
================================================================================
```

---

## 🆘 Soporte Adicional

### Si nada funciona:

1. **Revisa los logs:**
   - Los errores se muestran en terminal
   - Copia el error completo

2. **Verifica configuración básica:**
   ```bash
   python scripts/verify_setup.py
   ```

3. **Consulta la documentación:**
   - [QUICKSTART.md](QUICKSTART.md) - Instalación
   - [EXAMPLES.md](EXAMPLES.md) - Ejemplos de uso
   - [CONTEXT.md](CONTEXT.md) - Documentación completa

4. **Reinstala desde cero:**
   ```bash
   # Elimina entorno virtual
   rm -rf .venv

   # Elimina archivos generados
   rm chart_of_accounts.json saved_reports.json

   # Reinstala
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

   # Verifica
   python scripts/verify_setup.py
   ```

---

## 💡 Prevención de Problemas

### Mejores Prácticas:

1. ✅ **Mantén tokens actualizados**
   - Los refresh tokens expiran en 100 días
   - Guarda nuevos tokens cuando se refresquen

2. ✅ **Usa el mismo ambiente**
   - Sandbox para pruebas
   - Producción para operaciones reales
   - No mezcles

3. ✅ **Respalda tu `.env`**
   - Guarda una copia segura
   - No la subas a Git

4. ✅ **Monitorea costos**
   - Usa: `¿cuánto he gastado?`
   - Revisa Excel: `informe de tokens`

5. ✅ **Actualiza Chart of Accounts**
   - Si creas cuentas nuevas en QuickBooks
   - Ejecuta: `refrescar chart`

---

## 📞 FAQs

**P: ¿Cada cuánto debo refrescar los tokens?**  
R: El sistema lo hace automáticamente. Solo hazlo manual si hay error.

**P: ¿Puedo usar el asistente sin internet?**  
R: No. Necesita conexión a QuickBooks y OpenRouter.

**P: ¿Los datos se quedan en memoria?**  
R: No. Cada sesión carga fresh data de QuickBooks.

**P: ¿Qué pasa si cierro el asistente sin "salir"?**  
R: Se guarda el tracking de tokens automáticamente al cerrar.

**P: ¿Puedo recuperar un depósito mal creado?**  
R: Debes eliminarlo desde QuickBooks Online manualmente.

---

## 9. Problemas Multi-Empresa (v3.5)

### ❌ Error: "Empresa no encontrada"

**Síntomas:**
```
❌ Empresa 'Tech Inc' no encontrada. Empresas registradas: Acme Corp, Design Co
```

**Causa:** Intentas cambiar a una empresa no registrada.

**Solución:**
```
👤: "lista las empresas"
🤖: 🏢 Empresas registradas: Acme Corp, Design Co

👤: "registra Tech Inc con realm_id <tu_realm_id>"
```

---

### ❌ Error: "Token inválido al cambiar empresa"

**Síntomas:**
```
❌ 401 Unauthorized al cambiar a Tech Inc
```

**Causa:** El access token de Tech Inc expiró y el refresh falló.

**Solución:**
```bash
# Opción 1: Refrescar manualmente
python scripts/refresh_token.py

# Opción 2: Re-autorizar la app
# Ve a https://developer.intuit.com → tu app → "Keys & OAuth"
# Regenera tokens y actualiza .env
```

---

### ❌ Error: "Chart de cuentas vacío tras cambiar"

**Síntomas:**
```
⚠️ No se encontraron cuentas en la empresa actual
```

**Causa:** El caché de chart está vacío o es de otra empresa.

**Solución:**
```
👤: "refrescar chart"
🤖: 📊 Descargando chart desde QBO... 87 cuentas encontradas ✅
```

---

### ❌ Error: "No puedo registrar nueva empresa"

**Síntomas:**
```
❌ No se puede registrar empresa: realm_id no válido
```

**Solución:**
1. Verifica que el `realm_id` es correcto (en la URL de QBO, después de `/company/`)
2. Verifica que la app está autorizada en esa empresa
3. Si la app no está autorizada, ejecuta `python scripts/refresh_token.py`

---

### ❌ Error: "Cambio de empresa no se refleja"

**Síntomas:** Dices "cambia a Tech Inc" pero las operaciones siguen aplicando a la empresa anterior.

**Causa:** Bug en v3.5 conocido cuando hay concurrencia con operaciones pendientes.

**Solución:**
1. Espera a que terminen las operaciones en curso
2. Vuelve a decir "cambia a Tech Inc"
3. Si persiste, reinicia la app

Ver [`MULTI_EMPRESA.md`](MULTI_EMPRESA.md) para más detalles.

---

<div align="center">

[⬆ Volver arriba](#-quickbooks-ai-assistant---troubleshooting)

</div>
