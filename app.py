import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Ventas", layout="centered")
st.title("Registro de ventas semanal 💰")

archivo = "ventas.csv"

# 📅 FUNCIÓN FECHA
def obtener_fecha(dia):
    dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]
    hoy = datetime.now()
    return (hoy + timedelta(days=dias.index(dia) - hoy.weekday())).strftime("%d-%m-%Y")

dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]

# 📌 SELECCIÓN
dia = st.selectbox("Selecciona el día", dias)
fecha_actual = obtener_fecha(dia)
st.write("📅 Fecha:", fecha_actual)

# 📥 CARGAR DATOS
if os.path.exists(archivo):
    df = pd.read_csv(archivo)
else:
    df = pd.DataFrame(columns=["id","dia","producto","precio","fecha"])

# 🧾 FORMULARIO
with st.form("form", clear_on_submit=True):
    producto = st.text_input("Producto")
    precio = st.number_input("Precio", min_value=0.0)

    guardar = st.form_submit_button("Guardar venta 💾")

    if guardar:
        if producto and precio > 0:
            nueva = pd.DataFrame([{
                "id": len(df) + 1,
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
    st.dataframe(ventas_dia, use_container_width=True)

    total = ventas_dia["precio"].sum()
    st.write(f"💰 Total: {total} Bs")

    # ❌ ELIMINAR VENTA
    st.subheader("Eliminar venta")

    id_eliminar = st.number_input("ID a eliminar", min_value=1, step=1)

    if st.button("Eliminar"):
        df = df[df["id"] != id_eliminar]
        df.to_csv(archivo, index=False)
        st.success("Venta eliminada")
        st.rerun()

else:
    st.info("No hay ventas")

# 📊 RESUMEN SEMANAL
st.subheader("📊 Resumen semanal")

total_semana = df["precio"].sum() if not df.empty else 0
cantidad = len(df)

st.write("🧾 Total vendido:", total_semana)
st.write("📦 Total ventas:", cantidad)

# 💸 GANANCIA
inversion = st.number_input("💸 Inversión semanal", min_value=0.0)
ganancia = total_semana - inversion

st.write("💵 Ganancia:", ganancia)

if ganancia > 0:
    st.success("Ganancia 💰")
elif ganancia == 0:
    st.info("Empate 🤝")
else:
    st.error("Pérdida ❌")
