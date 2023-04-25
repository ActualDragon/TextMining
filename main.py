from flask import Flask, redirect, url_for, request, render_template, session, abort #Framework que permite crear aplicaciones web
from werkzeug.utils import secure_filename #validar el archivo
import os #usar funcionalidades dependientes del sistema operativo
import webbrowser #Manejar el navegador
from flaskwebgui import FlaskUI #Import the library that converts the flask web app to a desktop app
import functions as fx

#CLASES
class Goldman_Index:
    edad = 0 #Valor encontrado [Edad]
    edad_p = -1 #Puntaje asignado segun el indice

    IAM = 0 #Infarto agudo de miocardio
    IAM_p = -1

    JVD = 0 #Distención de la vena yugular
    JVD_p = -1

    RS3 = 0 #Ruido cardiaco en S3
    RS3_p = -1

    EA = 0 #Estenosis aórtica
    EA_p = -1

    ECG = 0 #Ritmo distinto al sinusal o CAP (contracciones auriculares prematuras) en su último ECG
    ECG_p = -1

    CVP = 0 #5 contracciones ventriculares prematuras / min documentadas en cualquier momento
    CVP_p = -1

    #PO2 (presión parcial de oxígeno) < 60 o PCO2 (presión parcial de dióxido de carbono) > 50 mm Hg, K (potasio) < 3.0 o HCO3 (bicarbonato) < 20 meq/litro,
    #BUN (nitrógeno ureico en sangre) > 50 o Cr (creatinina) > 3.0 mg/dl, SGOT (transaminasa glutámico-oxalacética) abnormal,
    #señales de enfermedad hepática crónica o paciente postrado por causas no-cardíacas
    estado = 0
    estado_p = -1

    OR = 0 #Cirugia intraperitoneal, intratorácica, aórtica o de emergencia
    OR_p = -1

    is_empty = 0

class Puntaje_Lee:
    OR = 0  #Cirugia de alto riesgo (intraperitoneal, intratorácica o suprainguinal vascular) [Valor encontrado]
    OR_p = -1 #Puntaje asignado segun el indice

    isq = 0 #Historial de enfermedad cardíaca isquémica
    isq_p = -1

    cong = 0 #Historial de enfermedad cardíaca congestiva
    cong_p = -1

    CV = 0 #Historial de enfermedaad cerebrovascular
    CV_p = -1

    diab = 0 #Terapia de insulina para diabéticos
    diab_p = -1

    Cr = 0 #Creatinina preoperatoria > a 2 mg/dL (o > 177 micromol/L)
    Cr_p = -1

    is_empty = 0

class Detsky_Index:
    IAM = 0 #Valor encontrado Infarto agudo de miocardio < o > 6 meses
    IAM_p = -1 #Puntaje asignado segun el indice

    ang = 0 #Angina de pecho según la Sociedad Cardiovascular Canadiense -> Clase III o IV
    ang_p = -1

    angina = 0 #Angina inestable < 3 meses
    angina_p = -1

    edema = 0 #Edema pulmonar < 1 semana o cualquier otro momento
    edema_p = -1

    EA = 0 #Estenosis aórtica crítica
    EA_p = -1

    ECG = 0 #Ritmo distinto al sinusal o extrasístoles auriculares
    ECG_p = -1

    CAP = 0 # >5 CAP (contracciones auriculares prematuras) / min documentados en cualquier momento
    CAP_p = -1

    #PO2 (presión parcial de oxígeno) < 60 o PCO2 (presión parcial de dióxido de carbono) > 50 mm Hg, K (potasio) < 3.0 o HCO3 (bicarbonato) < 20 meq/litro,
    #BUN (nitrógeno ureico en sangre) > 50 o Cr (creatinina) > 3.0 mg/dl, SGOT (transaminasa glutámico-oxalacética) abnormal,
    #señales de enfermedad hepática crónica o paciente postrado por causas no-cardíacas
    estado = 0
    estado_p = -1

    edad = 0  #Edad > 70
    edad_p = -1

    ER = 0 #Cirugía de emergencia
    ER_p = -1

    is_empty = 0

class Puntaje_Padua:
    cancer = 0 #Valor encontrado Cancer activo -> metástasis y/o han pasado por quimioterapia o radioterapia en los últimos 6 meses
    cancer_p = -1 #Puntaje asignado segun el indice

    TEV = 0 #Tromboembolismo venoso (excluyendo trombosis venosa superficial)
    TEV_p = -1

    mov = 0 #Movilidad reducida -> postrado con privilegios de baño (por incapacidad del paciente u órdenes del médico) por lo menos 3 días
    mov_p = -1

    #Condición trombofília conocida (defectos de antitrombina, proteína C o S, factor V Leiden, mutación de protrombina G20210A, síndrome antifosfolípido)
    trombo = 0
    trombo_p = -1

    OR = 0 #Trauma reciente o cirugía <= 1 mes
    OR_p = -1

    edad = 0  #Edad > 70
    edad_p = -1

    falla = 0 #Falla cardíaca y/o respiratoria
    falla_p = -1

    IAM = 0 #Desorden reumatológico agudo o infarto agudo de miocardio
    IAM_p = -1

    BMI = 0 #Obesidad (BMI >= 30)
    BMI_p = -1

    TH = 0 #Tratammiento hormonal actual
    TH_p = -1

    is_empty = 0


# _.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.
# CONSTRUCTOR DE FLASH

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 #Limitar archivos a maximo 1MB
app.config['UPLOAD_PATH'] = r'./static/uploads' #Path al que se subira la copia temporal de los archivos a ser procesados
app.config['UPLOAD_EXTENSIONS'] = ['.doc', '.docx'] #Extensiones permitidas

#Crear interfaz de usuario para la aplicacion de escritorio
ui = FlaskUI(app=app, server="flask", port=5000)

#Generar la home page
@app.route('/')
def load():
    #Eliminar todos las copias temporales de los expedientes que se hayan quedado almacenados si la aplicación no se cerró adecuadamente
    basedir = os.path.abspath(os.path.dirname(__file__)) #Obtener el directorio actual
    path = f"{basedir}\\static\\uploads" #Obtener el directorio de los archivos temporales

    filelist = [ f for f in os.listdir(path) if f.endswith(".doc") or f.endswith(".docx") ] #Obtener los archivos
    for f in filelist:
        os.remove(os.path.join(path, f)) #Eliminar los archivos
    return render_template('index.html')

#Recibir el archivo subido
@app.route('/index', methods=['POST'])
def index():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename) #validar el nombre del archivo
    if filename != '': #validar que si se subió un archivo
        file_ext = os.path.splitext(filename)[1]
        #agregar validación de si no hay archivo
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != fx.validate_file(uploaded_file):
            print("Error controlado")
            abort(400)
        basedir = os.path.abspath(os.path.dirname(__file__)) #Obtener el directorio actual
        uploaded_file.save(os.path.join(basedir,app.config['UPLOAD_PATH'], filename)) #Guardar una copia temporal del archivo subido
    return redirect(url_for('indices', name=filename))

@app.route('/indices/<name>')
def indices(name):
    Goldman = Goldman_Index()
    Lee = Puntaje_Lee()
    Detsky = Detsky_Index()
    Padua = Puntaje_Padua()
    f = fx.Read_File(name) #Leer los contenidos del archivo
    fx.Find_Edad(f,Goldman, Detsky, Padua)
    fx.Find_IAM(f, Goldman, Detsky)
    fx.Find_JVD(f, Goldman)
    empty = fx.FindEmpty(Goldman, Lee, Detsky, Padua) #Determinar si hay atributos vacios
    if empty == 1:
        return render_template('validar.html',Goldman=Goldman, Detsky=Detsky, Lee=Lee, Padua=Padua) #Si hay atributos vacios, redirigir a un form que pide los datos faltantes
    else:
        return render_template('print.html',Goldman=Goldman, Detsky=Detsky, Lee=Lee, Padua=Padua) #Si no hay atributos vacios, redirigir a una pagina que imprime los resultados

#Funcion main driver
if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:5000") #Abrir la pagina principal en el navegador cuando se corre la app
    app.run()
    #ui.run()

#https://medium.com/@fareedkhandev/create-desktop-application-using-flask-framework-ee4386a583e9
