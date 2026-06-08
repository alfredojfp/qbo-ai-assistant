# Plan de Soporte — Dexter QBO Agent

**Última actualización:** Junio 2026

---

## Canales de Soporte

| Canal | Tiempo de respuesta | Disponibilidad |
|---|---|---|
| **Email** | < 24h hábiles | Lun-Vie 9:00-18:00 |
| **GitHub Issues** | < 48h | Público (reportes de bugs) |
| **WhatsApp / Telegram** (clientes Pro) | < 4h hábiles | Lun-Vie 9:00-18:00 |
| **Emergencias** (clientes Enterprise) | < 1h | 24/7 |

---

## Niveles de Servicio (SLA)

| Plan | Soporte incluido | Tiempo respuesta | Canal |
|---|---|---|---|
| **Básico** | Comunidad | < 48h | GitHub Issues |
| **Profesional** | Email + Chat | < 24h | Email, WhatsApp |
| **Enterprise** | Prioritario + Emergencias | < 1h | Teléfono, Email, Chat |

---

## Qué Cubre el Soporte

- ✅ Instalación y configuración inicial
- ✅ Errores de conexión con QuickBooks
- ✅ Problemas de autenticación OAuth
- ✅ Errores en procesamiento OCR
- ✅ Dudas sobre uso de herramientas
- ✅ Actualizaciones de seguridad

## Qué NO Cubre el Soporte

- ❌ Configuración de QuickBooks (ajena a Dexter)
- ❌ Problemas de red o hardware del cliente
- ❌ Errores por mal uso de la API de terceros (OpenRouter, Google)
- ❌ Desarrollo de funcionalidades personalizadas (cotizar aparte)
- ❌ Capacitación contable (uso de QuickBooks en sí)

---

## Proceso de Reporte de Bugs

1. El usuario reporta el problema por el canal correspondiente
2. Se asigna prioridad: Critical / High / Medium / Low
3. Se investiga y reproduce en entorno sandbox
4. Se implementa fix con test de regresión
5. Se despliega actualización
6. Se notifica al usuario

---

## Actualizaciones

Las actualizaciones se distribuyen vía el repositorio oficial. Los clientes con licencia activa reciben:

- **Parches de seguridad:** inmediatos
- **Bug fixes:** según prioridad (Critical < 24h, High < 72h, Medium < 1 semana)
- **Nuevas funcionalidades:** trimestrales

---

## Contacto

- **Email:** [tu email]
- **GitHub Issues:** repositorio del proyecto (clientes con acceso)
- **WhatsApp:** [tu número] (clientes Pro y Enterprise)
