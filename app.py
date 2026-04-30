import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Ventas", layout="centered")
st.title("Registro de ventas semanal 💰")

archivo = "ventas.csv"

# 📅 FUNCIÓN FECHA + SEMANA
def obtener_fecha(dia):
    dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]
    hoy = datetime.now()
    fecha = hoy + timedelta(days=dias.index(dia) - hoy.weekday())
    return fecha

def obtener_semana(fecha):
    return fecha.isocalendar()[1]

dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]

# 📌 SELECCIÓN
dia = st.selectbox("Selecciona el día", dias)
fecha_obj = obtener_fecha(dia)
fecha_actual = fecha_obj.strftime("%d-%m-%Y")
semana_actual = obtener_semana(fecha_obj)

st.write("📅 Fecha:", fecha_actual)
st.write("📆 Semana:", semana_actual)

# 📥 CARGAR DATOS
if os.path.exists(archivo):
    df = pd.read_csv(archivo)
else:
    df = pd.DataFrame(columns=["id","dia","producto","precio","fecha","semana"])

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
                "fecha": fecha_actual,
                "semana": semana_actual
            }])

            df = pd.concat([df, nueva], ignore_index=True)
            df.to_csv(archivo, index=False)

            st.success("Venta guardada ✅")
            st.rerun()
        else:
            st.warning("Completa los datos")

# 📊 MOSTRAR VENTAS DEL DÍA
ventas_dia = df[df["dia"] == dia]

st.subheader(f"Ventas de {dia}")

if not ventas_dia.empty:
    st.dataframe(ventas_dia[["id","producto","precio","fecha"]], use_container_width=True)

    total = ventas_dia["precio"].sum()
    st.write(f"💰 Total del día: {total} Bs")
else:
    st.info("No hay ventas")

# =========================
# 📚 HISTORIAL SEMANAL
# =========================

st.subheader("📚 Historial")

if st.button("Ver historial semanal"):
    
    if df.empty:
        st.warning("No hay datos")
    else:
        semanas = df["semana"].unique()

        for s in sorted(semanas):
            st.markdown(f"### 📆 Semana {s}")

            datos_semana = df[df["semana"] == s]

            st.dataframe(
                datos_semana[["dia","producto","precio","fecha"]],
                use_container_width=True
            )

            total_semana = datos_semana["precio"].sum()
            st.write(f"💰 Total semana {s}: {total_semana} Bs")

# 📊 RESUMEN GENERAL
st.subheader("📊 Resumen general")

total_general = df["precio"].sum() if not df.empty else 0
st.write("💰 Total general:", total_general)
