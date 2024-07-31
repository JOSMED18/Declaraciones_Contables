import streamlit as st
import pandas as pd
from openpyxl import load_workbook


# FUNCIONES


## Función para verificación del RUC
def VerificacionRUC (df):
    df_RUC = df.copy()
    df_RUC["Tiene14"] = df_RUC["Numero RUC"].map(len)!=14.00
    df_result = df_RUC[df_RUC["Tiene14"] == True].drop(["Tiene14"],axis=1)
    result = None
    if df_result.empty:
        result = "Todos los RUC tienen 14 caracteres ✅"
    else:
        result = df_result
    
    return result


## Función para verificación los numeros de documentos
def VerificacionNoDocumento (df):
    
    
    df_docnumber  = df.copy()
    df_docnumber["DocEsNo"] = pd.to_numeric(df["Numero Documento"], errors='coerce').isnull()
    df_result = df_docnumber[df_docnumber["DocEsNo"] == True].drop("DocEsNo", axis=1)
    

    if df_result.empty:
        result = "Los documentos no contienen letras ✅"
    else:
        result = df_result
    
    return result


## Función para verificar que los datos sean fechas y sean del año corriente
def VerificacionFecha (df):
    df_date = df.copy()
    
    def es_fecha(value):
        try:
            pd.to_datetime(value,errors='raise')
            return True
        except ValueError:
            return False

    df_date["es_fecha"] = df_date["Fecha de Emision de Documento"].apply(es_fecha)
    df_date["Fecha de Emision de Documento"] = pd.to_datetime(df_date["Fecha de Emision de Documento"], errors='coerce')
    df_date["Año"] = df_date["Fecha de Emision de Documento"].dt.year
    df_result = df_date[(df_date["Año"] != pd.Timestamp.today().year) | 
                        (df_date["es_fecha"] == False)].drop("Año", axis = 1)
    
    
    result = None


    if df_result.empty:
        result = "Las fechas son de este año y están correctamente digitadas ✅"
    else:
        result = df_result
    
    return result


## Función para verificar que la hoja no tenga formulas
def VerificacionFormula (file):
    
    #Sub-función para rastrear formulas 
    def contains_equal (celda):
        return '=' in str(celda)
    
    #Leyendo el archivo con el motor Openpyxl para captar las celdas con formulas
    ws = load_workbook(file, data_only=False).active
    data = list(ws.values)
    df_monto = pd.DataFrame(data[1:], columns=data[0])

    df_bool = df_monto.applymap(contains_equal)
    df_result = df_monto[df_bool.any(axis=1)]

    result = None

    if df_result.empty:
        result = "Ninguna celda en el archivo tiene fórmulas ✅"
    else:
        result = df_result[df_result.columns[:8]]

    return result

## Función para verificar el monto del IVA
def VerificacionIVA (df):
    df_calculation = df
    df_calculation["Calculo IVA"] = round(df_calculation["Monto IVA Trasladado"]/df_calculation["Ingreso sin IVA"],2)
    df_calculation["% Calculo IVA"] = (df_calculation["Calculo IVA"] * 100).astype(str) + '%'
    df_result = df_calculation[df_calculation["Calculo IVA"] != 0.15].drop("Calculo IVA",axis=1)

    if df_result.empty:
        result = "El IVA está calculado correctamente (15% del monto) ✅"
    else:
        result = df_result

    return result


## Funcion para verificar que los codigos y descripciones coincidan
def VerificacionCodigo (df):
    df_codigo = df.copy()
    df_codigo["Verificacion"] = df_codigo["Descripcion del Pago"] + df_codigo["Codigo Renglon"].astype(str)
    df_result = df_codigo[~df_codigo["Verificacion"].isin(["Compra11","Servicios13"])]


    result = None

    if df_result.empty:
        result = "Los codigos y descripciones coinciden ✅"
    else:
        result = df_result

    return result

#Header image and page heading
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
            
        #Displaying dataframe into streamlit page
        st.write("ESTAS SON LAS PRIMERAS FILAS DE LA TABLA QUE INGRESASTE")
        st.dataframe(data=df_IVA.head())

        "---"
        
        #Evaluación de las columnas
        RucV1 = VerificacionRUC(df_IVA)
        DocV1 = VerificacionNoDocumento(df_IVA)
        DateV1 = VerificacionFecha(df_IVA)
        FormulaV1 = VerificacionFormula(x)
        IVAV1 = VerificacionIVA(df_IVA)
        CodV1 = VerificacionCodigo(df_IVA)

        # Verificación del RUC
        if isinstance(RucV1, pd.DataFrame):
            st.write("LOS SIGUIENTES RUC _**NO**_ TIENEN 14 CARACTERES - **REVISAR** ✖️✖️✖️")
            st.dataframe(RucV1)
        else:
            st.write(RucV1)
        "---"
        
        # Verificación del numero de documento
        if isinstance(DocV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**TIENEN**_ LETRAS EN EL NÚMERO DE DOCUMENTO - **REVISAR** ✖️✖️✖️")
            st.dataframe(DocV1)
        else:
            st.write(DocV1)
        "---"

        # Verificación de la fecha
        if isinstance(DateV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**NO**_ SON FECHAS O _**NO**_ SON DE ESTE AÑO - **REVISAR** ✖️✖️✖️")
            st.dataframe(DateV1)
        else:
            st.write(DateV1)
        "---"

        # Verificación de formula
        if isinstance(FormulaV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**TIENEN**_ CELDAS CON FÓRMULAS - **REVISAR** ✖️✖️✖️")
            st.dataframe(FormulaV1)
        else:
            st.write(FormulaV1)
        "---"

        #Verificación de formula
        if isinstance(IVAV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**NO**_ TIENEN IVA DEL 15%  - **REVISAR** ✖️✖️✖️")
            st.dataframe(IVAV1)
        else:
            st.write(IVAV1)
        "---"
        
        # Verificación de CODIGO
        if isinstance(CodV1, pd.DataFrame):
            st.write("LOS SIGUIENTES REGISTROS _**NO**_ TIENEN EL CODIGO O DESCRIPCIÓN CORRECTAS  - **REVISAR** ✖️✖️✖️")
            st.dataframe(CodV1)
        else:
            st.write(CodV1)
        "---"

    except: 
        st.text("No se ha subido el documento")





with tab2:
    
    y = st.file_uploader('Ingrese formato de retenciones aquí')

    try:
        #Reading dataframe with pandas
        df_retenciones = pd.read_excel(y, names= ['Numero RUC', 'Nombre y Apellido o Razon Social', 'Numero Documento',
        'Descripcion del Pago', 'Fecha de Emision de Documento',
        'Ingreso sin IVA', 'Monto IVA Trasladado', 'Codigo Renglon'])
        
        #Mostrando la tabla con los registros incorrectos
        st.dataframe(data=df_retenciones)
    except: 
        st.text("No se ha subido el documento")