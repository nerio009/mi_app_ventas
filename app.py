import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

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

# 🔥 NUEVA FUNCIÓN VISUAL
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

# =========================
# 📚 HISTORIAL
# =========================
elif menu == "📚 Historial":

    for s in sorted(df["semana"].unique()):
        st.markdown(f"## 📆 Semana {s}")

        datos = df[df["semana"] == s].copy()
        datos["precio"] = datos["precio"].apply(bs)
        datos["estado"] = datos["pago"].apply(estado_icono)

        st.dataframe(datos[
            ["estado","dia","producto","precio","cliente","lugar","pago","fecha"]
        ])

        st.markdown("### 🗑 Eliminar por registro")

        for i, row in datos.iterrows():
            cols = st.columns([1,2,1,2,2,1,0.5])
            cols[0].write(row["estado"])
            cols[1].write(row["producto"])
            cols[2].write(row["precio"])
            cols[3].write(row["cliente"])
            cols[4].write(row["lugar"])
            cols[5].write(row["pago"])

            if cols[6].button("🗑", key=f"del_{row['id']}"):
                df = df[df["id"] != row["id"]]
                df.to_csv(archivo, index=False)
                st.success("Eliminado ✅")
                st.rerun()

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
# 💰 INVERSORES
# =========================
elif menu == "💰 Inversores":

    st.subheader("💰 Inversores")

    if not df_inv.empty:
        st.dataframe(df_inv)

# =========================
# 🧨 BORRAR SOLO VENTAS
# =========================
st.sidebar.markdown("---")

if st.sidebar.button("🗑 Borrar TODAS las ventas"):
    if os.path.exists(archivo):
        os.remove(archivo)
        st.success("Ventas eliminadas")
        st.rerun()
