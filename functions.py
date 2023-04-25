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
        p = p.replace("\\", "/").replace('"','\\"').replace("'","\'") #Escapar caracteres especiales
        p = p.replace('\n', '').replace('\r', '') #Eliminar saltos de linea y el retorno de carro
        p = p.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U") #Eliminar acentos para facilitar procesamiento
        f.append(p)
    #Eliminar el texto adicional que agrega la libreria aspose.words
    size = len(f)
    for x in range(1,size-2):
        parr.append(f[x])
    #Separar los parrafos en oraciones
    for x in parr:
        sentences = x.split(". ")
        for i in sentences:
            text.append(i.lower())
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
    Goldman.edad = edad
    Detsky.edad = edad
    Padua.edad = edad
    print("Edad: %s", edad)

    age = int(edad[0])
    if age != 0: #Validar se que encontro la edad
        if age > 70:
            Goldman.edad_p = 5 #Si el paciente tiene mas de 70 años se le agregan 5 puntos (1 en Padua)
            Detsky.edad_p = 5
            Padua.edad_p = 1
        else:
            Goldman.edad_p = 0 #Si el paciente tiene 70 años o menos no se le agregan puntos
            Detsky.edad_p = 0
            Padua.edad_p = 0
    return 0

#Determinar si ha habido infarto agudo de miocardio
def Find_IAM(f, Goldman, Detsky):
    terms = ['infarto agudo miocardio', ' im ', ' ima ', ' iam ', 'infarto cardiaco', 'ataque cardiaco', 'ataque corazon', 'infarto miocardio', 'infarto miocardico', 'sindrome isquemico coronario agudo', ' sica ', 'sindrome coronario agudo', 'evento coronario agudo', 'insuficiencia coronaria aguda', 'evento coronario isquemico agudo', 'necrosis miocardica aguda', 'crisis coronaria aguda', 'sindrome isquemia miocardica aguda', 'evento coronario isquemico agudo']
    text = Find_Syn(terms,f)
    print(text.Term)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Goldman.IAM = text.Term
        Detsky.IAM = text.Term
        time = Find_Time(f,text)
        if time != 0:
            i = time.split()
            match i[1]:
                case "meses":
                    if int(i[0]) <=6:
                        Goldman.IAM_p = 10
                        Detsky.IAM_p = 10
                case "semanas":
                    if int(i[0]) <=24:
                        Goldman.IAM_p = 10
                        Detsky.IAM_p = 10
                case "dias":
                    if int(i[0]) <=183:
                        Goldman.IAM_p = 10
                        Detsky.IAM_p = 10
                case _:
                    Detsky.IAM_p = 5
                    Goldman.IAM_p = 0
        else:
            Detsky.IAM_p = 0
            Goldman.IAM_p = 0
    print("IAM: %s", text.Term)
    return 0

#Determinar si hay distensión de la vena yugular
def Find_JVD(f, Goldman):
    terms = ['pletora yugular', 'ingurgitacion yugular', ' JVD ', 'distension vena yugular', 'distension yugular', 'pletora vena yugular', 'ingurgitacion vena yugular',  'signo de kussmaul', 'triada de beck', 'yugular prominente', 'aumento presion venosa yugular', 'vena yugular externa dilatada', 'yugular ingurgitada', 'turgencia vena yugular', 'turgencia yugular', 'reflujo hepatoyugular']
    text = Find_Syn(terms,f)
    print(text.Term)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Goldman.JVD = text.Term
        Goldman.JVD_p = 11
    print("JVD: %s", text.Term)
    return 0

#Determinar si hay algun criterio no encontrado
def FindEmpty(Goldman, Lee, Detsky, Padua):
    G_class = ["edad_p", "IAM_p", "JVD_p", "RS3_p", "EA_p", "ECG_p", "CVP_p", "estado_p", "OR_p"]
    L_class = ["OR_p", "isq_p", "cong_p", "CV_p", "diab_p", "Cr_p"]
    D_class = ["IAM_p", "ang_p", "angina_p", "edema_p", "EA_p", "ECG_p", "CAP_p", "estado_p", "edad_p", "ER_p"]
    P_class = ["cancer_p", "TEV_p", "mov_p", "trombo_p", "OR_p", "edad_p", "falla_p", "IAM_p", "BMI_p", "TH_p"]
    n = 0

    #Validar si existe un atributo vacio
    for x in range(8):
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