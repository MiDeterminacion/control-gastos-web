import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = "finanzas.json"

# ----------------- Funciones básicas -----------------

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
    filtrados = [
        r for r in datos 
        if inicio <= datetime.strptime(r['fecha'], "%Y-%m-%d") <= fin
    ]
    return filtrados

def exportar_excel(datos):
    df = pd.DataFrame(datos)
    archivo = "finanzas_export.xlsx"
    df.to_excel(archivo, index=False)
    return archivo

# ----------------- Interfaz Streamlit -----------------

st.set_page_config(page_title="Control de Gastos", layout="centered")
st.title("💰 Control de Gastos")

menu = st.sidebar.radio("Navegación", ["Registrar", "Resumen", "Exportar"])

if menu == "Registrar":
    st.subheader("Agregar ingreso o gasto")
    tipo = st.selectbox("Tipo de registro", ["ingreso", "gasto"])
    monto = st.number_input("Monto", min_value=0.01, format="%.2f")
    descripcion = st.text_input("Descripción")
    fecha = st.date_input("Fecha", value=datetime.today())
    
    if st.button("Guardar"):
        if descripcion.strip() == "":
            st.warning("La descripción no puede estar vacía.")
        else:
            agregar_registro(
                tipo, monto, descripcion, fecha.strftime("%Y-%m-%d")
            )
            st.success(f"{tipo.capitalize()} guardado correctamente.")

elif menu == "Resumen":
    st.subheader("Ver resumen financiero")

    opciones = {
        "Hoy": (datetime.today(), datetime.today()),
        "Últimos 7 días": (datetime.today() - timedelta(days=7), datetime.today()),
        "Últimos 30 días": (datetime.today() - timedelta(days=30), datetime.today()),
        "Rango personalizado": None
    }

    seleccion = st.selectbox("Selecciona un periodo", list(opciones.keys()))

    if seleccion == "Rango personalizado":
        inicio = st.date_input("Desde", value=datetime.today() - timedelta(days=7))
        fin = st.date_input("Hasta", value=datetime.today())
    else:
        inicio, fin = opciones[seleccion]

    if st.button("Mostrar resumen"):
        registros = filtrar_por_rango(
            datetime.combine(inicio, datetime.min.time()),
            datetime.combine(fin, datetime.max.time())
        )
        if registros:
            ingresos = sum(r["monto"] for r in registros if r["tipo"] == "ingreso")
            gastos = sum(r["monto"] for r in registros if r["tipo"] == "gasto")
            balance = ingresos - gastos

            st.metric("Total ingresos", f"${ingresos:,.2f}")
            st.metric("Total gastos", f"${gastos:,.2f}")
            st.metric("Balance", f"${balance:,.2f}", delta_color="normal" if balance >= 0 else "inverse")

            df = pd.DataFrame(registros)
            st.dataframe(df)

            fig, ax = plt.subplots()
            ax.bar(["Ingresos", "Gastos"], [ingresos, gastos], color=["green", "red"])
            ax.set_ylabel("Monto")
            ax.set_title("Comparativa Ingresos vs Gastos")
            st.pyplot(fig)
        else:
            st.info("No hay registros en ese periodo.")

elif menu == "Exportar":
    st.subheader("Exportar datos a Excel")
    datos = cargar_datos()
    if datos:
        archivo = exportar_excel(datos)
        with open(archivo, "rb") as f:
            st.download_button(
                label="Descargar archivo Excel",
                data=f,
                file_name=archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("No hay datos para exportar.")
