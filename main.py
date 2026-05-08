import sys
import asyncio
from extractor import extraer_datos_ticket
from portal import facturar_ticket

async def main(imagen_path: str):
    print("="*50)
    print("SISTEMA DE AUTOFACTURACIÓN UVICUO")
    print("="*50)
    
    MAX_INTENTOS = 3
    
    for intento in range(1, MAX_INTENTOS + 1):
        try:
            print(f"\n📸 Paso 1: Extrayendo datos del ticket (intento {intento})...")
            datos = extraer_datos_ticket(imagen_path, intento)
            print(f"✅ Datos extraídos:")
            print(f"   Fecha:  {datos['fecha']}")
            print(f"   Folio:  {datos['folio_venta']}")
            print(f"   ID:     {datos['id_venta']}")
            print(f"   Total:  ${datos['total']}")
            
            print(f"\n🤖 Paso 2: Automatizando portal de OXXO...")
            resultado = await facturar_ticket(datos)
            
            if resultado == "invalido":
                if intento < MAX_INTENTOS:
                    print(f"\n⚠️ Portal rechazó los datos. Releyendo ticket con más cuidado (intento {intento + 1})...")
                    continue
                else:
                    print(f"\n❌ El portal rechazó los datos después de {MAX_INTENTOS} intentos.")
                    print("Por favor toma una foto más clara del ticket.")
                    break
            elif resultado == "ok":
                print("\n🎉 ¡Proceso completado! Revisa tu correo.")
                break
            else:
                print("\n❌ Error en el proceso. Revisa los mensajes anteriores.")
                break
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: py main.py <ruta_imagen>")
        sys.exit(1)
    
    asyncio.run(main(sys.argv[1]))