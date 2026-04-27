import streamlit as st
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

st.title("Registro de ventas semanal 💰")

# 🔐 Cargar credenciales desde secrets (Streamlit Cloud)
db = None

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except:
        st.warning("Firebase no configurado aún ⚠️")
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
                    st.toast("Venta guardada ✔️")
                else:
                    st.warning("No se guardó: Firebase no configurado")

            except:
                st.error("Precio inválido ❌")
        else:
            st.warning("Completa todos los campos ⚠️")

# 🔄 LEER DATOS DESDE FIREBASE
ventas = []

if db:
    ventas_ref = db.collection("ventas").stream()
    for v in ventas_ref:
        ventas.append(v.to_dict())

# Convertir a estructura por día
ventas_por_dia = {d: [] for d in dias}

for v in ventas:
    ventas_por_dia[v["dia"]].append(v)

# Mostrar ventas del día
st.subheader(f"Ventas de {dia}")

total_dia = 0

for v in ventas_por_dia[dia]:
    st.write(f"{v['producto']} - {v['precio']} Bs")
    total_dia += v["precio"]

st.write(f"💰 Total del día: {total_dia} Bs")

# Resumen semanal
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

# Inversión
inversion = st.number_input("💸 Inversión semanal", min_value=0.0)

ganancia = total_semana - inversion

st.write("🧾 Total vendido:", total_semana)
st.write("📦 Total de ventas:", cantidad_total)
st.write("💵 Ganancia:", ganancia)

# Resultado
if ganancia > 0:
    st.success("Resultado: Hubo ganancia 💰")
elif ganancia == 0:
    st.info("Resultado: Se recuperó la inversión 🤝")
else:
    st.error("Resultado: Hubo pérdida ❌")
