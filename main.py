from flask import Flask, redirect, url_for, request, render_template, session, abort, jsonify #Framework que permite crear aplicaciones web
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

    JVD = ["",""] #Distención de la vena yugular o ruido cardíaco en S3
    JVD_p = -1

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

    OR = 0 #Cirugia intraperitoneal, intratorácica o aórtica
    OR_p = -1

    ER = 0 #Cirugia de emergencia
    ER_p = -1

    is_empty = 0
    total = 0
    eval = ""

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
    total = 0
    eval = ""

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
    total = 0
    eval = ""

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
    total = 0
    eval = ""

# _.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.

def MakeClass(type,list): #Almacenar los objetos para poder accesarlos desde las diversas páginas
    match list:
        case "G":
            Name = "Goldman"
            List = ["edad_p", "IAM_p", "JVD_p", "EA_p", "ECG_p", "CVP_p", "estado_p", "OR_p", "ER_p", "edad", "IAM", "JVD", "EA", "ECG", "CVP", "estado", "OR", "ER"]
        case "D":
            Name = "Detsky"
            List = ["IAM_p", "ang_p", "angina_p", "edema_p", "EA_p", "ECG_p", "CAP_p", "estado_p", "edad_p", "ER_p","IAM", "ang", "angina", "edema", "EA", "ECG", "CAP", "estado", "edad", "ER"]
        case "L":
            Name = "Lee"
            List = ["OR_p", "isq_p", "cong_p", "CV_p", "diab_p", "Cr_p", "OR", "isq", "cong", "CV", "diab", "Cr"]
        case "P":
            Name = "Padua"
            List = ["cancer_p", "TEV_p", "mov_p", "trombo_p", "OR_p", "edad_p", "falla_p", "IAM_p", "BMI_p", "TH_p", "cancer", "TEV", "mov", "trombo", "OR", "edad", "falla", "IAM", "BMI", "TH"]
        case _:
            return 0
    for x in range(len(List)):
        var = Name+"."+List[x]
        val = getattr(type,List[x])
        session[var] = val
    return 0

def FindClass(type): #Acceder a los objetos guardados
    match type:
        case "Goldman":
            Object = Goldman_Index()
            List = ["edad_p", "IAM_p", "JVD_p", "EA_p", "ECG_p", "CVP_p", "estado_p", "OR_p", "ER_p", "edad", "IAM", "JVD", "EA", "ECG", "CVP", "estado", "OR", "ER"]
        case "Detsky":
            Object = Detsky_Index()
            List = ["IAM_p", "ang_p", "angina_p", "edema_p", "EA_p", "ECG_p", "CAP_p", "estado_p", "edad_p", "ER_p","IAM", "ang", "angina", "edema", "EA", "ECG", "CAP", "estado", "edad", "ER"]
        case "Lee":
            Object = Puntaje_Lee()
            List = ["OR_p", "isq_p", "cong_p", "CV_p", "diab_p", "Cr_p", "OR", "isq", "cong", "CV", "diab", "Cr"]
        case "Padua":
            Object = Puntaje_Padua()
            List = ["cancer_p", "TEV_p", "mov_p", "trombo_p", "OR_p", "edad_p", "falla_p", "IAM_p", "BMI_p", "TH_p", "cancer", "TEV", "mov", "trombo", "OR", "edad", "falla", "IAM", "BMI", "TH"]
        case _:
            return 0
    for x in List:
        var = type+"."+ x
        val = session.get(var)
        setattr(Object, x, val)
    return Object

# _.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.
# CONSTRUCTOR DE FLASH

app = Flask(__name__)
app.secret_key = '6b615dbef677bb488569e68c'
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
    fx.Find_IAM(f, Goldman, Detsky, Padua)
    fx.Find_JVD(f, Goldman)
    fx.Find_EA(f, Goldman,Detsky)
    fx.Find_ECG(f, Goldman,Detsky)
    fx.Find_CAP(f,Detsky)
    fx.Find_CVP(f,Goldman)
    fx.Find_estado(f, Goldman, Detsky, Padua)
    fx.Find_OR(f, Goldman, Lee)
    fx.Find_ER(f,Goldman, Detsky)
    fx.Find_isq(f, Lee)
    fx.Find_cong(f,Lee)
    fx.Find_CV(f,Lee)
    fx.Find_diab(f,Lee)
    fx.Find_Cr(f,Lee)
    fx.Find_ang(f,Detsky)
    fx.Find_angina(f,Detsky)
    fx.Find_edema(f,Detsky)
    fx.Find_cancer(f,Padua)
    fx.Find_TEV(f,Padua)
    fx.Find_trombo(f,Padua)
    fx.Find_trauma(f,Padua)
    fx.Find_falla(f,Padua)
    fx.Find_reuma(f,Padua)
    fx.Find_BMI(f,Padua)
    fx.Find_TH(f,Padua)
    MakeClass(Goldman,"G")
    MakeClass(Lee,"L")
    MakeClass(Detsky,"D")
    MakeClass(Padua,"P")
    empty = fx.FindEmpty(Goldman, Lee, Detsky, Padua) #Determinar si hay atributos vacios
    if empty == 1:
        return render_template('validar.html',Goldman=Goldman, Detsky=Detsky, Lee=Lee, Padua=Padua) #Si hay atributos vacios, redirigir a un form que pide los datos faltantes
    else:
        fx.AddTotal(Goldman, Detsky, Lee, Padua) #Hacer la suma final
        return render_template('print.html',Goldman=Goldman, Detsky=Detsky, Lee=Lee, Padua=Padua) #Si no hay atributos vacios, redirigir a una pagina que imprime los resultados

@app.route('/print', methods=['GET','POST'])
def print():
    Goldman = FindClass("Goldman") #Recuperar los objetos
    Detsky = FindClass("Detsky")
    Lee = FindClass("Lee")
    Padua = FindClass("Padua")
    form_data = request.form
    value = "No en el expediente. Seleccionado manualmente por el usuario"
    if Goldman.edad_p == -1: #Edad
        Goldman.edad = Detsky.edad = Padua.edad = value
        Goldman.edad_p = Detsky.edad_p = Padua.edad_p = form_data["Goldman_edad"]
        Padua.edad_p = int(int(Padua.edad_p)*(1/5))
    if Goldman.IAM_p == -1: #IAM
        Goldman.IAM = Detsky.IAM = value
        points = form_data["Goldman_IAM"]
        if points == 5: Detsky.IAM_p = points
        else: Goldman.IAM_p = Detsky.IAM_p = points
    if Goldman.JVD_p == -1: #JVD
            Goldman.JVD[0] = value
            Goldman.JVD_p = form_data["Goldman_JVD"]
    if Goldman.EA_p == -1: #EA
            Goldman.EA = Detsky.EA = value
            Goldman.EA_p = Detsky.EA_p = form_data["Goldman_EA"]
            Detsky.EA_p = int(int(Detsky.EA_p)*(20/3))
    if Goldman.ECG_p == -1: #ECG (Goldman)
            Goldman.ECG = value
            Goldman.ECG_p = form_data["Goldman_ECG"]
    if Detsky.ECG_p == -1: #ECG (Detsky)
            Detsky.ECG = value
            Detsky.ECG_p = form_data["Detsky_ECG"]
    if Goldman.CVP_p == -1: #CVP
            Goldman.CVP = value
            Goldman.CVP_p = form_data["Goldman_CVP"]
    if Goldman.estado_p == -1: #Estado general
        Goldman.estado = Detsky.estado = value
        Goldman.estado_p = Detsky.estado_p = form_data["Goldman_estado"]
        Detsky.estado_p = int(int(Detsky.estado_p)*(5/3))
    if Goldman.OR_p == -1: #Tipo de operación (Goldman)
        Goldman.OR = value
        Goldman.OR_p = form_data["Goldman_OR"]
    if Lee.OR_p == -1: #Tipo de operación (Lee)
        Lee.OR = value
        Lee.OR_p = form_data["Lee_OR"]
    if Goldman.ER_p == -1: #Cirugía de emergencia
        Goldman.ER = Detsky.ER = value
        Goldman.ER_p = Detsky.ER_p = form_data["Goldman_ER"]
        Detsky.ER_P = int(int(Detsky.ER_p)*(5/2))
    if Lee.isq_p == -1: #Enfermedad cardíaca isquémica
        Lee.isq = value
        Lee.isq_p = form_data["Lee_isq"]
    if Lee.cong_p == -1: #Enfermedad cardíaca congestiva
        Lee.cong = value
        Lee.cong_p = form_data["Lee_cong"]
    if Lee.CV_p == -1: #Enfermedad cerebrovascular
        Lee.CV = value
        Lee.CV_p = form_data["Lee_CV"]
    if Lee.diab_p == -1: #Insulina para diabéticos
        Lee.diab = value
        Lee.diab_p = form_data["Lee_diab"]
    if Lee.Cr_p == -1: #Creatinina preoperatoria
        Lee.Cr = value
        Lee.Cr_p = form_data["Lee_Cr"]
    if Detsky.ang_p == -1: #Angina de pecho
        Detsky.ang = value
        Detsky.ang_p = form_data["Detsky_ang"]
    if Detsky.angina_p == -1: #Angina inestable
        Detsky.angina = value
        Detsky.angina_p = form_data["Detsky_angina"]
    if Detsky.edema_p == -1: #Edema pulmonar
        Detsky.edema = value
        Detsky.edema_p = form_data["Detsky_edema"]
    if Detsky.CAP_p == -1: #CAP
        Detsky.CAP = value
        Detsky.CAP_p = form_data["Detsky_CAP"]
    if Padua.cancer_p == -1: #Cáncer
        Padua.cancer = value
        Padua.cancer_p = form_data["Padua_cancer"]
    if Padua.TEV_p == -1: #TEV
        Padua.TEV = value
        Padua.TEV_p = form_data["Padua_TEV"]
    if Padua.mov_p == -1: #Movilidad reducida
        Padua.mov = value
        Padua.mov_p = form_data["Padua_mov"]
    if Padua.trombo_p == -1: #Condición trombofília conocida
        Padua.trombo = value
        Padua.trombo_p = form_data["Padua_trombo"]
    if Padua.OR_p == -1: #Trauma reciente o cirugía
        Padua.OR = value
        Padua.OR_p = form_data["Padua_OR"]
    if Padua.falla_p == -1: #Falla cardíaca o respiratoria
        Padua.falla = value
        Padua.falla_p = form_data["Padua_falla"]
    if Padua.IAM_p == -1: #Desorden reumatológico agudo o infarto agudo de miocardio
        Padua.IAM = value
        Padua.IAM_p = form_data["Padua_IAM"]
    if Padua.BMI_p == -1: #Obesidad
        Padua.BMI = value
        Padua.BMI_p = form_data["Padua_BMI"]
    if Padua.TH_p == -1: #Tratamiento hormonal
        Padua.TH = value
        Padua.TH_p = form_data["Padua_TH"]
    fx.AddTotal(Goldman, Detsky, Lee, Padua) #Hacer la suma final
    return render_template('print.html',Goldman=Goldman, Detsky=Detsky, Lee=Lee, Padua=Padua)


#Funcion main driver
if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:5000") #Abrir la pagina principal en el navegador cuando se corre la app
    app.run()
    #ui.run()

#https://medium.com/@fareedkhandev/create-desktop-application-using-flask-framework-ee4386a583e9
