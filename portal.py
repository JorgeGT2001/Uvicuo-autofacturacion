import asyncio
from playwright.async_api import async_playwright

DATOS_FISCALES = {
    "rfc": "AUV230428ST1",
    "razon_social": "AUTO UVICUO",
    "codigo_postal": "05348",
    "estado": "CIUDAD DE MEXICO",
    "regimen_fiscal": "General de Ley Personas Morales",
    "uso_cfdi": "G03"
}

async def facturar_ticket(datos_ticket: dict):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        page = await browser.new_page(viewport=None)
        
        try:
            print("Abriendo portal de OXXO...")
            await page.goto("https://www4.oxxo.com:9443/facturacionElectronica-web/views/layout/inicio.do", timeout=30000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(5000)
            
            print("Cerrando popup...")
            await page.evaluate("""
                Array.from(document.querySelectorAll('.ui-dialog-titlebar-close'))
                    .find(el => el.getBoundingClientRect().top > 0 && el.getBoundingClientRect().top < 500)
                    .click()
            """)
            await page.wait_for_timeout(2000)
            print("Popup cerrado.")
            
            print("Llenando fecha...")
            await page.evaluate(f"""
                var input = document.querySelector('input[name="form:fecha_input"]');
                input.value = '{datos_ticket["fecha"]}';
                input.dispatchEvent(new Event('change', {{bubbles: true}}));
                input.dispatchEvent(new Event('blur', {{bubbles: true}}));
            """)
            await page.wait_for_timeout(500)
            
            print("Llenando folio...")
            await page.locator('input[name="form:folio"]').click()
            await page.locator('input[name="form:folio"]').fill(datos_ticket["folio_venta"])
            await page.wait_for_timeout(500)
            
            print("Llenando ID...")
            await page.locator('input[name="form:venta"]').click()
            await page.locator('input[name="form:venta"]').fill(datos_ticket["id_venta"])
            await page.wait_for_timeout(500)
            
            print("Llenando total...")
            await page.locator('input[name="form:total"]').click()
            await page.locator('input[name="form:total"]').fill(datos_ticket["total"])
            await page.wait_for_timeout(500)
            
            print("Validando ticket...")
            await page.evaluate("""
                Array.from(document.querySelectorAll('a, button'))
                    .find(el => el.textContent.includes('Validar Ticket'))
                    .click()
            """)
            await page.wait_for_timeout(4000)
            
            # Verificar si el ticket es válido
            contenido = await page.content()
            if "inválido" in contenido or "invalido" in contenido.lower():
                raise Exception("❌ El ticket es inválido. Verifica los datos.")
            if "ya fue facturado" in contenido.lower() or "facturado previamente" in contenido.lower():
                raise Exception("❌ Este ticket ya fue facturado anteriormente.")
            if "no han transcurrido" in contenido.lower() or "24 horas" in contenido.lower():
                raise Exception("❌ Debes esperar 24 horas después de la compra para facturar.")
            
            print("Continuando a datos fiscales...")
            await page.evaluate("""
                Array.from(document.querySelectorAll('a, button, input[type=button]'))
                    .find(el => el.textContent.includes('Continuar'))
                    .click()
            """)
            await page.wait_for_timeout(2000)
            
            print("Llenando RFC...")
            await page.locator('input[name="form:rfc"]').fill(DATOS_FISCALES["rfc"])
            await page.wait_for_timeout(500)
            
            print("Llenando razón social...")
            await page.locator('input[name="form:razon"]').fill(DATOS_FISCALES["razon_social"])
            await page.wait_for_timeout(500)
            
            print("Llenando código postal...")
            await page.locator('input[name="form:codigo"]').fill(DATOS_FISCALES["codigo_postal"])
            await page.wait_for_timeout(500)
            
            print("Seleccionando estado...")
            await page.evaluate("""
                document.querySelector('#form\\\\:estado .ui-selectonemenu-trigger').click()
            """)
            await page.wait_for_timeout(1000)
            await page.evaluate(f"""
                Array.from(document.querySelectorAll('#form\\\\:estado_panel .ui-selectonemenu-item'))
                    .find(el => el.textContent.includes('{DATOS_FISCALES["estado"]}'))
                    .click()
            """)
            await page.wait_for_timeout(500)
            
            print("Seleccionando régimen fiscal...")
            await page.evaluate("""
                document.querySelector('#form\\\\:selectOneMenuRegFis .ui-selectonemenu-trigger').click()
            """)
            await page.wait_for_timeout(1000)
            await page.evaluate(f"""
                Array.from(document.querySelectorAll('#form\\\\:selectOneMenuRegFis_panel .ui-selectonemenu-item'))
                    .find(el => el.textContent.includes('{DATOS_FISCALES["regimen_fiscal"]}'))
                    .click()
            """)
            await page.wait_for_timeout(500)
            
            print("Seleccionando uso CFDI...")
            await page.evaluate("""
                document.querySelector('#form\\\\:selectOneMenuCFDI .ui-selectonemenu-trigger').click()
            """)
            await page.wait_for_timeout(1000)
            await page.evaluate("""
                document.querySelectorAll('#form\\\\:selectOneMenuCFDI_panel .ui-selectonemenu-item')[8].click()
            """)
            await page.wait_for_timeout(500)
            
            await page.screenshot(path="paso3_fiscal.png")
            print("Screenshot: paso3_fiscal.png")
            
            print("Generando factura...")
            await page.evaluate("""
                Array.from(document.querySelectorAll('a, button, input[type=button]'))
                    .find(el => el.textContent.includes('Generar Factura'))
                    .click()
            """)
            await page.wait_for_timeout(5000)
            
            print("Ingresando correo...")
            await page.locator('input[name="form:emailEnv"]').fill("jorgegarciatapia@live.com")
            await page.wait_for_timeout(500)
            
            print("Enviando correo...")
            await page.evaluate("""
                Array.from(document.querySelectorAll('a, button'))
                    .find(el => el.textContent.includes('Enviar correo'))
                    .click()
            """)
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path="paso4_enviado.png")
            print("✅ Factura enviada a jorgegarciatapia@live.com")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await page.screenshot(path="error.png")
            print("Screenshot del error guardado: error.png")
        
        finally:
            input("Presiona Enter para cerrar el navegador...")
            await browser.close()

if __name__ == "__main__":
    datos = {
        "fecha": "03/05/2026",
        "folio_venta": "878765",
        "id_venta": "10GUD508DZ1",
        "total": "42.00"
    }
    
    asyncio.run(facturar_ticket(datos))