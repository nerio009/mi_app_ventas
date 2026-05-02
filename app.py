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
    if n == int(n):
        return f"{int(n):,} Bs"
    else:
        return f"{n:,.2f} Bs"

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

# ======================================
# 🔥 NAVEGACIÓN
# ======================================
menu = st.sidebar.radio(
    "📂 Navegación",
    ["📅 Registro", "📚 Historial", "🧾 Pendientes", "💰 Inversores"]
)

# =========================
# 📅 REGISTRO
# =========================
if menu == "📅 Registro":

    indice_hoy = datetime.now().weekday()
    dia = st.selectbox("Selecciona el día", dias, index=indice_hoy)

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
                st.error("Ingresa un número válido")

    ventas_dia = df[df["dia"] == dia]

    st.subheader(f"Ventas de {dia}")

    if not ventas_dia.empty:
        df_mostrar = ventas_dia.copy()
        df_mostrar["precio"] = df_mostrar["precio"].apply(bs)

        st.dataframe(df_mostrar[
            ["id","producto","precio","cliente","lugar","pago","fecha"]
        ])

        total = ventas_dia["precio"].sum()
        st.write(f"💰 Total: {bs(total)}")
    else:
        st.info("No hay ventas")

    # 🗑 Eliminar venta (lista rápida en Registro)
    st.subheader("🗑 Eliminar venta")
    if not ventas_dia.empty:
        opciones = ventas_dia.apply(
            lambda x: f"ID {int(x['id'])} | {x['producto']} - {x['cliente']} - {x['precio']} Bs",
            axis=1
        ).tolist()

        seleccion = st.selectbox(
            "Selecciona venta a eliminar",
            opciones,
            key="eliminar_venta"
        )

        if st.button("❌ Eliminar venta"):
            idx_local = opciones.index(seleccion)
            id_sel = int(ventas_dia.iloc[idx_local]["id"])
            df = df[df["id"] != id_sel]
            df.to_csv(archivo, index=False)
            st.success("Venta eliminada ✅")
            st.rerun()

# =========================
# 📚 HISTORIAL
# =========================
elif menu == "📚 Historial":

    st.subheader("📚 Historial semanal")

    if df.empty:
        st.warning("No hay registros")
    else:
        for s in sorted(df["semana"].unique()):
            st.markdown(f"## 📆 Semana {s}")

            datos = df[df["semana"] == s].copy()
            datos_fmt = datos.copy()
            datos_fmt["precio"] = datos_fmt["precio"].apply(bs)

            st.dataframe(datos_fmt[
                ["id","dia","producto","precio","cliente","lugar","pago","fecha"]
            ])

            # 🔥 SOLO CANCELADOS
            cancelados = df[
                (df["semana"] == s) & (df["pago"] == "Cancelado")
            ]
            total = cancelados["precio"].sum()
            st.write(f"💰 Total REAL (Cancelados): {bs(total)}")

            # =========================
            # 🗑 ELIMINAR CON ICONO POR FILA (HISTORIAL)
            # =========================
            st.markdown("### 🗑 Eliminar por registro")
            for i, row in datos.iterrows():
                c1, c2, c3, c4, c5, c6, c7 = st.columns([1.2,1.5,1.2,1.5,1.2,1.2,0.6])

                c1.write(row["dia"])
                c2.write(row["producto"])
                c3.write(bs(row["precio"]))
                c4.write(row["cliente"])
                c5.write(row["lugar"])
                c6.write(row["pago"])

                if c7.button("🗑", key=f"del_hist_{int(row['id'])}"):
                    df = df[df["id"] != int(row["id"])]
                    df.to_csv(archivo, index=False)
                    st.success("Venta eliminada ✅")
                    st.rerun()

# =========================
# 🧾 PENDIENTES
# =========================
elif menu == "🧾 Pendientes":

    st.subheader("🧾 Ventas pendientes")

    pendientes = df[df["pago"] == "Pendiente"]

    if not pendientes.empty:
        df_p = pendientes.copy()
        df_p["precio"] = df_p["precio"].apply(bs)

        st.dataframe(df_p[
            ["id","dia","producto","precio","cliente","lugar","fecha"]
        ])

        total_pendiente = pendientes["precio"].sum()
        st.write(f"💸 Total pendiente: {bs(total_pendiente)}")
    else:
        st.success("No hay deudas pendientes 🎉")

# =========================
# 💰 INVERSORES
# =========================
elif menu == "💰 Inversores":

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

    # 🗑 BORRAR INVERSOR INDIVIDUAL
    st.subheader("🗑 Eliminar inversor")

    if not df_inv.empty:
        nombres = df_inv["nombre"].tolist()

        nombre_eliminar = st.selectbox(
            "Selecciona inversor a eliminar",
            nombres,
            key="eliminar_inversor"
        )

        if st.button("❌ Eliminar inversor"):
            df_inv = df_inv[df_inv["nombre"] != nombre_eliminar]
            df_inv.to_csv(archivo_inv, index=False)
            st.success("Inversor eliminado ✅")
            st.rerun()

# =========================
# 🧨 BORRAR TODO (SOLO VENTAS)
# =========================
st.sidebar.markdown("---")
st.sidebar.subheader("⚠️ Modo prueba (solo ventas)")

if "confirmar_borrado" not in st.session_state:
    st.session_state.confirmar_borrado = False

if not st.session_state.confirmar_borrado:
    if st.sidebar.button("🗑 Borrar TODAS las ventas"):
        st.session_state.confirmar_borrado = True
        st.rerun()
else:
    if st.sidebar.button("✅ Confirmar borrado"):
        # SOLO borra ventas
        if os.path.exists(archivo):
            os.remove(archivo)

        st.success("Ventas eliminadas")
        st.session_state.confirmar_borrado = False
        st.rerun()

    if st.sidebar.button("❌ Cancelar"):
        st.session_state.confirmar_borrado = False
        st.rerun()
