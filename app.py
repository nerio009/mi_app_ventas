import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Ventas", layout="centered")
st.title("Registro de ventas semanal 💰")

archivo = "ventas.csv"

# 📅 FUNCIÓN FECHA
def obtener_fecha(dia):
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    
    hoy = datetime.now()
    indice_hoy = hoy.weekday()
    indice_dia = dias.index(dia)
    
    diferencia = indice_dia - indice_hoy
    fecha = hoy + timedelta(days=diferencia)
    
    return fecha.strftime("%d-%m-%Y")

dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

# 📌 SELECCIÓN
dia = st.selectbox("Selecciona el día", dias)
fecha_actual = obtener_fecha(dia)

st.write("📅 Fecha:", fecha_actual)

# 📥 LEER ARCHIVO
if os.path.exists(archivo):
    df = pd.read_csv(archivo)
else:
    df = pd.DataFrame(columns=["dia", "producto", "precio", "fecha"])

# 🧾 FORMULARIO
with st.form("form"):
    producto = st.text_input("Producto")
    precio = st.number_input("Precio", min_value=0.0)
    
    guardar = st.form_submit_button("Guardar venta 💾")

    if guardar:
        if producto and precio > 0:
            nueva = pd.DataFrame([{
                "dia": dia,
                "producto": producto,
                "precio": precio,
                "fecha": fecha_actual
            }])

            df = pd.concat([df, nueva], ignore_index=True)
            df.to_csv(archivo, index=False)

            st.success("Venta guardada ✅")
            st.rerun()
        else:
            st.warning("Completa los datos")

# 📊 FILTRAR
ventas_dia = df[df["dia"] == dia]

st.subheader(f"Ventas de {dia}")

if not ventas_dia.empty:
    st.dataframe(ventas_dia)

    total = ventas_dia["precio"].sum()
    st.write(f"💰 Total: {total} Bs")
else:
    st.info("No hay ventas")
