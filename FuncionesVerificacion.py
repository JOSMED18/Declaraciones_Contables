import pandas as pd
from openpyxl import load_workbook

# FUNCIONES

## Función para verificación del RUC
def VerificacionRUC (df):
    df_RUC = df.copy()
    df_RUC["Tiene14"] = df_RUC[df_RUC.columns[0]].astype(str).map(len)!=14.00
    df_result = df_RUC[df_RUC["Tiene14"] == True].drop(["Tiene14"],axis=1)
    result = None
    if df_result.empty:
        result = "Todos los RUC tienen 14 caracteres ✅"
    else:
        result = df_result
    
    return result


## Función para verificación los numeros de documentos
def VerificacionNoDocumento(df):
    
    
    df_docnumber  = df.copy()
    df_docnumber["DocEsNo"] = pd.to_numeric(df_docnumber["Numero Documento"], errors='coerce').isnull()
    df_result = df_docnumber[(df_docnumber["DocEsNo"] == True) & (~df_docnumber["Numero Documento"].isna())].drop("DocEsNo", axis=1)
    

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
def VerificacionFormula (file,document):
    
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
    elif document == 0:
        result = df_result[df_result.columns[:8]]
    elif document == 1:
        result = df_result[df_result.columns[:10]]
    else:
        result = ""

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



# FUNCIONES DE DOCUMENTO DE RETENCIONES


## Funcion para verificar que los codigos y descripciones coincidan

def VerificacionINSS (df):
    df_calculation = df.copy()
    df_calculation["Calculo INSS"] = round(df_calculation[df_calculation.columns[3]]/df_calculation[df_calculation.columns[2]],2)
    df_calculation["% Calculo INSS"] = (df_calculation["Calculo INSS"] * 100).astype(str) + '%'
    df_result = df_calculation[(df_calculation["Calculo INSS"] != 0.07) &
                               (~df_calculation["INGRESOS BRUTOS MENSUALES"].isna())].drop("Calculo INSS",axis=1)

    if df_result.empty:
        result = "El INSS está calculado correctamente (7% del monto) ✅"
    else:
        result = df_result

    return result

## Funcion para verificar el valor de base imponible
def VerificacionBase(df):
    df_base = df.copy()
    df_base["Calculo Base"] = round(df_base["INGRESOS BRUTOS MENSUALES"] - df_base["VALOR COTIZACIÓN INSS"],2)
    df_result = None
    df_result = df_base[(df_base["Calculo Base"] != df_base["BASE IMPONIBLE"]) & (~df_base["INGRESOS BRUTOS MENSUALES"].isna())]
    if df_result.empty:
        result = "La base imponible está bien calculada ✅"
    else:
        result = df_result

    return result


## Funcion para verificar el valor retenido
def VerificacionRetenciones(df):

    df_retencion = df.copy()

    def CalculoIR (x):
        base = x * 12 *0.93

        if base >= 0 and base <= 100000:
            impuesto = 0

        elif base >= 100001  and base <= 200000:
            ImpuestoMensual = ( ( base - 100000 ) * 0.15 ) / 12

        elif base >= 200001  and base <= 350000:
            ImpuestoMensual = ( ( ( base - 200000 ) * 0.20 ) + 15000 ) / 12

        elif base >= 350001  and base <= 500000:
            ImpuestoMensual = ( ( ( base - 350000 ) * 0.25 ) + 45000 ) / 12

        else:
            ImpuestoMensual = ( ( ( base - 500000 ) * 0.30 ) + 82500 ) / 12

        return round(ImpuestoMensual,2)

    def CalculoRetencion(x):
        Retencion = x * 0.02
        return round(Retencion,2)

    def CalculoServicios (x):
        Retencion = x * 0.1
        return round(Retencion,2)

    df_retencion["Calculo IR"] = df_retencion.apply(lambda row: CalculoIR(row["INGRESOS BRUTOS MENSUALES"]) if row["CÓDIGO DE RETENCIÓN"] == 11
                                                    else (CalculoRetencion(row["BASE IMPONIBLE"]) if row["CÓDIGO DE RETENCIÓN"] == 22 else CalculoServicios(row["BASE IMPONIBLE"])), axis=1)
    
    df_result = df_retencion[df_retencion["Calculo IR"] != df_retencion["VALOR RETENIDO"]]

    result = None

    if df_result.empty:
        result = "El valor retenido está bien calculado ✅"
    else:
        result = df_result

    return result



