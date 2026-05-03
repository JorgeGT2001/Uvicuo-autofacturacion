\# Sistema de Autofacturación OXXO — Uvicuo



\## Qué hace este sistema

Automatiza la generación de CFDIs a partir de una foto de ticket de OXXO.

El empleado solo toma la foto — el sistema extrae los datos, entra al portal de OXXO y genera la factura automáticamente.



\## Flujo

1\. Foto del ticket entra al sistema

2\. Claude Vision extrae los datos (fecha, folio, ID, total)

3\. Playwright automatiza el portal de OXXO

4\. CFDI enviado al correo del cliente



\## Cómo correr el sistema



Instalar dependencias:

&#x20;   py -m pip install anthropic playwright pillow requests

&#x20;   py -m playwright install chromium



Correr el sistema:

&#x20;   py main.py ticket3.jpeg



\## Archivos

\- main.py — Orquestador principal

\- extractor.py — Extrae datos del ticket con Claude Vision

\- portal.py — Automatiza el portal de OXXO



\## Decisiones de diseño

\- Python + Playwright: más robusto para portales complejos con JavaScript como el de OXXO

\- Claude Vision: interpreta tickets con diferentes formatos y calidad de foto mejor que OCR tradicional

\- Manejo de errores: ticket inválido, ya facturado, menos de 24 horas, portal caído



\## Qué haría diferente con más tiempo

\- Bot de WhatsApp para que el empleado mande la foto directo desde su celular

\- Base de datos para trackear tickets ya facturados

\- Soporte para otros portales (7-Eleven, Walmart, etc.)

\- Dashboard para monitorear el estado de cada factura

