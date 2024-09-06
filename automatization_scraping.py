import pandas as pd #Manejo de datos con DataFrames
import pdfplumber as pdf #Ingresar al PDF
import re #Expresion regular para captura de texto
import time #Manejo de tiempos
from selenium import webdriver #navegado de Selenium
from selenium.webdriver.common.by import By #Encontrar elementos en el codigo del navegador
from selenium.webdriver.support.wait import WebDriverWait #Esperas del navegador
from selenium.webdriver.support import expected_conditions as EC #Esperar una condición del navegador
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException,TimeoutException #Excepciones en Selenium
import datetime #Manero de fechas

with open('codigos.txt', 'r') as archivo:
    """Ingresa al archivo codigos.txt para capturar todos los RUT 
    previamente extraidos"""
    lineas = archivo.readlines()

# Elimina los saltos de línea al final de cada elemento
lineas = [linea.strip() for linea in lineas]

def validar(driver,Lista_Xpath, Lista_Guardar):
    """Función para evitar que salga el error NoSuchElementException cada que no aparece un elemento que se desea extraer.
    Con este codigo se reemplaza por el valor null."""
    for Xpath in Lista_Xpath:
        try:
            elemen = driver.find_element(by=By.XPATH, value=Xpath)
            Lista_Guardar.append(elemen.text)
        except NoSuchElementException:
            elemen = 'null'
            Lista_Guardar.append(elemen)
    return(Lista_Guardar)

list_validar_gen = [
    '//*[@id="results-content"]/tr[2]/td[2]/h3/b', #0 Razon social
    '//*[@id="results-content"]/tr[4]/td[2]', #1 Rubro
    '//*[@id="results-content"]/tr[5]/td[2]', #2 Subrubro
    '//*[@id="results-content"]/tr[6]/td[2]', #3 Actividades economicas
    '//*[@id="results-content"]/tr[7]/td[2]', #4 Region
    '//*[@id="results-content"]/tr[8]/td[2]', #5 Comuna
    '//*[@id="results-content"]/tr[9]/td[2]', #6 Ciudad
    '//*[@id="results-content"]/tr[10]/td[2]', #7 Tipo contribuyente
    '//*[@id="results-content"]/tr[11]/td[2]', #8 Subtipo contribuyente
    '//*[@id="results-content"]/tr[12]/td[2]', #9 Fecha inicio
    '//*[@id="results-content"]/tr[13]/td[2]', #10 Cantidad personas
]

try:
    data_chile = pd.read_csv('./data/datos_chile.csv',sep=';', encoding='utf_8_sig')
    viejos = list(data_chile['RUT'])
except:
    data_chile = pd.DataFrame()
    viejos = []

try:
    df_errores = pd.read_csv('./data/errores_chile.csv',sep=';', encoding='utf_8_sig')
except:
    df_errores = pd.DataFrame()

url = 'https://www.genealog.cl/Geneanexus/search'
options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get(url)

indice = 0
for i,codigo in enumerate(lineas[::-1]):
    try:
        datos_nuevos = {}
        indice +=1
        if codigo in viejos:
            print('Ya existe')
            continue
        if indice == 27:
            break
        try:
            inp_codigo = driver.find_element(By.XPATH,'/html/body/div[4]/div[1]/div/div/div[1]/form/div/div[1]/div[2]/input')
            inp_codigo.send_keys(codigo)
            btn_buscar = driver.find_element(By.XPATH,'//*[@id="searchSubmitInitial"]/button')
            btn_buscar.click()
        except:
            inp_codigo = driver.find_element(By.XPATH,'/html/body/div[4]/div[1]/div/div/div[1]/form/div/div[1]/div[2]/input')
            inp_codigo.clear()
            inp_codigo.send_keys(codigo)
            btn_buscar = driver.find_element(By.XPATH,'/html/body/div[4]/div[1]/div/div/div[1]/form/div/div[1]/div[3]/button')
            btn_buscar.click()
        time.sleep(5)
        
        tip_entidad = driver.find_element(By.XPATH,'//*[@id="results-content"]/tr[2]/td[3]').text
        if tip_entidad.strip() != 'Empresas':
            continue
        list_guardar_gen = []
        time.sleep(2)
        empresa = driver.find_element(By.XPATH, '/html/body/div[4]/div[3]/div/div[5]/div[1]/table/tbody/tr[2]/td[1]/a')
        empresa.click()
        time.sleep(5)
        
        driver.switch_to.window(driver.window_handles[1])
        validar(driver, list_validar_gen, list_guardar_gen)
        raz_soc = list_guardar_gen[0]
        rubro = list_guardar_gen[1]
        subrubro = list_guardar_gen[2]
        act_eco = list_guardar_gen[3]
        region = list_guardar_gen[4]
        comuna = list_guardar_gen[5]
        ciudad = list_guardar_gen[6]
        tip_cont = list_guardar_gen[7]
        sub_tip_cont = list_guardar_gen[8]
        fec_ini = list_guardar_gen[9]
        cant_pers = list_guardar_gen[10]
        
        try:
            btn_cont = driver.find_element(By.XPATH, '//*[@id="OwnEvent_showContact"]/td/button')
            btn_cont.click()
        except:
            print("Sin boton contacto")
            pass
        time.sleep(1)
        
        cont_class = []
        cont_class = driver.find_elements(By.CLASS_NAME, 'parseOnAsk')
        contacto = ''
        correo = ''
        telefono = ''
        new_web = ''
        if len(cont_class) > 0:
            try:
                contacto = cont_class[0].find_element(By.XPATH,'span').text
            except NoSuchElementException:
                contacto = 'null'
            for contenido in cont_class:
                
                texto = contenido.text
                if "@" in texto:
                    emails = re.findall(r'\w+@+\w+.+\w',texto)
                    if len(emails) > 1:
                        for email in emails:
                            correo = correo + '\n'+ email
                    elif len(emails) == 1:
                        correo = emails[0]
                    else:
                        correo = 'null'
                    
                elif "+" in texto:
                    tels = re.findall(r'\d+', texto)
                    if len(tels) > 1:
                        for tel in tels:
                            telefono = telefono + '\n'+ tel
                    elif len(tels) == 1:
                        telefono = tels[0]
                    else:
                        telefono = 'null'
                    
                elif "www." in texto and "www.flaticon.com" not in texto:
                    web = re.findall(r'www.+\w+\w{4}', texto)
                    if len(web) == 0:
                        new_web = 'null'
                    elif len(web) == 1:
                        new_web = web[0].replace("launch","").strip()
                    else:
                        for errase_launche in web:
                            new_text = errase_launche.replace("launch","").strip()
                            new_web = new_web+'\n'+new_text
        
        datos_nuevos = {
            'RUT':codigo,
            'RAZON_SOCIAL':raz_soc,
            'RUBRO':rubro,
            'SUBRUBRO':subrubro,
            'ACTIVIDADES_ECONOMICAS':act_eco,
            'REGION':region,
            'COMUNA':comuna,
            'CIUDAD':ciudad,
            'TIPO_CONTRIBUYENTE':tip_cont,
            'CONTACTO':contacto,
            'CORREO':correo,
            'TELEFONO':telefono,
            'SITIO_WEB':new_web
        }
        df_new = pd.DataFrame(datos_nuevos,index=[indice])
        data_chile = pd.concat((data_chile,df_new))
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    except Exception as ex:
        print("ERROR : ", ex)
        reg_error = {'Fecha':datetime.datetime.now(),
                     'Error':ex,
                     'Codigo':codigo}
        df_new_error = pd.DataFrame(reg_error, index=[indice])
        df_errores = pd.concat((df_errores, df_new_error))
        continue
try:
    data_chile.drop(columns='Unnamed: 0', inplace=True)
except:
    pass
data_chile.to_csv('./data/datos_chile.csv',sep=';', encoding='utf_8_sig')
try:
    df_errores.drop(columns='Unnamed: 0', inplace=True)
except:
    pass
df_errores.to_csv('./data/errores_chile.csv',sep=';', encoding='utf_8_sig')
driver.close()