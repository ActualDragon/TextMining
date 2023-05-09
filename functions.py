import filetype
import aspose.words as aw #Lectura de archivos
import spacy #Procesamiento de lenguaje natural
import os #usar funcionalidades dependientes del sistema operativo

nlp = spacy.load('es_core_news_sm') #Cargar el modelo en español de spaCy

class Search:
    Term = 0
    Line = -1

# _.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~"~._.~"~.
#FUNCIONES

#Validar que el archivo sea del tipo permitido (sin importar la extension que tenga)
def validate_file(file):
    header = file.read()
    file.seek(0)
    format = filetype.guess(header)
    if (format is None):
        return None
    format = format.extension
    if (format != "doc") and (format != "docx"):
        return None
    return '.' + format

#Leer la copia local del archivo que se subió
def Read_File(name):
    f = []
    parr = []
    text = []
    basedir = os.path.abspath(os.path.dirname(__file__)) #Obtener el directorio actual
    path = f"{basedir}\\static\\uploads\\{name}" #Obtener el directorio del archivo temporal
    doc = aw.Document(path) # Cargar el archivo a leer
    # Leer el contenido de los parrafos tipo nodo
    for paragraph in doc.get_child_nodes(aw.NodeType.PARAGRAPH, True) :
        paragraph = paragraph.as_paragraph()
        p = paragraph.to_string(aw.SaveFormat.TEXT)
        f.append(p)
    #Eliminar el texto adicional que agrega la libreria aspose.words
    size = len(f)
    for x in range(1,size-2):
        parr.append(f[x])
    #Separar los parrafos en oraciones
    for x in parr:
        sentences = x.split(". ")
        for i in sentences:
            i = i.lower()
            i = i.replace("\\", "/").replace('"','\\"').replace("'","\'") .replace("-"," ")#Escapar caracteres especiales
            i = i.replace('\n', '').replace('\r', '') #Eliminar saltos de linea y el retorno de carro
            i = i.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u") #Eliminar acentos para facilitar procesamiento
            text.append(i)
    return text

#Encontrar coincidencias en el texto
def Find_Syn(terms,f):
    IAM = Search()
    for i in range(len(terms)): #Ir recorriendo la lista de términos para buscar coincidencias en el texto
        for j in range(len(f)):
            doc = nlp(f[j]) #Procesar el texto con spacy
            filter = [token.text for token in doc if not token.is_stop or token.text == 'no'] #Quitar palabras vacías (de, por, en, la, etc) pero conservar "no"
            sentence = ' '.join(filter) #Reformar la oración sin las palabras vacías
            k = sentence.find(terms[i])
            if k != -1: #Si encuentra coincidencias, agregarla al objeto
                IAM.Term = f[j] #El término encontrado en el texto
                IAM.Line = j #Número de elemento de la lista
    return IAM

#Determinar cúando presentó la condición
def Find_Time(f,x):
    text = f[x.Line]
    doc = nlp(text) #Procesar el texto con spaCy
    # Extraer todas las palabras relacionadas con tiempo que sean sustantivos o adjetivos
    tiempos = [f"{doc[i-1].text} {token.text}" for i, token in enumerate(doc) if token.pos_ in ['NOUN', 'ADJ'] and ('dia' in token.text or 'dias' in token.text or 'semana' in token.text or 'semanas' in token.text or 'mes' in token.text or 'meses' in token.text or 'año' in token.text or 'años' in token.text)]
    if tiempos != []:
        return tiempos[0]
    return 0

#Encontrar la edad del paciente
def Find_Edad(f, Goldman, Detsky, Padua):
    j = ""; l = ""
    edad = []
    #De acuerdo con el analisis de la estructura de los expedientes, la edad siempre se encuentra antes del tag "ANTECEDENTES"
    for x in range(len(f)):
        i = f[x].find("antecedentes")
        if i != -1:
            j =  x #Encontrar el elemento de la lista donde empiezan los antecedentes (pues la edad va a estar antes)
    if j != "":
        for x in range(j):
            doc = nlp(f[x]) #Procesar el texto con spaCy
            # Extraer todas las palabras relacionadas con edad que sean sustantivos o adjetivos
            edad = [f"{doc[i-1].text}" for i, token in enumerate(doc) if token.pos_ in ['NOUN', 'ADJ'] and ('años' in token.text)]
    else:
        print("No hay antecedentes")
    if edad == []:
        edad.append(0)
    Goldman.edad = Detsky.edad = Padua.edad = edad[0]
    print("Edad: %s", edad[0])

    age = int(edad[0])
    if age != 0: #Validar se que encontro la edad
        if age > 70:
            Goldman.edad_p = Detsky.edad_p = 5 #Si el paciente tiene mas de 70 años se le agregan 5 puntos (1 en Padua)
            Padua.edad_p = 1
        else:
            Goldman.edad_p = Detsky.edad_p = Padua.edad_p = 0 #Si el paciente tiene 70 años o menos no se le agregan puntos
    return 0

#Encontrar la cantidad de sustancia en el paciente
def Find_Cant(term):
    term = str(term)
    cant = 0
    for i in term.split():
        try: #intentar convertir el token a float
            cant = float(i)
            break #salir del loop si i es la primera cadena que si es float
        except:
            continue
    print("Cantidad: " + str(cant)) #1.5
    return cant

#Determinar si ha habido infarto agudo de miocardio
def Find_IAM(f, Goldman, Detsky, Padua):
    terms = ['infarto agudo miocardio', ' im ', ' ima ', ' iam ', 'infarto cardiaco', 'ataque cardiaco', 'ataque corazon', 'infarto miocardio', 'infarto miocardico', 'sindrome isquemico coronario agudo', ' sica ', 'sindrome coronario agudo', 'evento coronario agudo', 'insuficiencia coronaria aguda', 'evento coronario isquemico agudo', 'necrosis miocardica aguda', 'crisis coronaria aguda', 'sindrome isquemia miocardica aguda', 'evento coronario isquemico agudo']
    text = Find_Syn(terms,f)
    print(text.Term)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Goldman.IAM = Detsky.IAM = Padua.IAM = text.Term
        Padua.IAM_p = 1
        time = Find_Time(f,text)
        if time != 0:
            i = time.split()
            match i[1]:
                case "meses":
                    if int(i[0]) <=6:
                        Goldman.IAM_p = Detsky.IAM_p = 10
                case "semanas":
                    if int(i[0]) <=24:
                        Goldman.IAM_p = Detsky.IAM_p = 10
                case "dias":
                    if int(i[0]) <=183:
                        Goldman.IAM_p = Detsky.IAM_p = 10
                case _:
                    Detsky.IAM_p = 5
                    Goldman.IAM_p = 0
        else:
            Detsky.IAM_p = 6
            Goldman.IAM_p = 0
    print("IAM: %s", text.Term)
    print("Detsky: %d", Detsky.IAM_p)
    return 0

#Determinar si hay distensión de la vena yugular o ruido cardíaco en S3
def Find_JVD(f, Goldman):
    terms1 = ['pletora yugular', 'ingurgitacion yugular', ' JVD ', 'distension vena yugular', 'distension yugular', 'pletora vena yugular', 'ingurgitacion vena yugular',  'signo de kussmaul', 'triada de beck', 'yugular prominente', 'aumento presion venosa yugular', 'vena yugular externa dilatada', 'yugular ingurgitada', 'turgencia vena yugular', 'turgencia yugular', 'reflujo hepatoyugular']
    terms2 = ['ruido cardiaco s3', 'roce pericardico s3', 'sonido cardiaco s3', 'tono cardiaco s3', 'galope protodiastolico', 'tercer ruido cardiaco', 'ruido cardiaco tercera fase', 'ruido llenado ventricular rapido', 'tercer componente ruido cardiaco','galope ventricular protodiastolico', 'sonido galope ventricular', 'ruido llenado protodiastolico', 'tercer ruido']
    text1 = Find_Syn(terms1,f)
    text2 = Find_Syn(terms2,f)
    if text1.Term != 0 or text2.Term != 0: #Determinar si se encontró una coincidencia
        if  text1.Term != 0:
            Goldman.JVD[0] = text1.Term
        if  text2.Term != 0:
            Goldman.JVD[1] = text2.Term
        Goldman.JVD_p = 11
    print("JVD: %s", text1.Term)
    print("RS3: %s", text2.Term)
    return 0

#Determinar si hay estenosis aórtica
def Find_EA(f, Goldman, Detsky):
    terms = ['valvulopatia aortica', 'estenosis valvular aortica', ' ea ', ' eao ', 'sorta estenotica', 'aortoestenosis', 'estenosis aorta', 'estenosis aortica', 'estenosis valvular aortica', 'obstruccion aortica']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Goldman.EA = Detsky.EA = text.Term
        Goldman.EA_p = 3
        Detsky.EA_p = 20
    print("EA: %s", text.Term)
    return 0

#Determinar si hay ritmo distinto del sinusal
def Find_ECG(f, Goldman, Detsky):
    terms1 =['ritmo no sinusal', 'taquiarritmia', 'taquicardia', 'flutter auricular', 'fibrilacion', 'bradicardia', 'bradiarritmia', 'paro sinusal', 'bloqueo sino-auricular', 'bloqueo sinoauricular', 'bloqueo sino auricular',  'bloqueo av', 'mobitz ', 'wenckebach', 'ritmo distinto sinusal', 'arritmia', 'ritmo cardiaco anormal', 'ritmo cardiaco no sinusal', 'bloqueo auriculoventricular', 'bloqueo de rama', 'ritmo de escape', 'extrasistoles']
    terms2 = ['contraccion auricular prematura', 'contracciones auriculares prematuras', 'latido auricular prematuro', 'sistole prematura', 'extrasistoles auriculares', ' cap ', 'arritmia auricular', 'ritmo auricular prematuro', 'complejo auricular prematuro', 'latidos prematuros auriculares', 'extrasistole auricular', 'palpitaciones auriculares', 'palpitacion auricular', 'arritmia auricular']
    terms3 = ['contraccion auricular prematura', 'contracciones auriculares prematuras', 'latido auricular prematuro', 'sistole prematura', 'extrasistoles auriculares', ' cap ', 'arritmia auricular']
    text1 = Find_Syn(terms1,f)
    text2 = Find_Syn(terms2,f)
    text3 = Find_Syn(terms3,f)
    if text1.Term != 0 or text2.Term != 0: #Determinar si se encontró ritmo no sinusal o extrasístoles auriculares
        if  text1.Term != 0:
            Detsky.ECG = text1.Term
        else:
            Detsky.ECG = text2.Term
        Detsky.ECG_p = 5
    if text1.Term != 0 or text3.Term != 0: #Determinar si se encontró ritmo distinto al sinusal
        if  text1.Term != 0:
            Goldman.ECG = text1.Term
        else:
            Goldman.ECG = text3.Term
        Goldman.ECG_p = 7
    print("ritmo sinusal: %s", text1.Term)
    print("extrasistoles: %s", text2.Term)
    print("CAP: %s", text3.Term)
    return 0

#Determinar si hay contracciones auriculares prematuras
def Find_CAP(f,Detsky):
    terms = ['contraccion auricular prematura', 'contracciones auriculares prematuras', 'latido auricular prematuro', 'sistole prematura', 'extrasistoles auriculares', ' cap ', 'arritmia auricular']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Detsky.CAP = text.Term
        x = Find_Cant(text.Term)
        if x >= 5: Detsky.CAP_p = 5
        else: Detsky.CAP_p = 0
    print("CAP 2: %s", text.Term)
    return 0

#Determinar si hay contracciones ventriculares prematuras
def Find_CVP(f,Goldman):
    terms = ['contraccion ventricular prematura', 'contracciones ventriculares prematuras', 'latido ventricular prematuro', 'extrasistoles ventriculares', 'arritmia ventricular']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Goldman.CVP = text.Term
        Goldman.CVP_p = 5
    print("CVP: %s", Goldman.CVP)
    return 0


#Determinar estado general
def Find_estado(f, Goldman, Detsky, Padua):

    #Encontrar el número en todos
    find = x = ""
    cant1 = cant3 = cant4 = cant5 = cant6 = cant7 = 0
    terms1 = ['pao2', 'presion parcial oxigeno', 'presion oxigeno', 'po2', 'presion arterial oxigeno', 'tension parcial oxigeno ', 'nivel oxigeno'] #Presión parcial de O2
    terms2 = ['cirrosis', 'fibrosis hepatica', 'esteatosis hepatica', 'hepatitis', 'hipertension portal', 'ascitis', 'hiperbilirrubinemia', 'hepatomegalia', 'elevacion transaminasas', 'pruebas funcion hepatica alteradas', 'varices esofagicas', 'cabeza medusa', 'caput medusae', 'tiempos coagulacion alterados', 'colangitis biliar', 'encefalopatia hepatica', 'elastografia hepatica', 'hepatopatia', 'ictericia', 'cancer higado', 'cancer hepatico','enfermedad hepatica', 'daño hepatico cronico',  'insuficiencia hepatica cronica', 'niveles elevados enzimas hepaticas', 'bilirrubina elevada', 'albumina baja', 'tiempo protrombina prolongado.', 'trombocitopenia', 'prurito', 'hepatomegalia'] #Enfermedad hepática
    terms3 = ['pco2', 'p co2', 'presion parcial co2', 'tension co2', 'presion parcial dioxido carbono', 'co2 parcial'] #Presion parcial de CO2
    terms4 = ['potasio serico', 'concentración potasio', 'niveles potasio', 'nivel potasio', 'kalemia', 'potasio plasmatico', 'K serico'] #Niveles de K
    terms5 = ['nivel bicarbonato sangre', 'bicarbonato serico', 'co2 serico', 'hco3 serico', 'concentracion bicarbonato sangre'] #Niveles de bicarbonato
    terms6 =  ['nitrogeno ureico sangre', ' bun ', 'urea sangre', 'azotemia', 'concentracion nitrogeno ureico', ' nus  '] #Nitrogeno ureico en sangre
    terms7 = ['creatinina sangre', 'creatinina serica', 'creatinina plasmatica', 'creatinina suero', 'concentracion creatinina', 'creatinina'] #Creatinina
    terms8 = ['transaminasa glutamico oxalacetica elevada', 'elevacion tgo', 'tgo alto', 'aspartato transaminasa alta', 'elevacion ast', 'ast elevada', 'niveles elevados tgo', 'aumento tgo', 'enzimas hepaticas elevadas', 'niveles elevados transaminasa glutamico oxalacetica', 'aumento transaminasa glutamico oxalacetica', 'transaminasa glutamico oxalacetica alta', 'valores elevados transaminasa glutamico oxalacetica', 'anormalidad transaminasa glutamico oxalacetica', 'niveles anormales transaminasa glutamico oxalacetica', 'transaminasa glutamico oxalacetica fuera rango', 'sgot anormal', 'sgot elevado'] #SGOT
    terms9 = ['postrada', 'inmovilizada', 'encamada', 'sedentaria', 'inactiva','postrado', 'inmovilizado', 'encamado', 'sedentario', 'inactivo' ] #Paciente postrado
    text1 = Find_Syn(terms1,f)
    if text1.Term != 0 :
        cant1 = Find_Cant(text1.Term)
        find = find + " " + str(cant1) + " " + str(text1.Term)
    text2 = Find_Syn(terms2,f)
    if text2.Term != 0: find = find + " " + str(text2.Term)
    text3 = Find_Syn(terms3,f)
    if text3.Term != 0 :
        cant3 = Find_Cant(text3.Term)
        find = find + " " + str(cant3) + " " + str(text3.Term)
    text4 = Find_Syn(terms4,f)
    if text4.Term != 0 :
        cant4 = Find_Cant(text4.Term)
        find = find + " " + str(cant4) + " " + str(text4.Term)
    text5 = Find_Syn(terms5,f)
    if text5.Term != 0 :
        cant5 = Find_Cant(text5.Term)
        find = find + " " + str(cant5) + " " + str(text5.Term)
    text6 = Find_Syn(terms6,f)
    if text6.Term != 0 :
        cant6 = Find_Cant(text6.Term)
        find = find + " " + str(cant6) + " " + str(text6.Term)
    text7 = Find_Syn(terms7,f)
    if text7.Term != 0 :
        cant7 = Find_Cant(text7.Term)
        find = find + " " + str(cant7) + " " + str(text7.Term)
    text8 = Find_Syn(terms8,f)
    if text8.Term != 0: find = find + " " + str(text8.Term)
    text9 = Find_Syn(terms9,f)
    if text9.Term != 0:
        find = find + " " + str(text9.Term)
        Padua.mov = text9.Term
        Padua.mov_p = 3
    if text1.Term !=0 or text2.Term !=0 or text3.Term !=0 or text4.Term !=0 or text5.Term !=0 or text6.Term !=0 or text7.Term !=0 or text8.Term !=0 or text9.Term !=0:
        Goldman.estado = Detsky.estado = find
        if cant1 <= 60 or text2.Term != 0 or cant3 > 50 or cant4 < 3 or cant5 < 20 or cant6 > 50 or cant7 >3 or text8.Term != 0 or text9.Term != 0: #Determinar si se encontró ritmo no sinusal o extrasístoles auriculares
            Goldman.estado_p = 3
            Detsky.estado_p = 5
    print("ritmo sinusal: %s", text1.Term)
    print("extrasistoles: %s", text2.Term)
    print("CAP: %s", text3.Term)
    return 0

#Determinar el tipo de cirugía
def Find_OR(f, Goldman, Lee):
    terms1 =['laparoscopia', 'laparotomia', 'laparotomia exploratoria', 'cirugia abierta de abdomen', 'colecistectomia', 'apendicectomia', 'reseccion intestinal', 'gastrectomia', 'hemicolectomia', 'cirugia intraperitoneal', 'cirugia abdomen', 'cirugia abdominal', 'reseccion intestinal', 'colectomia', 'gastrectomia', 'herniorrafia', 'histerectomia', 'ooforectomia', 'nefrectomia', 'quistectomia ovarica', 'esplenectomia', 'pancreatectomia'] #intraperitoneal
    terms2 = ['cirugia toracica', 'cirugia de torax', 'cirugia intratoracica', 'toracotomia', 'toracoscopia', 'reseccion pulmonar', 'lobectomia', 'neumonectomia', 'pleurectomia', 'pleurodesis', 'timectomia', 'mediastinoscopia', 'mediastinotomia', 'drenaje toracico', 'cirugia esofago toracico', 'cirugia pared toracica', 'cirugia aorta toracica'] #intratoracica
    terms3 = ['cirugia aortica', 'cirugia aorta', 'cirugia reemplazo aorta', 'cirugia aneurisma aortico', 'cirugia diseccion aortica', 'cirugia valvula aortica', 'cirugia raiz aortica', 'endoprotesis aortica', 'revascularizacion aortica', 'aneurismectomia', 'endarterectomia aortica', 'colocacion stent aortico', 'reparacion aorta', 'transposicion aortica', 'anastomosis aortica', 'arterioplastica aortica', 'bypass aortico'] #aortica
    terms4 =  ['cirugia suprainguinal vascular', 'cirugia vascular suprainguinal', 'revascularizacion femoral', 'bypass femoral', 'bypass iliaco femoral', 'bypass aortofemoral', 'bypass femoro popliteo', 'endarterectomima femoral', 'endarterectomia iliaca', 'angioplastia femoral', 'trombectomia femoral', 'arterioplastia femoral', 'arterioplastia iliaca', 'stent femoral', 'stent iliaco', 'diseccion aneurisma iliaco', 'diseccion aneurisma femoral', 'reseccion aneurisma iliaco', 'reseccion aneurisma femoral',' ligadura arterial femoral', 'ligadura arterial iliaca'] #suprainguinal vascular
    text1 = Find_Syn(terms1,f)
    text2 = Find_Syn(terms2,f)
    text3 = Find_Syn(terms3,f)
    text4 = Find_Syn(terms4,f)
    if text1.Term != 0 or text2.Term != 0 or text3.Term != 0: #Determinar si se encontró ritmo no sinusal o extrasístoles auriculares
        if  text1.Term != 0:
            Goldman.OR = text1.Term
        if  text2.Term != 0:
            Goldman.OR = text2.Term
        if  text3.Term != 0:
            Goldman.OR = text3.Term
        Goldman.OR_p = 3
    if text1.Term != 0 or text2.Term != 0 or text4.Term != 0: #Determinar si se encontró ritmo no sinusal o extrasístoles auriculares
        if  text1.Term != 0:
            Lee.OR = text1.Term
        if  text2.Term != 0:
            Lee.OR = text2.Term
        if  text4.Term != 0:
            Lee.OR = text3.Term
        Lee.OR_p = 1
    print("Intraperitoneal: %s", text1.Term)
    print("Intratoracica: %s", text2.Term)
    print("Aortica: %s", text3.Term)
    print("Suprainguinal: %s", text4.Term)
    return 0

#Determinar si la operacion es de emergencia
def Find_ER(f,Goldman, Detsky):
    terms = ['cirugia urgencia', 'cirugia emergencia', 'cirugia inmediata', 'cirugia rescate', 'cirugia critica', 'procedimiento salvamiento', 'pprocedimiento vital', 'intervencion emergencia', 'tratamiento quirurgico urgencia', 'tratamiento quirurgico emergencia', 'procedimiento quirurgico critico', 'intervencion urgencia', 'procedimiento de rescate', 'intervencion critica', 'tratamiento quirurgico vital', 'procedimiento quirurgico emergencia']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Goldman.ER = Detsky.ER = text.Term
        Goldman.ER_p = 4
        Detsky.ER_p = 10
    print("ER: %s", text.Term)
    return 0

#Determinar si hay algun criterio no encontrado
def FindEmpty(Goldman, Lee, Detsky, Padua):
    G_class = ["edad_p", "IAM_p", "JVD_p", "EA_p", "ECG_p", "CVP_p", "estado_p", "OR_p", "ER_p"]
    L_class = ["OR_p", "isq_p", "cong_p", "CV_p", "diab_p", "Cr_p"]
    D_class = ["IAM_p", "ang_p", "angina_p", "edema_p", "EA_p", "ECG_p", "CAP_p", "estado_p", "edad_p", "ER_p"]
    P_class = ["cancer_p", "TEV_p", "mov_p", "trombo_p", "OR_p", "edad_p", "falla_p", "IAM_p", "BMI_p", "TH_p"]
    n = 0

    #Validar si existe un atributo vacio
    for x in range(9):
        if getattr(Goldman,G_class[x]) == -1:
            n = n+1
            Goldman.is_empty = 1
    for x in range(6):
        if getattr(Lee,L_class[x]) == -1:
            n = n+1
            Lee.is_empty = 1
    for x in range(10):
        if getattr(Detsky,D_class[x]) == -1:
            n = n+1
            Detsky.is_empty = 1
    for x in range(10):
        if getattr(Padua,P_class[x]) == -1:
            n = n+1
            Padua.is_empty = 1
    if n != 0:
        return 1 #Algun campo se encuentra vacio
    else:
        return 0 #Ningun campo esta vacio

#Hacer la suma final
def AddTotal(Goldman, Detsky, Lee, Padua):
    G_class = ["edad_p", "IAM_p", "JVD_p", "EA_p", "ECG_p", "CVP_p", "estado_p", "OR_p", "ER_p"]
    L_class = ["OR_p", "isq_p", "cong_p", "CV_p", "diab_p", "Cr_p"]
    D_class = ["IAM_p", "ang_p", "angina_p", "edema_p", "EA_p", "ECG_p", "CAP_p", "estado_p", "edad_p", "ER_p"]
    P_class = ["cancer_p", "TEV_p", "mov_p", "trombo_p", "OR_p", "edad_p", "falla_p", "IAM_p", "BMI_p", "TH_p"]
    #Validar si existe un atributo vacio
    for x in G_class:
        val = getattr(Goldman,x)
        if val != -1:
           print("Val: " + x)
           print(val)
           Goldman.total = Goldman.total + int(val)
    if Goldman.total in range(0,5):
        Goldman.eval = "El paciente presenta un riesgo del 1% de presentar complicaciones"
    if Goldman.total in range(6,12):
        Goldman.eval = "El paciente presenta un riesgo del 7% de presentar complicaciones"
    if Goldman.total in range(13,25):
        Goldman.eval = "El paciente presenta un riesgo del 14% de presentar complicaciones"
    if Goldman.total in range(26,53):
        Goldman.eval = "El paciente presenta un riesgo del 28% de presentar complicaciones"
    val = 0
    for x in D_class:
        val = getattr(Detsky,x)
        print("Val: " + x)
        print(val)
        if val != -1:
           Detsky.total = Detsky.total + int(val)
    if Detsky.total in range(0,5):
        Detsky.eval = "El paciente presenta un riesgo del 6% de presentar complicaciones"
    if Detsky.total in range(6,12):
        Detsky.eval = "El paciente presenta un riesgo del 7% de presentar complicaciones"
    if Detsky.total in range(13,25):
        Detsky.eval = "El paciente presenta un riesgo del 20% de presentar complicaciones"
    if Detsky.total in range(26,85):
        Detsky.eval = "El paciente presenta un riesgo del 100% de presentar complicaciones"
    val = 0
    for x in L_class:
        val = getattr(Lee,x)
        if val != -1:
           Lee.total = Lee.total + int(val)
    if Lee.total == 0:
        Lee.eval = "El paciente presenta un riesgo del 0.4% de presentar complicaciones"
    if Lee.total == 1:
        Lee.eval = "El paciente presenta un riesgo del 0.9% de presentar complicaciones"
    if Lee.total == 2:
        Lee.eval = "El paciente presenta un riesgo del 6.6% de presentar complicaciones"
    if Lee.total >= 3:
        Lee.eval = "El paciente presenta un riesgo del 11% de presentar complicaciones"
    val = 0
    for x in P_class:
        val = getattr(Padua,x)
        if val != -1:
           Padua.total = Padua.total + int(val)
    if Padua.total >= 4:
        Padua.eval = "El paciente tiene un riesgo incrementado de tromboembolismo venoso"
    else:
        Padua.eval = "El paciente no tiene un riesgo incrementado de tromboembolismo venoso"
    return 0