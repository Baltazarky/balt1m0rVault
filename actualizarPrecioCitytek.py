import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

# --- 1. CONFIGURACIÓN ---
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1PzQZQOuqMEGyGxS1kJVsc5wzH3b7p4HXpbmYIsncX4Q/edit?gid=872154147#gid=872154147"
NOMBRE_PESTANA = "Lista Precios"
# Ruta de tu archivo en el repositorio (ajustá si está en alguna carpeta)
RUTA_JSON = "precios.json" 

# --- 2. CONEXIÓN CON GOOGLE ---
credenciales_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_json, scope)
cliente = gspread.authorize(creds)

# --- 3. EXTRACCIÓN DE PRECIOS DEL EXCEL ---
planilla = cliente.open_by_url(URL_PLANILLA)
hoja = planilla.worksheet(NOMBRE_PESTANA)

# Leemos desde la fila 5 para saltar el banner
registros_excel = hoja.get_all_records(head=5) 

# Armamos un diccionario temporal solo con Cod y Precios
precios_actualizados = {}
for fila in registros_excel:
    cod = str(fila.get("Cod", "")).strip()
    precio_efvo = str(fila.get("Precio efvo", "")).strip()
    precio_lista = str(fila.get("Precio de lista", "")).strip()
    
    if cod and precio_efvo:
        precios_actualizados[cod] = {
            "efectivo": precio_efvo,
            "lista": precio_lista
        }

# --- 4. ACTUALIZACIÓN DEL JSON EXISTENTE ---
# Abrimos el JSON que ya tenés en tu repositorio
with open(RUTA_JSON, "r", encoding="utf-8") as archivo_lectura:
    base_datos_json = json.load(archivo_lectura)

productos_actualizados = 0

# Recorremos el JSON producto por producto
for id_producto, datos in base_datos_json.items():
    cod_json = datos.get("Cod", "").strip()
    
    # Si el SKU del JSON coincide con alguno del Excel, actualizamos los precios
    if cod_json in precios_actualizados:
        nuevos_datos = precios_actualizados[cod_json]
        
        datos["precioContado"] = nuevos_datos["efectivo"]
        
        # Opcional: actualizamos también el de lista si viene en el excel
        if nuevos_datos["lista"]:
            datos["precioFinanciado_Referencia"] = nuevos_datos["lista"]
            
        productos_actualizados += 1

# --- 5. GUARDAR EL JSON SOBRESCRITO ---
with open(RUTA_JSON, "w", encoding="utf-8") as archivo_escritura:
    json.dump(base_datos_json, archivo_escritura, ensure_ascii=False, indent=2)

print(f"¡Éxito! Se actualizaron los precios de {productos_actualizados} productos en el JSON.")