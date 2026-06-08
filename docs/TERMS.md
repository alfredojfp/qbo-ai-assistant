# Términos de Servicio — Dexter QBO Agent

**Última actualización:** Junio 2026

---

## 1. Aceptación de los Términos

Al instalar, acceder o usar Dexter ("el Software"), aceptás estos Términos de Servicio. Si no estás de acuerdo, no uses el Software.

---

## 2. Descripción del Servicio

Dexter es un agente de inteligencia artificial que automatiza tareas contables en QuickBooks Online mediante procesamiento de lenguaje natural. El Software:

- Se ejecuta **localmente** en tu computadora
- Se conecta a QuickBooks Online vía API oficial de Intuit
- Utiliza modelos de lenguaje (LLM) vía OpenRouter
- Utiliza OCR vía Google Gemini para procesar documentos

---

## 3. Licencia de Uso

### 3.1 Uso Personal / Educativo

Se permite el uso gratuito para fines personales, educativos o de evaluación con una (1) empresa en entorno sandbox de QuickBooks.

### 3.2 Uso Comercial

El uso comercial (producción, múltiples empresas, servicios a terceros) requiere una **licencia comercial** otorgada por el Desarrollador. Contactá al Desarrollador para términos y precios.

### 3.3 Restricciones

**No está permitido:**
- Redistribuir, revender o sublicenciar el Software
- Modificar el Software y ofrecerlo como producto propio
- Usar el Software para actividades ilegales o fraudulentas
- Eludir las limitaciones de licencia o los mecanismos de protección
- Extraer, copiar o reutilizar el código fuente sin autorización

---

## 4. Cuentas de Terceros

Para usar Dexter necesitás cuentas en servicios de terceros:

| Servicio | Responsabilidad |
|---|---|
| **Intuit Developer** (QuickBooks API) | Tuya. Dexter no es responsable de las políticas de Intuit ni de cambios en su API. |
| **OpenRouter** (LLM) | Tuya. Los costos de uso del LLM se facturan directamente a tu cuenta de OpenRouter. |
| **Google AI** (Gemini OCR) | Tuya. Opcional. Solo necesario para funcionalidad OCR. |

---

## 5. Limitación de Responsabilidad

**EL SOFTWARE SE PROPORCIONA "TAL CUAL" (AS IS), SIN GARANTÍAS DE NINGÚN TIPO.**

El Desarrollador **no será responsable** por:

- Pérdidas financieras o contables derivadas del uso del Software
- Errores en transacciones creadas por el Software en QuickBooks
- Datos incorrectos extraídos por OCR
- Decisiones contables tomadas basadas en respuestas del LLM
- Interrupciones del servicio por cambios en la API de QuickBooks, OpenRouter o Google
- Pérdida de datos por fallos en tu computadora o instalación
- Problemas derivados del mal uso o configuración incorrecta del Software

**Es tu responsabilidad:**
- Revisar todas las transacciones antes de que se creen en QuickBooks
- Usar el modo simulación (`--dry-run`) para verificar operaciones
- Mantener copias de seguridad de tus datos
- Configurar correctamente las credenciales y APIs
- Cumplir con las leyes y regulaciones contables aplicables

---

## 6. Modo Simulación y Confirmación

Dexter incluye mecanismos de seguridad:

- **Modo Dry-Run (`--dry-run`):** simulá operaciones sin afectar QuickBooks
- **Modo Confirmación:** las operaciones de creación, modificación o eliminación requieren confirmación explícita
- **CSV Preview:** el OCR genera un archivo CSV para tu revisión antes de crear bills

El Desarrollador recomienda usar siempre estos mecanismos en entornos de producción.

---

## 7. Actualizaciones y Soporte

- Las actualizaciones del Software se distribuyen a través del repositorio oficial
- El soporte se proporciona según el plan de licencia adquirido
- El Desarrollador se reserva el derecho de modificar, suspender o discontinuar el Software en cualquier momento

---

## 8. Propiedad Intelectual

Dexter es propiedad intelectual del Desarrollador. Todos los derechos reservados.

- El código fuente es propietario (licencia "All Rights Reserved")
- El nombre "Dexter" y el logo son propiedad del Desarrollador
- Las contribuciones al proyecto (pull requests) se consideran propiedad del Desarrollador al ser aceptadas

---

## 9. Terminación

El Desarrollador puede terminar tu acceso al Software si violás estos términos. Al terminar, debés:
- Dejar de usar el Software
- Eliminar todas las copias del Software en tu posesión
- Las disposiciones de limitación de responsabilidad sobreviven a la terminación

---

## 10. Ley Aplicable

Estos términos se rigen por las leyes del país de residencia del Desarrollador. Cualquier disputa se resolverá mediante negociación de buena fe antes de recurrir a instancias legales.

---

## 11. Contacto

Para licencias comerciales, soporte, o preguntas sobre estos términos:
- Abrí un issue en el repositorio del proyecto
- Contactá al Desarrollador directamente

---

**Al usar Dexter, confirmás que leíste, entendiste y aceptás estos Términos de Servicio.**
