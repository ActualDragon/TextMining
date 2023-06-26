from flask import Flask, redirect, url_for, request, render_template, session, flash #Framework que permite crear aplicaciones web
from werkzeug.utils import secure_filename #validar el archivo
import os #usar funcionalidades dependientes del sistema operativo
import webbrowser #Manejar el navegador
from flaskwebgui import FlaskUI #Import the library that converts the flask web app to a desktop app
import functions as fx
from datetime import datetime

#CLASES
class Goldman_Index:
    edad = 0 #Valor encontrado [Edad]
    edad_p = -1 #Puntaje asignado segun el indice

    IAM = "" #Infarto agudo de miocardio
    IAM_p = -1

    JVD = [""] #Distención de la vena yugular o ruido cardíaco en S3
    JVD_p = -1

    EA = "" #Estenosis aórtica
    EA_p = -1

    ECG = "" #Ritmo distinto al sinusal o CAP (contracciones auriculares prematuras) en su último ECG
    ECG_p = -1

    CVP = "" #5 contracciones ventriculares prematuras / min documentadas en cualquier momento
    CVP_p = -1

    #PO2 (presión parcial de oxígeno) < 60 o PCO2 (presión parcial de dióxido de carbono) > 50 mm Hg, K (potasio) < 3.0 o HCO3 (bicarbonato) < 20 meq/litro,
    #BUN (nitrógeno ureico en sangre) > 50 o Cr (creatinina) > 3.0 mg/dl, SGOT (transaminasa glutámico-oxalacética) abnormal,
    #señales de enfermedad hepática crónica o paciente postrado por causas no-cardíacas
    estado = ""
    estado_p = -1

    OR = "" #Cirugia intraperitoneal, intratorácica o aórtica
    OR_p = -1

    ER = "" #Cirugia de emergencia
    ER_p = -1

    eval = ""
    percent = 0
    total = 0
    is_empty = 0

class Puntaje_Lee:
    OR = ""  #Cirugia de alto riesgo (intraperitoneal, intratorácica o suprainguinal vascular) [Valor encontrado]
    OR_p = -1 #Puntaje asignado segun el indice

    isq = "" #Historial de enfermedad cardíaca isquémica
    isq_p = -1

    cong = "" #Historial de enfermedad cardíaca congestiva
    cong_p = -1

    CV = "" #Historial de enfermedaad cerebrovascular
    CV_p = -1

    diab = "" #Terapia de insulina para diabéticos
    diab_p = -1

    Cr = "" #Creatinina preoperatoria > a 2 mg/dL (o > 177 micromol/L)
    Cr_p = -1

    eval = ""
    percent = 0
    total = 0
    is_empty = 0

class Detsky_Index:
    IAM = "" #Valor encontrado Infarto agudo de miocardio < o > 6 meses
    IAM_p = -1 #Puntaje asignado segun el indice

    ang = "" #Angina de pecho según la Sociedad Cardiovascular Canadiense -> Clase III o IV
    ang_p = -1

    angina = "" #Angina inestable < 3 meses
    angina_p = -1

    edema = "" #Edema pulmonar < 1 semana o cualquier otro momento
    edema_p = -1

    EA = "" #Estenosis aórtica crítica
    EA_p = -1

    ECG = "" #Ritmo distinto al sinusal o extrasístoles auriculares
    ECG_p = -1

    CAP = "" # >5 CAP (contracciones auriculares prematuras) / min documentados en cualquier momento
    CAP_p = -1

    #PO2 (presión parcial de oxígeno) < 60 o PCO2 (presión parcial de dióxido de carbono) > 50 mm Hg, K (potasio) < 3.0 o HCO3 (bicarbonato) < 20 meq/litro,
    #BUN (nitrógeno ureico en sangre) > 50 o Cr (creatinina) > 3.0 mg/dl, SGOT (transaminasa glutámico-oxalacética) abnormal,
    #señales de enfermedad hepática crónica o paciente postrado por causas no-cardíacas
    estado = ""
    estado_p = -1

    edad = 0  #Edad > 70
    edad_p = -1

    ER = "" #Cirugía de emergencia
    ER_p = -1

    total = 0
    is_empty = 0
    percent = 0
    eval = ""

class Puntaje_Padua:
    cancer = "" #Valor encontrado Cancer activo -> metástasis y/o han pasado por quimioterapia o radioterapia en los últimos 6 meses
    cancer_p = -1 #Puntaje asignado segun el indice

    TEV = "" #Tromboembolismo venoso (excluyendo trombosis venosa superficial)
    TEV_p = -1

    mov = "" #Movilidad reducida -> postrado con privilegios de baño (por incapacidad del paciente u órdenes del médico) por lo menos 3 días
    mov_p = -1

    #Condición trombofília conocida (defectos de antitrombina, proteína C o S, factor V Leiden, mutación de protrombina G20210A, síndrome antifosfolípido)
    trombo = ""
    trombo_p = -1

    OR = "" #Trauma reciente o cirugía <= 1 mes
    OR_p = -1

    edad = ""  #Edad > 70
    edad_p = -1

    falla = "" #Falla cardíaca y/o respiratoria
    falla_p = -1

    IAM = "" #Desorden reumatológico agudo o infarto agudo de miocardio
    IAM_p = -1

    BMI = "" #Obesidad (BMI >= 30)
    BMI_p = -1

    TH = "" #Tratammiento hormonal actual
    TH_p = -1

    total = 0
    is_empty = 0
    eval = ""

# _.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.

def MakeClass(type,Name): #Almacenar los objetos para poder accesarlos desde las diversas páginas
    atributos = [attr for attr in dir(type) if not callable(getattr(type, attr)) and not attr.startswith("__")]
    for atributo in atributos:
        var = Name+"."+f'{atributo}'
        valor = getattr(type, atributo)  # Obtener el valor del atributo
        session[var] = valor
    return 0

def FindClass(type): #Acceder a los objetos guardados
    match type:
        case "Goldman":
            Object = Goldman_Index()
            List = ["edad_p", "IAM_p", "JVD_p", "EA_p", "ECG_p", "CVP_p", "estado_p", "OR_p", "ER_p", "edad", "IAM", "JVD", "EA", "ECG", "CVP", "estado", "OR", "ER", "total", "is_empty", "eval", "percent"]
        case "Detsky":
            Object = Detsky_Index()
            List = ["IAM_p", "ang_p", "angina_p", "edema_p", "EA_p", "ECG_p", "CAP_p", "estado_p", "edad_p", "ER_p","IAM", "ang", "angina", "edema", "EA", "ECG", "CAP", "estado", "edad", "ER", "total", "is_empty", "eval", "percent"]
        case "Lee":
            Object = Puntaje_Lee()
            List = ["OR_p", "isq_p", "cong_p", "CV_p", "diab_p", "Cr_p", "OR", "isq", "cong", "CV", "diab", "Cr", "total", "is_empty", "eval"]
        case "Padua":
            Object = Puntaje_Padua()
            List = ["cancer_p", "TEV_p", "mov_p", "trombo_p", "OR_p", "edad_p", "falla_p", "IAM_p", "BMI_p", "TH_p", "cancer", "TEV", "mov", "trombo", "OR", "edad", "falla", "IAM", "BMI", "TH", "total", "is_empty", "eval", "percent"]
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
app.config['UPLOAD_EXTENSIONS'] = ['.doc', '.docx', '.DOC', '.DOCX'] #Extensiones permitidas

#Crear interfaz de usuario para la aplicacion de escritorio
ui = FlaskUI(app=app, server="flask", port=5000)

#Generar la home page
@app.route('/')
def instructions():
    return render_template('intro.html')

@app.route('/home')
def home():
    session.clear() #Eliminar sesiones anteriores
    #Eliminar todos las copias temporales de los expedientes que se hayan quedado almacenados si la aplicación no se cerró adecuadamente
    basedir = os.path.abspath(os.path.dirname(__file__)) #Obtener el directorio actual
    path = f"{basedir}\\static\\uploads" #Obtener el directorio de los archivos temporales

    filelist = [ f for f in os.listdir(path) if f.endswith(".doc") or f.endswith(".docx")] #Obtener los archivos
    for f in filelist:
        os.remove(os.path.join(path, f)) #Eliminar los archivos
    return render_template('index.html')

#Si se desea agregar un paciente nuevo
@app.route('/alta')
def alta():
    name = "Alta_paciente"
    return redirect(url_for('indices', name=name))

#Recibir el archivo subido
@app.route('/index', methods=['POST'])
def index():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename) #validar el nombre del archivo
    if filename != '': #validar que si se subió un archivo
        file_ext = os.path.splitext(filename)[1]
        #agregar validación de si no hay archivo
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != fx.validate_file(uploaded_file):
            flash('Por favor ingrese solamente un archivo .doc o .docx')
            return redirect(url_for('home'))
        basedir = os.path.abspath(os.path.dirname(__file__)) #Obtener el directorio actual
        uploaded_file.save(os.path.join(basedir,app.config['UPLOAD_PATH'], filename)) #Guardar una copia temporal del archivo subido
    return redirect(url_for('indices', name=filename))

@app.route('/indices/<name>')
def indices(name):
    Goldman = Goldman_Index()
    Lee = Puntaje_Lee()
    Detsky = Detsky_Index()
    Padua = Puntaje_Padua()
    if name == "Alta_paciente": #Si se van a registrar los datos de un paciente sin expediente
        text = ["Alta", "Paciente", "Nuevo"]
    else: #Si se subió un expediente
        text = fx.Read_File(name) #Leer los contenidos del archivo
    f = fx.Process_Text(text) #Procesar el texto
    fx.Find_Edad(f,Goldman,Detsky,Padua)
    fx.Find_IAM(f,text,Goldman,Detsky,Padua)
    fx.Find_JVD(f,text,Goldman)
    fx.Find_EA(f,text,Goldman,Detsky)
    fx.Find_ECG(f,text,Goldman,Detsky)
    fx.Find_CAP(f,text, Goldman,Detsky)
    fx.Find_CVP(f,text,Goldman)
    fx.Find_estado(f,text,Goldman,Detsky,Padua)
    fx.Find_OR(f,text,Goldman,Lee)
    fx.Find_ER(f,text,Goldman,Detsky)
    fx.Find_isq(f,text,Lee)
    fx.Find_cong(f,text,Lee)
    fx.Find_CV(f,text,Lee)
    fx.Find_diab(f,text,Lee)
    fx.Find_Cr(f,text,Lee)
    fx.Find_ang(f,text,Detsky)
    fx.Find_angina(f,text,Detsky)
    fx.Find_edema(f,text,Detsky)
    fx.Find_cancer(f,text,Padua)
    fx.Find_TEV(f,text,Padua)
    fx.Find_trombo(f,text,Padua)
    fx.Find_trauma(f,text,Padua, Goldman, Lee)
    fx.Find_falla(f,text,Padua)
    fx.Find_reuma(f,text,Padua)
    fx.Find_BMI(f,text,Padua)
    fx.Find_TH(f,text,Padua)
    MakeClass(Goldman,"Goldman")
    MakeClass(Lee,"Lee")
    MakeClass(Detsky,"Detsky")
    MakeClass(Padua,"Padua")
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
    if Goldman.edad_p == -1: #Edad
        Goldman.edad = Detsky.edad = Padua.edad = form_data["Goldman_edad"]
        if int(Goldman.edad) >= 70:
            Goldman.edad_p = Detsky.edad_p= 5
        else:
            Goldman.edad_p = Detsky.edad_p= 0
        Padua.edad_p = int(int(Goldman.edad_p)*(1/5))
    if Goldman.IAM_p == -1: #IAM
        points = form_data["Goldman_IAM"]
        match points:
            case "10":
                Goldman.IAM_p = Detsky.IAM_p = points
                Goldman.IAM = Detsky.IAM = "Paciente presentó un IAM hace menos de 6 meses."
            case "5":
                Detsky.IAM_p = points
                Goldman.IAM = Detsky.IAM = "Paciente presentó un IAM hace más de 6 meses."
            case _:
                Goldman.IAM_p = Detsky.IAM_p = points
                Goldman.IAM = Detsky.IAM = "Paciente no presentó un IAM."
    if Goldman.JVD_p == -1: #JVD
            Goldman.JVD_p = form_data["Goldman_JVD"]
            if Goldman.JVD_p == "11":
                Goldman.JVD = "Paciente presenta distensión de la vena yugular o ruido cardiaco en S3."
            else:
                Goldman.JVD = "Paciente no presenta distensión de la vena yugular o ruido cardiaco en S3."
    if Goldman.EA_p == -1: #EA
            Goldman.EA_p = Detsky.EA_p = form_data["Goldman_EA"]
            Detsky.EA_p = int(int(Detsky.EA_p)*(20/3))
            if Goldman.EA_p == "3":
                Goldman.EA = Detsky.EA = "Paciente presenta estenosis aórtica significativa."
            else:
                Goldman.EA = Detsky.EA = "Paciente no presenta estenosis aórtica significativa."
    if Goldman.ECG_p == -1: #ECG (Goldman)
            Goldman.ECG_p = form_data["Goldman_ECG"]
            if Goldman.ECG_p == "7":
                Goldman.ECG = "Paciente presenta ritmo distinto al sinusal o contracciones auriculares prematuras en su último ECG."
            else:
                Goldman.ECG = "Paciente no presenta ritmo distinto al sinusal o contracciones auriculares prematuras en su último ECG."
    if Detsky.ECG_p == -1: #ECG (Detsky)
            Detsky.ECG_p = form_data["Detsky_ECG"]
            if Detsky.ECG_p == "5":
                Detsky.ECG = "Paciente presenta ritmo distinto al sinusal o extrasístoles auriculares."
            else:
                Detsky.ECG = "Paciente no presenta ritmo distinto al sinusal o extrasístoles auriculares."
    if Goldman.CVP_p == -1: #CVP
            Goldman.CVP_p = form_data["Goldman_CVP"]
            if Goldman.CVP_p == "7":
                Goldman.CVP = "Paciente presenta más de 5 CVP's / min documentados en cualquier momento."
            else:
                Goldman.CVP = "Paciente no presenta más de 5 CVP's / min documentados en cualquier momento."
    if Goldman.estado_p == -1: #Estado general
        Goldman.estado_p = Detsky.estado_p = form_data["Goldman_estado"]
        Detsky.estado_p = int(int(Detsky.estado_p)*(5/3))
        if Goldman.estado_p == "3":
            Goldman.estado = Detsky.estado = "Paciente presenta pobre estado médico general"
        else:
            Goldman.estado = Detsky.estado = "Paciente no presenta pobre estado médico general"
        Goldman.estado = Goldman.estado + "(PO2 [presión parcial de oxígeno] < 60 o PCO2 [presión parcial de dióxido de carbono] > 50 mm Hg, K [potasio], < 3.0 o HCO3 [bicarbonato], > 20 meq/litro, BUN [nitrógeno ureico en sangre] > 50 o Cr [creatinina] > 3.0 mg/dl, SGOT [transaminasa glutámico-oxalacética] abnormal, señales de enfermedad hepática crónica o paciente postrado por causas no-cardíacas)."
    if Goldman.OR_p == -1: #Tipo de operación (Goldman)
        Goldman.OR_p = form_data["Goldman_OR"]
        if Goldman.OR_p == "3":
            Goldman.OR = "La cirugía es intraperitoneal o intratorácica o aórtica."
        else:
            Goldman.OR = "La cirugía no es intraperitoneal o intratorácica o aórtica."
    if Lee.OR_p == -1: #Tipo de operación (Lee)
        Lee.OR_p = form_data["Lee_OR"]
        if Lee.OR_p == "1":
            Lee.OR = "La cirugía es intraperitoneal, intratorácica o suprainguinal vascular."
        else:
            Lee.OR = "La cirugía no es intraperitoneal, intratorácica o suprainguinal vascular."
    if Goldman.ER_p == -1: #Cirugía de emergencia
        Goldman.ER_p = Detsky.ER_p = form_data["Goldman_ER"]
        Detsky.ER_P = int(int(Detsky.ER_p)*(5/2))
        if Goldman.ER_p == "4":
            Goldman.ER = Detsky.ER = "La cirugía es de emergencia."
        else:
            Goldman.ER = Detsky.ER = "La cirugía no es de emergencia."
    if Lee.isq_p == -1: #Enfermedad cardíaca isquémica
        Lee.isq_p = form_data["Lee_isq"]
        if Lee.isq_p == "1":
            Lee.isq = "El paciente presenta historial de enfermedad cardíaca isquémica."
        else:
            Lee.isq = "El paciente no presenta historial de enfermedad cardíaca isquémica."
    if Lee.cong_p == -1: #Enfermedad cardíaca congestiva
        Lee.cong_p = form_data["Lee_cong"]
        if Lee.cong_p == 1:
            Lee.cong = "El paciente presenta historial de enfermedad cardíaca congestiva."
        else:
            Lee.cong = "El paciente no presenta historial de enfermedad cardíaca congestiva."
    if Lee.CV_p == -1: #Enfermedad cerebrovascular
        Lee.CV_p = form_data["Lee_CV"]
        if Lee.CV_p == "1":
            Lee.CV = "El paciente presenta historial de enfermedad cerebrovascular."
        else:
            Lee.CV = "El paciente no presenta historial de enfermedad cerebrovascular."
    if Lee.diab_p == -1: #Insulina para diabéticos
        Lee.diab_p = form_data["Lee_diab"]
        if Lee.diab_p == "1":
            Lee.diab = "El paciente está en terapia de insulina para diabéticos."
        else:
            Lee.diab = "El paciente no está en terapia de insulina para diabéticos."
    if Lee.Cr_p == -1: #Creatinina preoperatoria
        Lee.Cr_p = form_data["Lee_Cr"]
        if Lee.Cr_p == "1":
            Lee.Cr = "El paciente presenta creatinina preoperatoria > a 2 mg/dL (o > 177 micromol/L)."
        else:
            Lee.Cr = "El paciente no presenta creatinina preoperatoria > a 2 mg/dL (o > 177 micromol/L)."
    if Detsky.ang_p == -1: #Angina de pecho
        Detsky.ang_p = form_data["Detsky_ang"]
        match Detsky.ang_p:
            case "10":
                Goldman.IAM = Detsky.IAM = "El paciente presenta angina Clase III."
            case "20":
                Goldman.IAM = Detsky.IAM = "El paciente presenta angina Clase IV."
            case _:
                Goldman.IAM = Detsky.IAM = "El paciente no presenta angina Clase III o IV."
    if Detsky.angina_p == -1: #Angina inestable
        Detsky.angina_p = form_data["Detsky_angina"]
        if Detsky.angina_p == "10":
            Detsky.angina = "El paciente presenta angina inestable desde hace menos de 3 meses."
        else:
            Detsky.angina = "El paciente no presenta angina inestable desde hace menos de 3 meses."
    if Detsky.edema_p == -1: #Edema pulmonar
        Detsky.edema_p = form_data["Detsky_edema"]
        match Detsky.edema_p:
            case "10":
                Goldman.IAM = Detsky.IAM = "El paciente presenta edema pulmonar desde hace menos de 1 semana."
            case "5":
                Goldman.IAM = Detsky.IAM = "El paciente presenta edema pulmonar desde hace más de 1 semana."
            case _:
                Goldman.IAM = Detsky.IAM = "El paciente no presenta edema pulmonar."
    if Detsky.CAP_p == -1: #CAP
        Detsky.CAP_p = form_data["Detsky_CAP"]
        if Detsky.CAP_p == "5":
            Detsky.CAP = "El paciente presenta > 5 CAP / min documentados en cualquier momento."
        else:
            Detsky.CAP = "El paciente no presenta > 5 CAP / min documentados en cualquier momento."
    if Padua.cancer_p == -1: #Cáncer
        Padua.cancer_p = form_data["Padua_cancer"]
        if Padua.cancer_p == "3":
            Padua.cancer = "El paciente presenta cáncer activo"
        else:
            Padua.cancer = "El paciente no presenta cáncer activo"
        Padua.cancer = Padua.cancer + "(Metástasis y/o ha pasado por quimioterapia o radioterapia en los últimos 6 meses)."
    if Padua.TEV_p == -1: #TEV
        Padua.TEV_p = form_data["Padua_TEV"]
        if Padua.TEV_p == "3":
            Padua.TEV = "El paciente presenta tromboembolismo venoso (excluyendo trombosis venosa superficial)."
        else:
            Padua.TEV = "El paciente no presenta tromboembolismo venoso (excluyendo trombosis venosa superficial)."
    if Padua.mov_p == -1: #Movilidad reducida
        Padua.mov_p = form_data["Padua_mov"]
        if Padua.mov_p == "3":
            Padua.mov = "El paciente presenta movilidad reducida"
        else:
            Padua.mov = "El paciente presenta movilidad reducida"
        Padua.mov = Padua.mov + "(Postrado con privilegios de baño [por incapacidad del paciente u órdenes del médico] por lo menos 3 días)."
    if Padua.trombo_p == -1: #Condición trombofília conocida
        Padua.trombo_p = form_data["Padua_trombo"]
        if Padua.trombo_p == "3":
            Padua.trombo = "El paciente presenta condición trombofília conocida"
        else:
            Padua.trombo = "El paciente no presenta condición trombofília conocida"
        Padua.trombo = Padua.trombo + "(Defectos de antitrombina, proteína C o S, factor V Leiden, mutación de protrombina G20210A, síndrome antifosfolípido)."
    if Padua.OR_p == -1: #Trauma reciente o cirugía
        Padua.OR_p = form_data["Padua_OR"]
        if Padua.OR_p == "2":
            Padua.OR = "El paciente ha tenido trauma o cirugía en el último mes."
        else:
            Padua.OR = "El paciente no ha tenido trauma o cirugía en el último mes."
    if Padua.falla_p == -1: #Falla cardíaca o respiratoria
        Padua.falla_p = form_data["Padua_falla"]
        if Padua.falla_p == "1":
            Padua.falla = "El paciente presenta falla cardíaca o respiratoria."
        else:
            Padua.falla = "El paciente no presenta falla cardíaca o respiratoria."
    if Padua.IAM_p == -1: #Desorden reumatológico agudo o infarto agudo de miocardio
        Padua.IAM_p = form_data["Padua_IAM"]
        if Padua.IAM_p == "1":
            Padua.IAM = "El paciente presenta desorden reumatológico agudo o IAM."
        else:
            Padua.IAM = "El paciente no presenta desorden reumatológico agudo o IAM."
    if Padua.BMI_p == -1: #Obesidad
        Padua.BMI_p = form_data["Padua_BMI"]
        if Padua.BMI_p == "1":
            Padua.BMI = "El paciente presenta obesidad."
        else:
            Padua.BMI = "El paciente no presenta obesidad."
    if Padua.TH_p == -1: #Tratamiento hormonal
        Padua.TH_p = form_data["Padua_TH"]
        if Padua.TH_p == "1":
            Padua.TH = "El paciente se encuentra en tratamiento hormonal."
        else:
            Padua.TH = "El paciente no se encuentra en tratamiento hormonal."
    fx.AddTotal(Goldman, Detsky, Lee, Padua) #Hacer la suma final
    #Cuando se vuelve a cargar la página después de guardar el archivo, mostrarle una alerta al usuario
    if session.get('archivo'):
        archivo = session.get('archivo')
        session.pop("archivo")
        if os.path.isfile(archivo):
            flash("Archivo Guardado Exitosamente!\nLo encontrarás en la carpeta \"Descargas\"")
    return render_template('print.html',Goldman=Goldman, Detsky=Detsky, Lee=Lee, Padua=Padua)

@app.route("/save", methods=['GET', 'POST'])
def save():
    nombre_file = request.args.get("nombre_file")
    nombre = request.args.get("nombre")
    filename = secure_filename(nombre_file+".doc")
    save_path = os.path.join(os.path.expanduser("~"),"Downloads")
    completeName = os.path.join(save_path, filename)
    dt = datetime.now()
    time = f'{dt:%d-%m-%Y}'

    Goldman_Point = request.args.get("Goldman_Point")
    Goldman_Eval = request.args.get("Goldman_Eval")
    Detsky_Point = request.args.get("Detsky_Point")
    Detsky_Eval = request.args.get("Detsky_Eval")
    Lee_Point = request.args.get("Lee_Point")
    Lee_Eval = request.args.get("Lee_Eval")
    Padua_Point = request.args.get("Padua_Point")
    Padua_Eval = request.args.get("Padua_Eval")

    content = f"""Expediente del paciente: {nombre}\nFecha de modificación: {time}
                \n\n1. Índice de Goldman:\n- Puntaje calculado: {Goldman_Point}\n- {Goldman_Eval}
                \n\n2. Índice de Detsky:\n- Puntaje calculado: {Detsky_Point}\n- {Detsky_Eval}
                \n\n3. Puntaje de Lee:\n- Puntaje calculado: {Lee_Point}\n- {Lee_Eval}
                \n\n4. Puntaje de Padua:\n- Puntaje calculado: {Padua_Point}\n- {Padua_Eval}"""

    file = open(completeName, "w+", encoding='utf-8')
    file.write(u'\ufeff')
    file.write(content)
    file.close()

    session['archivo'] = completeName

    return redirect(url_for('print'),code=307)

#Funcion main driver
if __name__ == '__main__':
    webbrowser.open_new("http://127.0.0.1:5000") #Abrir la pagina principal en el navegador cuando se corre la app
    app.run()
    #ui.run()

#https://medium.com/@fareedkhandev/create-desktop-application-using-flask-framework-ee4386a583e9
