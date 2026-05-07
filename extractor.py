import anthropic
import base64
import json
import sys
import re
from pathlib import Path

PROMPT_INTENTO_1 = """Eres un extractor de datos de tickets de OXXO. Lee la imagen y responde SOLO con JSON.

ESTRUCTURA EXACTA DE CADA CAMPO:
- fecha: formato DD/MM/YYYY exacto
- folio_venta: solo números después de "Fol_Vta:" o "Fol Vta:"
- id_venta: código después de "ID=" — SIEMPRE tiene esta estructura: 10 + 3 LETRAS MAYÚSCULAS + 3 NÚMEROS + 2 LETRAS MAYÚSCULAS + 1 NÚMERO. Ejemplo: 10GUD508DZ1. Cuidado: no confundas 0 con O, ni 1 con I, ni G con 6, ni Z con 2
- total: número con 2 decimales sin símbolo $ (ejemplo: 42.00)
- tienda: nombre de la tienda en el encabezado

Responde ÚNICAMENTE con este JSON sin texto adicional:
{"fecha": "DD/MM/YYYY", "folio_venta": "123456", "id_venta": "10XXX000XX0", "total": "00.00", "tienda": "NOMBRE"}"""

PROMPT_INTENTO_2 = """El sistema intentó facturar con tus datos anteriores pero el portal de OXXO los rechazó.

Lee el ticket NUEVAMENTE con máxima atención. El error probablemente está en el ID de venta.

REGLAS ESTRICTAS PARA EL ID DE VENTA:
- Empieza SIEMPRE con el número 1 y el número 0: "10"
- Posiciones 3-5: TRES LETRAS MAYÚSCULAS (A-Z) — no números
- Posiciones 6-8: TRES NÚMEROS (0-9) — no letras
- Posiciones 9-10: DOS LETRAS MAYÚSCULAS (A-Z) — no números  
- Posición 11: UN NÚMERO (0-9)
- Confusiones comunes: O vs 0, I vs 1, Z vs 2, G vs 6, S vs 5

También verifica:
- Folio: solo los números después de Fol_Vta:
- Total: exactamente como aparece en el ticket incluyendo centavos

Responde ÚNICAMENTE con JSON:
{"fecha": "DD/MM/YYYY", "folio_venta": "123456", "id_venta": "10XXX000XX0", "total": "00.00", "tienda": "NOMBRE"}"""

PROMPT_INTENTO_3 = """TERCER INTENTO. El portal sigue rechazando los datos.

Analiza el ticket caracter por caracter. Busca específicamente:

1. La línea que contiene "ID=" — copia exactamente los 11 caracteres después del signo igual
2. La línea que contiene "Fol_Vta:" o "Fol Vta:" — copia solo los números
3. La fecha al inicio del ticket — formato DD/MM/YYYY
4. El Total — busca "Total: $" y copia el número exacto

Para el ID recuerda:
- Caracter 1: siempre "1"
- Caracter 2: siempre "0"  
- Caracteres 3,4,5: letras (si ves algo que parece número pero está en posición de letra, es letra)
- Caracteres 6,7,8: números (si ves algo que parece letra pero está en posición de número, es número)
- Caracteres 9,10: letras
- Caracter 11: número

Responde ÚNICAMENTE con JSON:
{"fecha": "DD/MM/YYYY", "folio_venta": "123456", "id_venta": "10XXX000XX0", "total": "00.00", "tienda": "NOMBRE"}"""

def validar_y_limpiar_datos(datos: dict) -> dict:
    errores = []
    
    # Validar fecha
    fecha = datos.get("fecha", "")
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', fecha):
        errores.append(f"⚠️ Fecha con formato sospechoso: {fecha}")
    
    # Validar y limpiar total
    total = datos.get("total", "")
    total_limpio = re.sub(r'[^\d.]', '', total)
    if total_limpio != total:
        print(f"⚠️ Total limpiado: '{total}' → '{total_limpio}'")
        datos["total"] = total_limpio
    if not re.match(r'^\d+\.\d{2}$', total_limpio):
        errores.append(f"⚠️ Total con formato sospechoso: {total_limpio}")
    
    # Validar folio
    folio = datos.get("folio_venta", "")
    folio_limpio = re.sub(r'[^\d]', '', folio)
    if folio_limpio != folio:
        print(f"⚠️ Folio limpiado: '{folio}' → '{folio_limpio}'")
        datos["folio_venta"] = folio_limpio
    if not folio_limpio.isdigit():
        errores.append(f"⚠️ Folio con formato sospechoso: {folio_limpio}")
    
    # Validar ID de venta
    id_venta = datos.get("id_venta", "")
    if not re.match(r'^10[A-Z]{3}[0-9]{3}[A-Z]{2}[0-9]{1}$', id_venta):
        errores.append(f"⚠️ ID de venta con formato sospechoso: {id_venta}")
    
    for error in errores:
        print(error)
    
    return datos

def extraer_datos_ticket(imagen_path: str, intento: int = 1) -> dict:
    with open(imagen_path, "rb") as f:
        imagen_base64 = base64.standard_b64encode(f.read()).decode("utf-8")
    
    ext = Path(imagen_path).suffix.lower()
    media_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
    media_type = media_types.get(ext, "image/jpeg")
    
    client = anthropic.Anthropic(api_key="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")
    
    prompts = {1: PROMPT_INTENTO_1, 2: PROMPT_INTENTO_2, 3: PROMPT_INTENTO_3}
    instruccion = prompts.get(intento, PROMPT_INTENTO_3)
    
    mensaje = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": imagen_base64
                    }
                },
                {
                    "type": "text",
                    "text": instruccion
                }
            ]
        }]
    )
    
    respuesta = mensaje.content[0].text.strip()
    print(f"Respuesta de Claude (intento {intento}): {respuesta}")
    
    if not respuesta or len(respuesta) < 10:
        raise ValueError("❌ No se pudo leer el ticket. Verifica que la imagen sea clara y legible.")
    
    if any(palabra in respuesta.lower() for palabra in ["no puedo", "no es posible", "ilegible", "cannot", "unclear"]):
        raise ValueError("❌ La imagen está borrosa o es ilegible. Toma una foto más clara del ticket.")
    
    match = re.search(r'\{.*\}', respuesta, re.DOTALL)
    if match:
        datos = json.loads(match.group())
        datos = validar_y_limpiar_datos(datos)
        return datos
    else:
        raise ValueError(f"No se encontró JSON en la respuesta: {respuesta}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: py extractor.py <ruta_imagen>")
        sys.exit(1)
    
    imagen = sys.argv[1]
    print(f"Procesando imagen: {imagen}")
    
    datos = extraer_datos_ticket(imagen)
    print("\n✅ Datos extraídos:")
    print(json.dumps(datos, indent=2, ensure_ascii=False))