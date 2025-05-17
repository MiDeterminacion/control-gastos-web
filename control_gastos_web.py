import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

DATA_FILE = "finanzas.json"

# ---------- Funciones de datos ----------
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

def guardar_datos(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def agregar_registro(tipo, monto, descripcion, fecha):
    datos = cargar_datos()
    datos.append({
        "tipo": tipo,
        "monto": monto,
        "descripcion": descripcion,
        "fecha": fecha
    })
    guardar_datos(datos)

def filtrar_por_rango(inicio, fin):
    datos = cargar_datos()
    return [r for r in datos if inicio <= datetime.strptime(r['fecha'], "%Y-%m-%d") <= fin]

# ---------- Estilos personalizados ----------
st.set_page_config(page_title="Panel de Finanzas", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #F5F7FA;
    }
    .metric {
        font-size: 24px !important;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        height: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Encabezado ----------
st.title("💸 Panel de Control Financiero")

# ---------- Navegación ----------
menu = st.sidebar.radio("Ir a", ["➕ Registrar", "📈 Resumen", "🛠 Editar / Eliminar"])

# ---------- Registrar ingresos/gastos ----------
if menu == "➕ Registrar":
    st.header("Registrar Ingreso o Gasto")

    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("Tipo de registro", ["ingreso", "gasto"])
        monto = st.number_input("Monto", min_value=0.01, format="%.2f")
    with col2:
        descripcion = st.text_input("Descripción")
        fecha = st.date_input("Fecha", value=datetime.today())

    if st.button("Guardar registro"):
        if descripcion.strip() == "":
            st.warning("La descripción no puede estar vacía.")
        else:
            agregar_registro(tipo, monto, descripcion, fecha.strftime("%Y-%m-%d"))
            st.success(f"{tipo.capitalize()} guardado correctamente.")

# ---------- Resumen ----------
elif menu == "📈 Resumen":
    st.header("Resumen Financiero")

    opciones = {
        "Hoy": (datetime.today(), datetime.today()),
        "Últimos 7 días": (datetime.today() - timedelta(days=7), datetime.today()),
        "Últimos 30 días": (datetime.today() - timedelta(days=30), datetime.today()),
        "Rango personalizado": None
    }

    periodo = st.selectbox("Seleccionar periodo", list(opciones.keys()))
    if periodo == "Rango personalizado":
        col1, col2 = st.columns(2)
        with col1:
            inicio = st.date_input("Desde", value=datetime.today() - timedelta(days=7))
        with col2:
            fin = st.date_input("Hasta", value=datetime.today())
    else:
        inicio, fin = opciones[periodo]

    registros = filtrar_por_rango(
        datetime.combine(inicio, datetime.min.time()),
        datetime.combine(fin, datetime.max.time())
    )

    if registros:
        ingresos = sum(r["monto"] for r in registros if r["tipo"] == "ingreso")
        gastos = sum(r["monto"] for r in registros if r["tipo"] == "gasto")
        balance = ingresos - gastos

        col1, col2, col3 = st.columns(3)
        col1.metric("Ingresos", f"${ingresos:,.2f}")
        col2.metric("Gastos", f"${gastos:,.2f}")
        col3.metric("Balance", f"${balance:,.2f}")

        df = pd.DataFrame(registros)
        st.dataframe(df)

        fig = go.Figure(data=[
            go.Bar(name='Ingresos', x=["Ingresos"], y=[ingresos], marker_color='green'),
            go.Bar(name='Gastos', x=["Gastos"], y=[gastos], marker_color='red')
        ])
        fig.update_layout(title="Comparativa de Ingresos vs Gastos", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay registros en ese periodo.")

# ---------- Editar / Eliminar ----------
elif menu == "🛠 Editar / Eliminar":
    st.header("Editar o Eliminar Registros")

    datos = cargar_datos()
    if datos:
        df = pd.DataFrame(datos)
        df["id"] = df.index
        seleccion = st.selectbox("Selecciona un registro", df.apply(
            lambda r: f"{r['tipo']} - {r['descripcion']} (${r['monto']}) [{r['fecha']}]", axis=1))
        idx = df[df.apply(
            lambda r: f"{r['tipo']} - {r['descripcion']} (${r['monto']}) [{r['fecha']}]", axis=1) == seleccion]['id'].values[0]

        r = datos[idx]
        tipo = st.selectbox("Tipo", ["ingreso", "gasto"], index=["ingreso", "gasto"].index(r["tipo"]))
        monto = st.number_input("Monto", min_value=0.01, value=float(r["monto"]), format="%.2f")
        descripcion = st.text_input("Descripción", value=r["descripcion"])
        fecha = st.date_input("Fecha", value=datetime.strptime(r["fecha"], "%Y-%m-%d"))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Guardar cambios"):
                datos[idx] = {
                    "tipo": tipo,
                    "monto": monto,
                    "descripcion": descripcion,
                    "fecha": fecha.strftime("%Y-%m-%d")
                }
                guardar_datos(datos)
                st.success("Registro actualizado.")
        with col2:
            if st.button("Eliminar registro"):
                datos.pop(idx)
                guardar_datos(datos)
                st.warning("Registro eliminado.")
    else:
        st.info("No hay registros disponibles.")
