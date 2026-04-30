import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Ventas", layout="centered")
st.title("Registro de ventas suni 💰")

archivo = "ventas.csv"

# 📅 FECHA Y SEMANA
def obtener_fecha(dia):
    dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]
    hoy = datetime.now()
    return hoy + timedelta(days=dias.index(dia) - hoy.weekday())

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

# =========================
# 📊 VENTAS DEL DÍA
# =========================
ventas_dia = df[df["dia"] == dia]

st.subheader(f"Ventas de {dia}")

if not ventas_dia.empty:

    st.dataframe(
        ventas_dia[["id","producto","precio","fecha"]],
        use_container_width=True
    )

    st.subheader("🧾 Detalle")

    total_dia = 0

    for _, v in ventas_dia.iterrows():
        st.markdown(f"**🛒 {v['producto']}** — {v['precio']} Bs")
        total_dia += v["precio"]

    st.write(f"💰 Total del día: {total_dia} Bs")

else:
    st.info("No hay ventas registradas")

# =========================
# 📚 HISTORIAL (TOGGLE)
# =========================
st.subheader("📚 Historial")

if "mostrar_historial" not in st.session_state:
    st.session_state.mostrar_historial = False

# Texto dinámico del botón
texto_boton = "📖 Ocultar historial" if st.session_state.mostrar_historial else "📖 Ver historial semanal"

if st.button(texto_boton):
    st.session_state.mostrar_historial = not st.session_state.mostrar_historial

if st.session_state.mostrar_historial:

    if df.empty:
        st.warning("No hay registros")
    else:
        semanas = sorted(df["semana"].unique())

        for s in semanas:
            st.markdown(f"## 📆 Semana {s}")

            datos_semana = df[df["semana"] == s]

            st.dataframe(
                datos_semana[["dia","producto","precio","fecha"]],
                use_container_width=True
            )

            total_semana = datos_semana["precio"].sum()
            st.write(f"💰 Total semana {s}: {total_semana} Bs")

# =========================
# 📊 RESUMEN GENERAL
# =========================
st.subheader("📊 Resumen general")

total_general = df["precio"].sum() if not df.empty else 0
cantidad_total = len(df)

st.write("💰 Total vendido:", total_general)
st.write("📦 Total ventas:", cantidad_total)

# =========================
# 🧨 BORRAR TODO (CONFIRMACIÓN)
# =========================
st.subheader("⚠️ Modo prueba")

if "confirmar_borrado" not in st.session_state:
    st.session_state.confirmar_borrado = False

if not st.session_state.confirmar_borrado:
    if st.button("🗑 Borrar TODOS los registros"):
        st.session_state.confirmar_borrado = True
        st.rerun()

else:
    st.warning("¿Seguro que quieres borrar TODOS los registros?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Sí, borrar todo"):
            if os.path.exists(archivo):
                os.remove(archivo)

            st.success("Todos los datos fueron eliminados")
            st.session_state.confirmar_borrado = False
            st.rerun()

    with col2:
        if st.button("❌ No, cancelar"):
            st.session_state.confirmar_borrado = False
            st.rerun()
