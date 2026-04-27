import streamlit as st
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

st.title("Registro de ventas semanal 💰")

# 🔐 FIREBASE CONFIG
db = None

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": "mi-app-de-ventas-6f000",
            "private_key_id": "93a6db78d19b1a2cf27b5cce17ee11da24aa9a0b",
            "private_key": """-----BEGIN PRIVATE KEY-----
(tu clave larga)
-----END PRIVATE KEY-----""",
            "client_email": "firebase-adminsdk-fbsvc@mi-app-de-ventas-6f000.iam.gserviceaccount.com",
            "client_id": "108854541297629440482",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40mi-app-de-ventas-6f000.iam.gserviceaccount.com"
        })

        firebase_admin.initialize_app(cred)
        db = firestore.client()

    except Exception as e:
        st.error("Error conectando Firebase")
        st.write(e)

else:
    db = firestore.client()

# FUNCIÓN fecha
def obtener_fecha(dia):
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    
    hoy = datetime.now()
    indice_hoy = hoy.weekday()
    
    indice_dia = dias.index(dia)
    
    diferencia = indice_dia - indice_hoy
    fecha = hoy + timedelta(days=diferencia)
    
    return fecha.strftime("%d-%m-%Y")

dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

# Selección
dia = st.selectbox("Selecciona el día", dias)
fecha_actual = obtener_fecha(dia)
st.write("📅 Fecha:", fecha_actual)

# FORMULARIO
with st.form("form_venta", clear_on_submit=True):
    producto = st.text_input("Producto")
    precio_texto = st.text_input("Precio")

    guardar = st.form_submit_button("Guardar venta 💾")

    if guardar:
        if producto and precio_texto:
            try:
                precio = float(precio_texto)

                if db:
                    db.collection("ventas").add({
                        "dia": dia,
                        "producto": producto,
                        "precio": precio,
                        "fecha": fecha_actual
                    })
                    st.success("Venta guardada ✔️")
                else:
                    st.warning("No hay conexión con Firebase")

            except:
                st.error("Precio inválido ❌")
        else:
            st.warning("Completa todos los campos ⚠️")

# LEER DATOS
ventas = []

if db:
    ventas_ref = db.collection("ventas").stream()
    for v in ventas_ref:
        ventas.append(v.to_dict())

# AGRUPAR
ventas_por_dia = {d: [] for d in dias}

for v in ventas:
    ventas_por_dia[v["dia"]].append(v)

# MOSTRAR
st.subheader(f"Ventas de {dia}")

total_dia = 0

for v in ventas_por_dia[dia]:
    st.write(f"{v['producto']} - {v['precio']} Bs")
    total_dia += v["precio"]

st.write(f"💰 Total del día: {total_dia} Bs")

# RESUMEN
st.subheader("📊 Resumen semanal")

total_semana = 0
cantidad_total = 0

for d in dias:
    ventas_d = ventas_por_dia[d]
    
    total_d = sum(v["precio"] for v in ventas_d)
    cantidad_d = len(ventas_d)
    
    st.write(f"{d.capitalize()}: {cantidad_d} ventas | {total_d} Bs")
    
    total_semana += total_d
    cantidad_total += cantidad_d

# INVERSIÓN
inversion = st.number_input("💸 Inversión semanal", min_value=0.0)

ganancia = total_semana - inversion

st.write("🧾 Total vendido:", total_semana)
st.write("📦 Total de ventas:", cantidad_total)
st.write("💵 Ganancia:", ganancia)

# RESULTADO
if ganancia > 0:
    st.success("Resultado: Hubo ganancia 💰")
elif ganancia == 0:
    st.info("Resultado: Se recuperó la inversión 🤝")
else:
    st.error("Resultado: Hubo pérdida ❌")
