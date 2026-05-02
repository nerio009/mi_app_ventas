import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 🔗 GOOGLE SHEETS
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔗 CONEXIÓN GOOGLE SHEETS
try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credenciales.json", scope
    )

    client = gspread.authorize(creds)
    sheet = client.open("ventas_app").sheet1

except:
    sheet = None

# =========================

st.set_page_config(page_title="Ventas", layout="centered")
st.title("Registro de ventas semanal 💰")

archivo_inv = "inversores.csv"

# 📅 FUNCIONES
def obtener_fecha(dia):
    dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]
    hoy = datetime.now()
    return hoy + timedelta(days=dias.index(dia) - hoy.weekday())

def obtener_semana(fecha):
    return fecha.isocalendar()[1]

def bs(n):
    return f"{int(n):,} Bs" if n == int(n) else f"{n:,.2f} Bs"

def estado_icono(pago):
    return "✅" if pago == "Cancelado" else "❌"

dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]

# =========================
# 📥 DATOS DESDE SHEETS
# =========================
if sheet:
    datos = sheet.get_all_records()
    df = pd.DataFrame(datos)

    if df.empty:
        df = pd.DataFrame(columns=[
            "id","dia","producto","precio","cliente","lugar","pago","fecha","semana"
        ])
else:
    df = pd.DataFrame(columns=[
        "id","dia","producto","precio","cliente","lugar","pago","fecha","semana"
    ])

# =========================
# 📂 MENU
# =========================
menu = st.sidebar.radio(
    "📂 Navegación",
    ["📅 Registro", "📚 Historial", "🧾 Pendientes", "💰 Inversores"]
)

# =========================
# 📅 REGISTRO
# =========================
if menu == "📅 Registro":

    dia = st.selectbox("Selecciona el día", dias, index=datetime.now().weekday())

    fecha_obj = obtener_fecha(dia)
    fecha_actual = fecha_obj.strftime("%d-%m-%Y")
    semana_actual = obtener_semana(fecha_obj)

    st.write("📅 Fecha:", fecha_actual)
    st.write("📆 Semana:", semana_actual)

    with st.form("form", clear_on_submit=True):
        producto = st.text_input("Producto")
        precio_texto = st.text_input("Precio (Bs)")
        cliente = st.text_input("Nombre del cliente")
        lugar = st.text_input("Lugar de entrega")
        pago = st.selectbox("Estado de pago", ["Pendiente", "Cancelado"])

        if st.form_submit_button("Guardar venta 💾"):
            try:
                precio = float(precio_texto)

                if producto and precio > 0:
                    nuevo_id = (df["id"].max() + 1) if not df.empty else 1

                    if sheet:
                        sheet.append_row([
                            int(nuevo_id),
                            dia,
                            producto,
                            float(precio),
                            cliente,
                            lugar,
                            pago,
                            fecha_actual,
                            int(semana_actual)
                        ])

                    st.success("Venta guardada ✅")
                    st.rerun()

                else:
                    st.warning("Completa los datos")
            except:
                st.error("Número inválido")

    ventas_dia = df[df["dia"] == dia]

    if not ventas_dia.empty:
        df_mostrar = ventas_dia.copy()
        df_mostrar["precio"] = df_mostrar["precio"].apply(bs)
        df_mostrar["estado"] = df_mostrar["pago"].apply(estado_icono)

        st.dataframe(df_mostrar[
            ["estado","producto","precio","cliente","lugar","pago","fecha"]
        ])

        total = ventas_dia["precio"].sum()
        cantidad = len(ventas_dia)

        st.write(f"💰 Total vendido: {bs(total)}")
        st.write(f"📦 Cantidad de ventas: {cantidad}")

# =========================
# 📚 HISTORIAL
# =========================
elif menu == "📚 Historial":

    if not df.empty:
        total_general = df["precio"].sum()
        cantidad_general = len(df)

        total_cancelado = df[df["pago"] == "Cancelado"]["precio"].sum()
        cantidad_cancelado = len(df[df["pago"] == "Cancelado"])

        total_pendiente = df[df["pago"] == "Pendiente"]["precio"].sum()
        cantidad_pendiente = len(df[df["pago"] == "Pendiente"])

        st.markdown("## 📊 Resumen general")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("### 💰 Todas las ventas")
            st.write(f"Total: {bs(total_general)}")
            st.write(f"Cantidad: {cantidad_general}")

        with col2:
            st.write("### ✅ Cancelados")
            st.write(f"Total: {bs(total_cancelado)}")
            st.write(f"Cantidad: {cantidad_cancelado}")

        with col3:
            st.write("### ❌ Pendientes")
            st.write(f"Total: {bs(total_pendiente)}")
            st.write(f"Cantidad: {cantidad_pendiente}")

        st.markdown("---")

    for s in sorted(df["semana"].dropna().unique()):
        st.markdown(f"## 📆 Semana {int(s)}")

        datos = df[df["semana"] == s].copy()
        datos["precio"] = datos["precio"].apply(bs)
        datos["estado"] = datos["pago"].apply(estado_icono)

        st.dataframe(datos[
            ["estado","dia","producto","precio","cliente","lugar","pago","fecha"]
        ])

# =========================
# 🧾 PENDIENTES
# =========================
elif menu == "🧾 Pendientes":

    pendientes = df[df["pago"] == "Pendiente"]

    if not pendientes.empty:
        df_p = pendientes.copy()
        df_p["precio"] = df_p["precio"].apply(bs)
        df_p["estado"] = df_p["pago"].apply(estado_icono)

        st.dataframe(df_p[
            ["estado","dia","producto","precio","cliente","lugar","fecha"]
        ])

# =========================
# 💰 INVERSORES (COMO ANTES)
# =========================
elif menu == "💰 Inversores":

    if os.path.exists(archivo_inv):
        df_inv = pd.read_csv(archivo_inv)
    else:
        df_inv = pd.DataFrame(columns=["nombre","monto","porcentaje","ganancia","total"])

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

    if not df_inv.empty:
        df_tabla = df_inv.copy()
        df_tabla["monto"] = df_tabla["monto"].apply(bs)
        df_tabla["ganancia"] = df_tabla["ganancia"].apply(bs)
        df_tabla["total"] = df_tabla["total"].apply(bs)
        df_tabla["porcentaje"] = df_tabla["porcentaje"].astype(str) + "%"

        st.dataframe(df_tabla)

# =========================
# 🧨 BORRAR TODO
# =========================
st.sidebar.markdown("---")

if st.sidebar.button("🗑 Borrar TODAS las ventas"):
    if sheet:
        sheet.clear()
        st.success("Ventas eliminadas")
        st.rerun()
