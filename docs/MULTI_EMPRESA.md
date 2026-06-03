# 🏢 Gestión Multi-Empresa (v3.5)

Guía específica de la funcionalidad multi-empresa introducida en v3.5. Permite a Dexter gestionar **múltiples empresas de QuickBooks** de forma independiente con tokens aislados y cambio en caliente.

---

## 🎯 ¿Qué es?

Cada empresa de QuickBooks tiene:
- Sus propios tokens de acceso (access + refresh)
- Su propio Chart of Accounts
- Sus propias configuraciones de reportes guardados
- Su propio historial de bank feed
- Su propio `meta.json` de persistencia

**Aislamiento total:** cambiar de empresa es como tener un Dexter diferente para cada una, pero sin reiniciar la aplicación.

---

## 📂 Estructura de archivos

```
Qbo Scripts/
├── .env                              # Solo credenciales de la empresa por defecto
├── companies/                        # 🆕 Carpeta de empresas (creada al registrar)
│   ├── acme_corp/
│   │   ├── meta.json                 # Tokens, realm_id, contexto aislado
│   │   ├── chart_of_accounts.json    # Caché del chart
│   │   ├── saved_reports.json        # Reportes guardados
│   │   └── bank_feed_history.json    # Patrones aprendidos
│   ├── tech_inc/
│   │   ├── meta.json
│   │   ├── chart_of_accounts.json
│   │   └── ...
│   └── design_co/
│       └── ...
├── main.py                           # Lee de companies/<activa>/meta.json
└── company_manager.py                # 🆕 Lógica de gestión
```

---

## 🔄 Flujo de cambio de empresa

```
Usuario: "cambia a Tech Inc"
   │
   ▼
1. main.py detecta intención → invoca gestionar_empresas
   │
   ▼
2. company_manager.guardar_contexto_actual()
   • Guarda session_state en companies/<actual>/meta.json
   • Serializa chart, reportes, bank feed
   │
   ▼
3. company_manager.cargar_empresa("Tech Inc")
   • Lee companies/tech_inc/meta.json
   • Actualiza .env con tokens de Tech Inc
   • Refresca access token si está expirado
   • Recarga chart_of_accounts desde QBO o caché
   │
   ▼
4. main.py continúa conversación con Tech Inc
   • session_state["active_company"] = "Tech Inc"
   • Próximas operaciones aplican a Tech Inc
```

---

## 💻 Comandos del tool `gestionar_empresas`

### Listar empresas

```
👤: "muéstrame las empresas configuradas"
🤖: [gestionar_empresas(action="list")]

   🏢 Empresas registradas (3):
   1. ⭐ Acme Corp (activa)
   2. Tech Inc
   3. Design Co
```

### Cambiar empresa

```
👤: "cambia a Tech Inc"
🤖: [gestionar_empresas(action="select", name="Tech Inc")]

   ✅ Cambiado a Tech Inc
   📊 Chart de cuentas recargado: 87 cuentas
   🔑 Tokens actualizados correctamente
```

### Agregar empresa

```
👤: "registra una nueva empresa llamada Beta LLC"
🤖: [gestionar_empresas(action="add", name="Beta LLC", realm_id="123456789...")]

   🆕 Empresa Beta LLC registrada
   ⚠️ Necesito que autorices el acceso OAuth. Ejecuta: python scripts/refresh_token.py
```

### Eliminar empresa

```
👤: "elimina Design Co"
🤖: [gestionar_empresas(action="remove", name="Design Co")]

   🗑️ Empresa Design Co eliminada
   ⚠️ Los archivos en companies/design_co/ NO se borraron (hazlo manualmente si quieres)
```

---

## 🔐 Seguridad y aislamiento

| Recurso | ¿Aislado por empresa? | ¿Cómo se aísla? |
|---------|----------------------|-----------------|
| Access Token | ✅ Sí | `meta.json` por empresa |
| Refresh Token | ✅ Sí | `meta.json` por empresa |
| Realm ID | ✅ Sí | `meta.json` por empresa |
| Chart of Accounts | ✅ Sí | `chart_of_accounts.json` por empresa |
| Saved Reports | ✅ Sí | `saved_reports.json` por empresa |
| Bank Feed Patterns | ✅ Sí | `bank_feed_history.json` por empresa |
| Token Usage CSV | ⚠️ Compartido | `token_usage.csv` global (no por empresa) |
| User Behavior Patterns | ⚠️ Compartido | Singleton en memoria (v3.5) |

---

## ⚠️ Limitaciones actuales (v3.5)

- **Token usage** se acumula globalmente, no por empresa
- **User Behavior Learning** aún no aísla patrones por empresa (planeado para v3.6)
- **No hay encriptación** de `meta.json` (los tokens están en texto plano)
- **Cambio de empresa** requiere que la app esté autorizada en cada empresa por separado (OAuth por empresa)

---

## 🛠️ Configuración inicial

### Primera vez (una sola empresa)

1. Autoriza la app en QBO siguiendo [`INSTALL.md`](INSTALL.md)
2. Las credenciales se guardan en `.env` por defecto
3. Al primer arranque, `company_manager.py` crea `companies/<nombre>/` y `meta.json`

### Agregar segunda empresa

1. Desde la app QBO de la nueva empresa, autoriza el mismo Client ID
2. Obtén el `realm_id` de la nueva empresa
3. Ejecuta el comando `"registra una nueva empresa llamada <nombre>"` en Dexter
4. Autoriza con `python scripts/refresh_token.py`
5. La nueva empresa queda registrada

### Listo

Ahora puedes alternar entre empresas sin reiniciar.

---

## 📊 Casos de uso

### Caso 1: Contador con múltiples clientes

> "Tengo 12 clientes contables, cada uno con su QBO. Quiero gestionar todos desde un solo Dexter."

**Solución:** Registra cada empresa y cambia con `"cambia a Cliente X"`.

### Caso 2: Empresa con múltiples subsidiarias

> "Mi grupo empresarial tiene 3 subsidiarias, cada una con QBO separado."

**Solución:** Cambia entre subsidiarias para consolidar reportes.

### Caso 3: Sandbox vs Producción

> "Quiero probar cambios en sandbox antes de aplicar a producción."

**Solución:** Registra ambas y cambia con `"cambia a Sandbox"`.

---

## 🐛 Troubleshooting

### "Empresa no encontrada"

Verifica que la empresa está registrada:
```
👤: "lista las empresas"
```

### "Token inválido al cambiar"

```bash
python scripts/refresh_token.py
```

O reinicia la app y vuelve a autorizar.

### "Chart de cuentas vacío"

Fuerza refresh:
```
👤: "refrescar chart"
```

### "No puedo registrar nueva empresa"

Verifica que tienes el `realm_id` correcto y que la app está autorizada en esa empresa.

---

## 🔗 Documentos relacionados

- [ARCHITECTURE.md](ARCHITECTURE.md) — Diagrama de componentes multi-empresa
- [CAPACIDADES.md](CAPACIDADES.md) — Tool `gestionar_empresas` (tool #32)
- [CHANGELOG.md](CHANGELOG.md) — Cambios introducidos en v3.5
