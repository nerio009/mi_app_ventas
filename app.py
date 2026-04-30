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

# 💰 FORMATO
def bs(n):
    if n == int(n):
        return f"{int(n):,} Bs"
    else:
        return f"{n:,.2f} Bs"

dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]

# 📥 DATOS
if os.path.exists(archivo):
    df = pd.read_csv(archivo)
else:
    df = pd.DataFrame(columns=["id","dia","producto","precio","fecha","semana"])

if os.path.exists(archivo_inv):
    df_inv = pd.read_csv(archivo_inv)
else:
    df_inv = pd.DataFrame(columns=["nombre","monto","porcentaje","ganancia","total"])

# 🔘 TABS
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

    with st.form("form", clear_on_submit=True):
        producto = st.text_input("Producto")
        precio_texto = st.text_input("Precio (Bs)")

        if st.form_submit_button("Guardar venta 💾"):
            try:
                precio = float(precio_texto)

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
                else:
                    st.warning("Completa los datos")
            except:
                st.error("Ingresa un número válido")

    ventas_dia = df[df["dia"] == dia]

    st.subheader(f"Ventas de {dia}")

    if not ventas_dia.empty:
        df_mostrar = ventas_dia.copy()
        df_mostrar["precio"] = df_mostrar["precio"].apply(bs)

        st.dataframe(df_mostrar[["id","producto","precio","fecha"]])

        total = ventas_dia["precio"].sum()
        st.write(f"💰 Total: {bs(total)}")
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

            datos = df[df["semana"] == s].copy()
            datos["precio"] = datos["precio"].apply(bs)

            st.dataframe(datos[["dia","producto","precio","fecha"]])

            total = df[df["semana"] == s]["precio"].sum()
            st.write(f"💰 Total semana: {bs(total)}")

# =========================
# 💰 INVERSORES
# =========================
with tab3:

    st.subheader("💰 Registro de inversores")

    with st.form("form_inv", clear_on_submit=True):
        nombre = st.text_input("Nombre del inversor")
        monto_texto = st.text_input("Monto (Bs)")
        porcentaje_texto = st.text_input("Porcentaje (%)", value="20")

        if st.form_submit_button("Guardar inversor"):
            try:
                monto = float(monto_texto)
                porcentaje = float(porcentaje_texto)

                if nombre and monto > 0:
                    ganancia = monto * (porcentaje / 100)
                    total = monto + ganancia

                    nuevo = pd.DataFrame([{
                        "nombre": nombre,
                        "monto": monto,
                        "porcentaje": porcentaje,
                        "ganancia": ganancia,
                        "total": total
                    }])

                    df_inv = pd.concat([df_inv, nuevo], ignore_index=True)
                    df_inv.to_csv(archivo_inv, index=False)

                    st.success("Inversor guardado ✅")
                else:
                    st.warning("Completa los datos")
            except:
                st.error("Datos inválidos")

    # 📊 TABLA BONITA
    if not df_inv.empty:

        df_tabla = df_inv.copy()
        df_tabla["monto"] = df_tabla["monto"].apply(bs)
        df_tabla["ganancia"] = df_tabla["ganancia"].apply(bs)
        df_tabla["total"] = df_tabla["total"].apply(bs)
        df_tabla["porcentaje"] = df_tabla["porcentaje"].astype(str) + "%"

        st.dataframe(df_tabla, use_container_width=True)

        st.subheader("Eliminar inversores")

        for i in range(len(df_inv)):
            if st.button(f"🗑 Eliminar inversor {i}", key=f"del_{i}"):
                df_inv = df_inv.drop(i).reset_index(drop=True)
                df_inv.to_csv(archivo_inv, index=False)

                st.success("Inversor eliminado")
                st.rerun()

    else:
        st.info("No hay inversores registrados")

# =========================
# 🧨 BORRAR TODO
# =========================
st.subheader("⚠️ Modo prueba")

if "confirmar_borrado" not in st.session_state:
    st.session_state.confirmar_borrado = False

if not st.session_state.confirmar_borrado:
    if st.button("🗑 Borrar TODO"):
        st.session_state.confirmar_borrado = True
        st.rerun()
else:
    if st.button("✅ Confirmar borrado"):
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
