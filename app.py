import streamlit as st
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(page_title="Ventas", layout="centered")

st.title("Registro de ventas semanal 💰")

# 🔐 CONEXIÓN A FIREBASE
db = None

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("mi-app-de-ventas-6f000-firebase-adminsdk-fbsvc-59f54e0558.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()

except Exception as e:
    st.error("Firebase no configurado correctamente ❌")
    st.write(e)

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

# 📌 SELECCIÓN DE DÍA
dia = st.selectbox("Selecciona el día", dias)
fecha_actual = obtener_fecha(dia)

st.write("📅 Fecha:", fecha_actual)

# 🧾 FORMULARIO
with st.form("form_venta", clear_on_submit=True):
    producto = st.text_input("Producto")
    precio = st.number_input("Precio", min_value=0.0, step=0.1)

    guardar = st.form_submit_button("Guardar venta 💾")

    if guardar:
        if not producto:
            st.warning("Ingresa el producto ⚠️")

        elif precio <= 0:
            st.error("El precio debe ser mayor a 0 ❌")

        else:
            if db:
                try:
                    db.collection("ventas").add({
                        "dia": dia,
                        "producto": producto,
                        "precio": float(precio),
                        "fecha": fecha_actual,
                        "timestamp": datetime.now()
                    })
                    st.success("Venta guardada ✔️")

                except Exception as e:
                    st.error("Error guardando en Firebase ❌")
                    st.write(e)
            else:
                st.warning("No hay conexión con Firebase")

# 📥 LEER DATOS
ventas = []

if db:
    try:
        ventas_ref = db.collection("ventas").stream()
        for v in ventas_ref:
            data = v.to_dict()

            # Validación de datos
            if "dia" in data and "precio" in data:
                ventas.append(data)

    except Exception as e:
        st.warning("Error leyendo datos")
        st.write(e)

# 📊 AGRUPAR POR DÍA
ventas_por_dia = {d: [] for d in dias}

for v in ventas:
    ventas_por_dia[v["dia"]].append(v)

# 📅 MOSTRAR VENTAS DEL DÍA
st.subheader(f"Ventas de {dia}")

total_dia = 0

for v in ventas_por_dia[dia]:
    precio = float(v.get("precio", 0))
    st.write(f"{v.get('producto', 'Sin nombre')} - {precio} Bs")
    total_dia += precio

st.write(f"💰 Total del día: {total_dia} Bs")

# 📊 RESUMEN SEMANAL
st.subheader("📊 Resumen semanal")

total_semana = 0
cantidad_total = 0

for d in dias:
    ventas_d = ventas_por_dia[d]

    total_d = sum(float(v.get("precio", 0)) for v in ventas_d)
    cantidad_d = len(ventas_d)

    st.write(f"{d.capitalize()}: {cantidad_d} ventas | {total_d} Bs")

    total_semana += total_d
    cantidad_total += cantidad_d

# 💸 INVERSIÓN
inversion = st.number_input("💸 Inversión semanal", min_value=0.0)

ganancia = total_semana - inversion

st.write("🧾 Total vendido:", total_semana)
st.write("📦 Total de ventas:", cantidad_total)
st.write("💵 Ganancia:", ganancia)

# 📈 RESULTADO FINAL
if ganancia > 0:
    st.success("Resultado: Hubo ganancia 💰")
elif ganancia == 0:
    st.info("Resultado: Se recuperó la inversión 🤝")
else:
    st.error("Resultado: Hubo pérdida ❌")
