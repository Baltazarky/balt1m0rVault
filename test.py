import pandas as pd

url = "https://docs.google.com/spreadsheets/d/1S_2JtZrqDW6q_rXA80jPyGWdotI5ar3o/export?format=csv&gid=1406050365"

try:
    # Le decimos a Pandas que los títulos están en la fila 5 (índice 4)
    df = pd.read_csv(url, header=4)
    
    # Limpiamos los espacios basura ocultos en los nombres de las columnas por las dudas
    df.columns = df.columns.str.strip()
    
    nombre_columna = 'Precio efvo'
    
    # Verificamos si la columna existe y la imprimimos
    if nombre_columna in df.columns:
        precios = df[nombre_columna].dropna()
        
        print(f"--- Lista de {nombre_columna} ---")
        for precio in precios:
            print(precio)
    else:
        print(f"Error: No se encontró la columna '{nombre_columna}'.")
        print("Las columnas que detectó en la fila 5 son:")
        for c in df.columns:
            print(f"'{c}'")

except Exception as e:
    print(f"Error al leer los datos: {e}")