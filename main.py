import sys
import asyncio
from extractor import extraer_datos_ticket
from portal import facturar_ticket

async def main(imagen_path: str):
    print("="*50)
    print("SISTEMA DE AUTOFACTURACIÓN UVICUO")
    print("="*50)
    
    # Paso 1: Extraer datos del ticket
    print("\n📸 Paso 1: Extrayendo datos del ticket...")
    datos = extraer_datos_ticket(imagen_path)
    print(f"✅ Datos extraídos:")
    print(f"   Fecha:  {datos['fecha']}")
    print(f"   Folio:  {datos['folio_venta']}")
    print(f"   ID:     {datos['id_venta']}")
    print(f"   Total:  ${datos['total']}")
    
    # Paso 2: Facturar en el portal
    print("\n🤖 Paso 2: Automatizando portal de OXXO...")
    await facturar_ticket(datos)
    
    print("\n🎉 ¡Proceso completado! Revisa tu correo.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: py main.py <ruta_imagen>")
        sys.exit(1)
    
    asyncio.run(main(sys.argv[1]))