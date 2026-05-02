import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 🔗 NUEVO: GOOGLE SHEETS
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔗 CONEXIÓN GOOGLE SHEETS (NO ROMPE NADA)
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
    sheet = None  # Si falla, no rompe la app

# =========================

st.set_page_config(page_title="Ventas", layout="centered")
st.title("Registro de ventas semanal 💰")

archivo = "ventas.csv"
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

# 📥 DATOS
if os.path.exists(archivo):
    df = pd.read_csv(archivo)
else:
    df = pd.DataFrame(columns=[
        "id","dia","producto","precio","cliente","lugar","pago","fecha","semana"
    ])

if os.path.exists(archivo_inv):
    df_inv = pd.read_csv(archivo_inv)
else:
    df_inv = pd.DataFrame(columns=["nombre","monto","porcentaje","ganancia","total"])

# 📂 MENU
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
                    nueva = pd.DataFrame([{
                        "id": (df["id"].max() + 1) if not df.empty else 1,
                        "dia": dia,
                        "producto": producto,
                        "precio": precio,
                        "cliente": cliente,
                        "lugar": lugar,
                        "pago": pago,
                        "fecha": fecha_actual,
                        "semana": semana_actual
                    }])

                    df = pd.concat([df, nueva], ignore_index=True)
                    df.to_csv(archivo, index=False)

                    # 🔥 NUEVO: TAMBIÉN GUARDA EN GOOGLE SHEETS
                    if sheet:
                        sheet.append_row([
                            nueva["id"].iloc[0],
                            dia,
                            producto,
                            precio,
                            cliente,
                            lugar,
                            pago,
                            fecha_actual,
                            semana_actual
                        ])

                    st.success("Venta guardada ✅")
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
# RESTO DEL CÓDIGO IGUAL
# =========================

st.sidebar.markdown("---")

if st.sidebar.button("🗑 Borrar TODAS las ventas"):
    if os.path.exists(archivo):
        os.remove(archivo)
        st.success("Ventas eliminadas")
        st.rerun()
