import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Ventas", layout="centered")
st.title("Registro de ventas semanal 💰")

archivo = "ventas.csv"
archivo_inv = "inversores.csv"

# 📅 FECHA Y SEMANA
def obtener_fecha(dia):
    dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]
    hoy = datetime.now()
    return hoy + timedelta(days=dias.index(dia) - hoy.weekday())

def obtener_semana(fecha):
    return fecha.isocalendar()[1]

dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]

# 📥 CARGAR DATOS
if os.path.exists(archivo):
    df = pd.read_csv(archivo)
else:
    df = pd.DataFrame(columns=["id","dia","producto","precio","fecha","semana"])

if os.path.exists(archivo_inv):
    df_inv = pd.read_csv(archivo_inv)
else:
    df_inv = pd.DataFrame(columns=["nombre","monto","ganancia","total"])

# =========================
# 🔘 PESTAÑAS
# =========================
tab1, tab2, tab3 = st.tabs(["📅 Registro", "📚 Historial", "💰 Inversores"])

# =========================
# 📅 REGISTRO
# =========================
with tab1:

    dia = st.selectbox("Selecciona el día", dias)

    fecha_obj = obtener_fecha(dia)
    fecha_actual = fecha_obj.strftime("%d-%m-%Y")
    semana_actual = obtener_semana(fecha_obj)

    st.write("📅 Fecha:", fecha_actual)
    st.write("📆 Semana:", semana_actual)

    with st.form("form"):
        producto = st.text_input("Producto")
        precio = st.number_input("Precio", min_value=0.0)

        if st.form_submit_button("Guardar venta 💾"):
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

    ventas_dia = df[df["dia"] == dia]

    st.subheader(f"Ventas de {dia}")

    if not ventas_dia.empty:
        st.dataframe(ventas_dia[["id","producto","precio","fecha"]])

        total = ventas_dia["precio"].sum()
        st.write(f"💰 Total: {total} Bs")
    else:
        st.info("No hay ventas")

# =========================
# 📚 HISTORIAL
# =========================
with tab2:

    st.subheader("📚 Historial semanal")

    if df.empty:
        st.warning("No hay registros")
    else:
        for s in sorted(df["semana"].unique()):
            st.markdown(f"## 📆 Semana {s}")
            datos = df[df["semana"] == s]

            st.dataframe(datos[["dia","producto","precio","fecha"]])

            total = datos["precio"].sum()
            st.write(f"💰 Total semana: {total} Bs")

# =========================
# 💰 INVERSORES
# =========================
with tab3:

    st.subheader("💰 Registro de inversores")

    with st.form("form_inv"):
        nombre = st.text_input("Nombre del inversor")
        monto = st.number_input("Monto invertido", min_value=0.0)

        if st.form_submit_button("Guardar inversor"):
            if nombre and monto > 0:

                ganancia = monto * 0.20
                total = monto + ganancia

                nuevo = pd.DataFrame([{
                    "nombre": nombre,
                    "monto": monto,
                    "ganancia": ganancia,
                    "total": total
                }])

                df_inv = pd.concat([df_inv, nuevo], ignore_index=True)
                df_inv.to_csv(archivo_inv, index=False)

                st.success("Inversor guardado ✅")
                st.rerun()
            else:
                st.warning("Completa los datos")

    # 📊 MOSTRAR INVERSORES
    if not df_inv.empty:
        st.dataframe(df_inv, use_container_width=True)

        total_invertido = df_inv["monto"].sum()
        total_ganancia = df_inv["ganancia"].sum()

        st.write("💰 Total invertido:", total_invertido)
        st.write("📈 Ganancia total:", total_ganancia)
    else:
        st.info("No hay inversores registrados")

# =========================
# 🧨 BORRAR TODO
# =========================
st.subheader("⚠️ Modo prueba")

if "confirmar_borrado" not in st.session_state:
    st.session_state.confirmar_borrado = False

if not st.session_state.confirmar_borrado:
    if st.button("🗑 Borrar TODOS los registros"):
        st.session_state.confirmar_borrado = True
        st.rerun()

else:
    st.warning("¿Seguro que quieres borrar TODO?")

    if st.button("✅ Sí borrar todo"):
        if os.path.exists(archivo):
            os.remove(archivo)
        if os.path.exists(archivo_inv):
            os.remove(archivo_inv)

        st.success("Todo eliminado")
        st.session_state.confirmar_borrado = False
        st.rerun()

    if st.button("❌ Cancelar"):
        st.session_state.confirmar_borrado = False
        st.rerun()
