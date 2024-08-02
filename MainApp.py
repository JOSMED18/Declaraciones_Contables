import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from FuncionesVerificacion import VerificacionRUC, VerificacionNoDocumento, VerificacionFecha, VerificacionFormula, VerificacionIVA, VerificacionCodigo, VerificacionBase, VerificacionINSS,VerificacionRetenciones


# Encabezado e Imagen
st.image('Logo negativo M&L.png', width = 250)
st.header('Validación de tablas de declaración', divider= "blue")

#Creación de tabs separadas para cada formato
tab1, tab2 = st.tabs(["Crédito Fiscal", "Retenciones"]) 


with tab1:
    x = st.file_uploader('Ingrese formato de planilla de crédito fiscal aquí', type=["xlsx","csv"])
    try:
        #Reading dataframe with pandas
        df_IVA = pd.read_excel(x, names= ['Numero RUC', 'Nombre y Apellido o Razon Social', 'Numero Documento',
        'Descripcion del Pago', 'Fecha de Emision de Documento',
        'Ingreso sin IVA', 'Monto IVA Trasladado', 'Codigo Renglon'])
            
        #Mostrando las primeras filas del dataframe
        st.write("ESTAS SON LAS PRIMERAS FILAS DE LA TABLA QUE INGRESASTE")
        st.dataframe(data=df_IVA.head())

        "---"
        
        #Evaluación de las columnas
        RucV1 = VerificacionRUC(df_IVA)
        DocV1 = VerificacionNoDocumento(df_IVA)
        FechaV1 = VerificacionFecha(df_IVA)
        FormulaV1 = VerificacionFormula(x,0)
        IVAV1 = VerificacionIVA(df_IVA)
        CodV1 = VerificacionCodigo(df_IVA)

        # Verificación del RUC
        st.subheader("Revisión del RUC")
        if isinstance(RucV1, pd.DataFrame):
            st.write("LOS SIGUIENTES RUC _**NO**_ TIENEN 14 CARACTERES - **REVISAR** ✖️✖️✖️")
            st.dataframe(RucV1)
        else:
            st.write(RucV1)
        "---"
        
        # Verificación del numero de documento
        st.subheader("Revisión del número de documento")
        if isinstance(DocV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**TIENEN**_ LETRAS EN EL NÚMERO DE DOCUMENTO - **REVISAR** ✖️✖️✖️")
            st.dataframe(DocV1)
        else:
            st.write(DocV1)
        "---"

        # Verificación de la fecha
        st.subheader("Revisión de la fecha")
        if isinstance(FechaV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**NO**_ SON FECHAS O _**NO**_ SON DE ESTE AÑO - **REVISAR** ✖️✖️✖️")
            st.dataframe(FechaV1)
        else:
            st.write(FechaV1)
        "---"

        # Verificación de formula
        st.subheader("Revisión de formulas")
        if isinstance(FormulaV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**TIENEN**_ CELDAS CON FÓRMULAS - **REVISAR** ✖️✖️✖️")
            st.dataframe(FormulaV1)
        else:
            st.write(FormulaV1)
        "---"

        #Verificación del IVA
        st.subheader("Revisión del IVA")
        if isinstance(IVAV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**NO**_ TIENEN IVA DEL 15%  - **REVISAR** ✖️✖️✖️")
            st.dataframe(IVAV1)
        else:
            st.write(IVAV1)
        "---"
        
        # Verificación de CODIGO
        st.subheader("Revisión del codigo o renglón")
        if isinstance(CodV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**NO**_ TIENEN EL CODIGO O DESCRIPCIÓN CORRECTAS  - **REVISAR** ✖️✖️✖️")
            st.dataframe(CodV1)
        else:
            st.write(CodV1)
        "---"

    except: 
        st.text("No se ha subido el documento")


# Tabla Progresiva de IR de las rentas de trabajo



with tab2:
    
    y = st.file_uploader('Ingrese formato de retenciones aquí', type=["xlsx","csv"])

    try:
        
        
        df_retenciones = pd.read_excel(y, names=['No. RUC', 'NOMBRE Y APELLIDOS Ó RAZÓN SOCIAL',
       'INGRESOS BRUTOS MENSUALES', 'VALOR COTIZACIÓN INSS',
       'VALOR FONDO PENSIONES AHORRO', 'Numero Documento',
       'Fecha de Emision de Documento', 'BASE IMPONIBLE', 'VALOR RETENIDO',
       'ALÍCUOTA DE RETENCIÓN', 'CÓDIGO DE RETENCIÓN'])
        
        st.write()
        #Mostrando los primeros registros de la tabla
        st.write("ESTAS SON LAS PRIMERAS FILAS DE LA TABLA QUE INGRESASTE")
        st.dataframe(data=df_retenciones.head())        
        "---"
        
        
        RucV2 = VerificacionRUC(df_retenciones)
        INSSV2 = VerificacionINSS(df_retenciones)
        BaseV2 = VerificacionBase(df_retenciones)
        FormulaV2 = VerificacionFormula(y,1)
        FechaV2 = VerificacionFecha (df_retenciones)
        RetV2 = VerificacionRetenciones(df_retenciones)
        DocV2 = VerificacionNoDocumento(df_retenciones)

        # Verificación del RUC
        st.subheader("Revisión del RUC")

        if isinstance(RucV2, pd.DataFrame):
            st.write("LOS SIGUIENTES RUC _**NO**_ TIENEN 14 CARACTERES - **REVISAR** ✖️✖️✖️")
            st.dataframe(RucV2)
        else:
            st.write(RucV2)
        "---"


        # Verificación del numero de documento
        st.subheader("Revisión del número de documento")
        if isinstance(DocV2, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**TIENEN**_ LETRAS EN EL NÚMERO DE DOCUMENTO - **REVISAR** ✖️✖️✖️")
            st.dataframe(DocV2)
        else:
            st.write(DocV2)
        "---"

        # Verificación del INSS
        st.subheader("Revisión de Calculo del INSS")

        if isinstance(INSSV2, pd.DataFrame):
            st.write("LOS SIGUIENTES MONTOS DE INSS _**NO**_ SON EL 7% DEL INGRESO BRUTO MENSUAL - **REVISAR** ✖️✖️✖️")
            st.dataframe(INSSV2)
        else:
            st.write(INSSV2)
        "---"

        # Verificación de Base Imponible
        st.subheader("Revisión de Base Imponible")

        if isinstance(BaseV2, pd.DataFrame):
            st.write("LOS SIGUIENTES MONTOS DE BASE IMPONIBLE _**NO**_ COINCIDEN CON CALCULO (INGRESO BRUTO - INSS) - **REVISAR** ✖️✖️✖️")
            st.dataframe(BaseV2)
        else:
            st.write(BaseV2)
        "---"

        # Verificación de la fecha
        st.subheader("Revisión de la fecha")
        if isinstance(FechaV2, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**NO**_ SON FECHAS O _**NO**_ SON DE ESTE AÑO - **REVISAR** ✖️✖️✖️")
            st.dataframe(FechaV2)
        else:
            st.write(FechaV2)
        "---"

        # Verificación de formula
        st.subheader("Revisión de formulas")
        if isinstance(FormulaV2, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**TIENEN**_ CELDAS CON FÓRMULAS - **REVISAR** ✖️✖️✖️")
            st.dataframe(FormulaV2)
        else:
            st.write(FormulaV2)
        "---"

        # Verificación de retenciones
        st.subheader("Revisión de Retenciones")
        if isinstance(RetV2, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**DIFIEREN**_ CON EL CÁLCULO DEL IR - **REVISAR** ✖️✖️✖️")
            st.dataframe(RetV2)
        else:
            st.write(RetV2)
        "---"


    except: 
        st.text("No se ha subido el documento")

        