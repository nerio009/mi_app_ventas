import streamlit as st

st.title("Sistema de ventas 💰")

# Inicializar lista
if "ventas" not in st.session_state:
    st.session_state.ventas = []

venta = st.number_input("Ingresa una venta:", min_value=0)

if st.button("Agregar venta"):
    st.session_state.ventas.append(venta)

# Mostrar ventas
st.write("Ventas registradas:", st.session_state.ventas)

# Análisis
if len(st.session_state.ventas) > 0:
    ventas = st.session_state.ventas
    
    total = sum(ventas)
    cantidad = len(ventas)
    promedio = total / cantidad
    mayor = max(ventas)
    menor = min(ventas)

    st.subheader("📊 Análisis")
    st.write("Cantidad:", cantidad)
    st.write("Total:", total)
    st.write("Promedio:", promedio)
    st.write("Venta mayor:", mayor)
    st.write("Venta menor:", menor)