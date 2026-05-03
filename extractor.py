import anthropic
import base64
import json
import sys
import re
from pathlib import Path

def extraer_datos_ticket(imagen_path: str) -> dict:
    with open(imagen_path, "rb") as f:
        imagen_base64 = base64.standard_b64encode(f.read()).decode("utf-8")
    
    ext = Path(imagen_path).suffix.lower()
    media_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
    media_type = media_types.get(ext, "image/jpeg")
    
    client = anthropic.Anthropic(api_key="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")
    
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
                    "text": """Eres un extractor de datos de tickets de OXXO. 
Extrae exactamente estos datos del ticket y responde SOLO con JSON, sin texto adicional, sin markdown, sin explicaciones:

{"fecha": "DD/MM/YYYY", "folio_venta": "numero despues de Fol_Vta:", "id_venta": "codigo despues de ID=", "total": "monto con 2 decimales sin simbolo de pesos", "tienda": "nombre de la tienda"}"""
                }
            ]
        }]
    )
    
    respuesta = mensaje.content[0].text.strip()
    print(f"Respuesta de Claude: {respuesta}")
    
    # Verificar si Claude no pudo leer el ticket
    if not respuesta or len(respuesta) < 10:
        raise ValueError("❌ No se pudo leer el ticket. Verifica que la imagen sea clara y legible.")
    
    if any(palabra in respuesta.lower() for palabra in ["no puedo", "no es posible", "imagen borrosa", "ilegible", "cannot", "unclear"]):
        raise ValueError("❌ La imagen está borrosa o es ilegible. Toma una foto más clara del ticket.")
    
    # Buscar JSON en la respuesta
    match = re.search(r'\{.*\}', respuesta, re.DOTALL)
    if match:
        datos = json.loads(match.group())
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