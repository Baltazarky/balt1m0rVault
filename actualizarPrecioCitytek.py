import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

# --- 1. CONFIGURACIÓN ---
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1PzQZQOuqMEGyGxS1kJVsc5wzH3b7p4HXpbmYIsncX4Q/edit?gid=872154147#gid=872154147"
NOMBRE_PESTANA = "Lista Precios"
# Ahora sí, en la raíz del repo
RUTA_JSON = "precios.json" 

# --- 2. CONEXIÓN CON GOOGLE ---
try:
    credenciales_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_json, scope)
    cliente = gspread.authorize(creds)
    print("✅ Conexión con Google Sheets exitosa.")
except Exception as e:
    print(f"❌ ERROR CONECTANDO A GOOGLE: {e}")
    exit(1)

# --- 3. EXTRACCIÓN DE PRECIOS DEL EXCEL ---
print("\n--- LEYENDO EXCEL ---")
planilla = cliente.open_by_url(URL_PLANILLA)
hoja = planilla.worksheet(NOMBRE_PESTANA)

# Leemos desde la fila 5 para saltar el banner
registros_excel = hoja.get_all_records(head=5) 
print(f"📊 Se leyeron {len(registros_excel)} filas del Excel (después del banner).")

precios_actualizados = {}
for fila in registros_excel:
    cod = str(fila.get("Cod", "")).strip().upper() 
    precio_efvo = str(fila.get("Precio efvo", "")).strip()
    precio_lista = str(fila.get("Precio de lista", "")).strip()
    
    if cod and precio_efvo:
        precios_actualizados[cod] = {
            "efectivo": precio_efvo,
            "lista": precio_lista
        }

print(f"✅ Se guardaron {len(precios_actualizados)} SKUs válidos en memoria.")
if "PS5-BLUE" in precios_actualizados:
    print(f"🎯 DEBUG: Encontré PS5-BLUE en el Excel. Precio efvo: {precios_actualizados['PS5-BLUE']['efectivo']}")
else:
    print(f"⚠️ DEBUG: ¡ATENCIÓN! No encontré PS5-BLUE en la columna 'Cod' del Excel.")

# --- 4. ACTUALIZACIÓN DEL JSON EXISTENTE ---
print(f"\n--- LEYENDO JSON LOCAL: {RUTA_JSON} ---")
try:
    with open(RUTA_JSON, "r", encoding="utf-8") as archivo_lectura:
        base_datos_json = json.load(archivo_lectura)
    print(f"✅ JSON abierto. Contiene {len(base_datos_json)} productos (IDs de Tiendanube).")
except Exception as e:
    print(f"❌ ERROR AL ABRIR EL JSON LOCAL: {e}")
    exit(1)

productos_actualizados = 0

print("\n--- CRUZANDO DATOS (JSON vs EXCEL) ---")
for id_producto, datos in base_datos_json.items():
    cod_json = str(datos.get("Cod", "")).strip().upper()
    
    if not cod_json:
        print(f"  -> ⏭️ IGNORADO: El producto '{datos.get('nombre', id_producto)}' no tiene 'Cod' en el JSON.")
        continue
        
    if cod_json in precios_actualizados:
        nuevos_datos = precios_actualizados[cod_json]
        precio_viejo = datos.get("precioContado", "")
        precio_nuevo = nuevos_datos["efectivo"]
        
        if precio_viejo != precio_nuevo:
            print(f"  -> 💰 ACTUALIZANDO [{cod_json}]: {precio_viejo} PASA A {precio_nuevo}")
            datos["precioContado"] = precio_nuevo
            
            if nuevos_datos["lista"]:
                datos["precioFinanciado_Referencia"] = nuevos_datos["lista"]
            
            productos_actualizados += 1
        else:
            print(f"  -> ➖ SIN CAMBIOS para [{cod_json}]: Ya tiene el precio {precio_viejo}")
    else:
        print(f"  -> ⚠️ NO ENCONTRADO EN EXCEL: El SKU '[{cod_json}]' está en el JSON pero no en la planilla.")

# --- 5. GUARDAR EL JSON SOBRESCRITO ---
print(f"\n--- GUARDANDO CAMBIOS ---")
with open(RUTA_JSON, "w", encoding="utf-8") as archivo_escritura:
    json.dump(base_datos_json, archivo_escritura, ensure_ascii=False, indent=2)

print(f"🎉 ¡PROCESO TERMINADO! Se modificaron {productos_actualizados} productos en el JSON.")