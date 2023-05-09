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
            i = i.replace("meses", "mes").replace("dias", "dia").replace("semanas", "semana").replace("años", "año")
            text.append(i)
    return text

#Encontrar coincidencias en el texto
def Find_Syn(terms, f):
    IAM = Search()
    for j, text in enumerate(f): #Ir recorriendo la lista de términos para buscar coincidencias en el texto
        doc = nlp(text) #Procesar el texto con spacy
        filter = [token.text for token in doc if not token.is_stop or token.text == 'no'] #Quitar palabras vacías (de, por, en, la, etc) pero conservar "no"
        sentence = ' '.join(filter) #Reformar la oración sin las palabras vacías
        for i, term in enumerate(terms):
            if term in sentence: #Si encuentra coincidencias, agregarla al objeto
                IAM.Term = text #El término encontrado en el texto
                IAM.Line = j #Número de elemento de la lista
                break

    return IAM

#Determinar cúando presentó la condición
def Find_Time(f,x):
    text = f[x.Line]
    doc = nlp(text) #Procesar el texto con spaCy
    # Extraer todas las palabras relacionadas con tiempo que sean sustantivos o adjetivos
    tiempos = [f"{doc[i-1].text} {token.text}" for i, token in enumerate(doc) if token.pos_ in ['NOUN', 'ADJ'] and ('dia' in token.text or 'semana' in token.text or 'mes' in token.text or 'año' in token.text)]
    if tiempos:
        return tiempos[0]
    return 0

#Encontrar la edad del paciente
def Find_Edad(f, Goldman, Detsky, Padua):
    edad = []
    #De acuerdo con el analisis de la estructura de los expedientes, la edad siempre se encuentra antes del tag "ANTECEDENTES"
    j = next((x for x, item in enumerate(f) if "antecedentes" in item), None)
    if j is not None: #Encontrar el elemento de la lista donde empiezan los antecedentes (pues la edad va a estar antes)
        for x in range(j):
            doc = nlp(f[x])#Procesar el texto con spaCy
            edad = [f"{doc[i-1].text}" for i, token in enumerate(doc) if token.pos_ in ['NOUN', 'ADJ'] and ('año' in token.text)]# Extraer la edad
    if not edad:
        print("No hay antecedentes")
        edad.append(0)
    Goldman.edad = Detsky.edad = Padua.edad = edad[0]
    print("Edad: %s" % edad[0])
    age = int(edad[0])
    if age != 0:
        if age > 70: #Si el paciente tiene mas de 70 años se le agregan 5 puntos (1 en Padua)
            Goldman.edad_p = Detsky.edad_p = 5
            Padua.edad_p = 1
        else: #Si el paciente tiene 70 años o menos no se le agregan puntos
            Goldman.edad_p = Detsky.edad_p = Padua.edad_p = 0
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
    print("Cantidad: " + str(cant))
    return cant

#Determinar si ha habido infarto agudo de miocardio
def Find_IAM(f, Goldman, Detsky, Padua):
    terms = ['infarto agudo miocardio', ' im ', ' ima ', ' iam ', 'infarto cardiaco', 'ataque cardiaco', 'ataque corazon', 'infarto miocardio', 'infarto miocardico', 'sindrome isquemico coronario agudo', ' sica ', 'sindrome coronario agudo', 'evento coronario agudo', 'insuficiencia coronaria aguda', 'evento coronario isquemico agudo', 'necrosis miocardica aguda', 'crisis coronaria aguda', 'sindrome isquemia miocardica aguda', 'evento coronario isquemico agudo']
    text = Find_Syn(terms, f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Goldman.IAM = Detsky.IAM = Padua.IAM = text.Term
        Padua.IAM_p = 1
        time = Find_Time(f, text)
        if time != 0:
            i = time.split()
            duration = int(i[0])
            unit = i[1]
            if unit == "mes" and duration <= 6:
                Goldman.IAM_p = Detsky.IAM_p = 10
            elif unit == "semana" and duration <= 24:
                Goldman.IAM_p = Detsky.IAM_p = 10
            elif unit == "dia" and duration <= 183:
                Goldman.IAM_p = Detsky.IAM_p = 10
            else:
                Detsky.IAM_p = 5
                Goldman.IAM_p = 0
        else:
            Detsky.IAM_p = 6
            Goldman.IAM_p = 0
    print("IAM: %s" % text.Term)
    print("Detsky: %d" % Detsky.IAM_p)
    return 0


#Determinar si hay distensión de la vena yugular o ruido cardíaco en S3
def Find_JVD(f, Goldman):
    terms1 = ['pletora yugular', 'ingurgitacion yugular', ' JVD ', 'distension vena yugular', 'distension yugular', 'pletora vena yugular', 'ingurgitacion vena yugular',  'signo de kussmaul', 'triada de beck', 'yugular prominente', 'aumento presion venosa yugular', 'vena yugular externa dilatada', 'yugular ingurgitada', 'turgencia vena yugular', 'turgencia yugular', 'reflujo hepatoyugular']
    terms2 = ['ruido cardiaco s3', 'roce pericardico s3', 'sonido cardiaco s3', 'tono cardiaco s3', 'galope protodiastolico', 'tercer ruido cardiaco', 'ruido cardiaco tercera fase', 'ruido llenado ventricular rapido', 'tercer componente ruido cardiaco','galope ventricular protodiastolico', 'sonido galope ventricular', 'ruido llenado protodiastolico', 'tercer ruido']
    text1 = Find_Syn(terms1, f)
    text2 = Find_Syn(terms2, f)
    if text1.Term != 0 or text2.Term != 0: #Determinar si se encontró una coincidencia
        Goldman.JVD[0] = text1.Term
        Goldman.JVD[1] = text2.Term
        Goldman.JVD_p = 11
    print("JVD: %s" % text1.Term)
    print("RS3: %s" % text2.Term)
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
    terms1 = ['ritmo no sinusal', 'taquiarritmia', 'taquicardia', 'flutter auricular', 'fibrilacion', 'bradicardia', 'bradiarritmia', 'paro sinusal', 'bloqueo sino-auricular', 'bloqueo sinoauricular', 'bloqueo sino auricular', 'bloqueo av', 'mobitz ', 'wenckebach', 'ritmo distinto sinusal', 'arritmia', 'ritmo cardiaco anormal', 'ritmo cardiaco no sinusal', 'bloqueo auriculoventricular', 'bloqueo de rama', 'ritmo de escape', 'extrasistoles']
    terms2 = ['contraccion auricular prematura', 'contracciones auriculares prematuras', 'latido auricular prematuro', 'sistole prematura', 'extrasistoles auriculares', ' cap ', 'arritmia auricular', 'ritmo auricular prematuro', 'complejo auricular prematuro', 'latidos prematuros auriculares', 'extrasistole auricular', 'palpitaciones auriculares', 'palpitacion auricular', 'arritmia auricular']
    text1 = Find_Syn(terms1, f)
    text2 = Find_Syn(terms2, f)
    if text1.Term != 0 or text2.Term != 0:
        if text1.Term != 0:
            Detsky.ECG = text1.Term
        else:
            Detsky.ECG = text2.Term
        Detsky.ECG_p = 5
        Goldman.ECG_p = 7
    if text1.Term != 0:
        Goldman.ECG = text1.Term
    elif text2.Term != 0:
        Goldman.ECG = text2.Term
    print("ritmo sinusal:", text1.Term)
    print("extrasistoles:", text2.Term)
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
        x = Find_Cant(text.Term)
        if x >= 5: #Determinar si ha habido >5 CVP/min
            Goldman.CVP = text.Term
            Goldman.CVP_p = 5
    print("CVP: %s", Goldman.CVP)
    return 0


#Determinar estado general
def Find_estado(f, Goldman, Detsky, Padua):
    find = ""
    terms1 = ['pao2', 'presion parcial oxigeno', 'presion oxigeno', 'po2', 'presion arterial oxigeno', 'tension parcial oxigeno ', 'nivel oxigeno'] #Presión parcial de O2
    terms2 = ['cirrosis', 'fibrosis hepatica', 'esteatosis hepatica', 'hepatitis', 'hipertension portal', 'ascitis', 'hiperbilirrubinemia', 'hepatomegalia', 'elevacion transaminasas', 'pruebas funcion hepatica alteradas', 'varices esofagicas', 'cabeza medusa', 'caput medusae', 'tiempos coagulacion alterados', 'colangitis biliar', 'encefalopatia hepatica', 'elastografia hepatica', 'hepatopatia', 'ictericia', 'cancer higado', 'cancer hepatico','enfermedad hepatica', 'daño hepatico cronico',  'insuficiencia hepatica cronica', 'niveles elevados enzimas hepaticas', 'bilirrubina elevada', 'albumina baja', 'tiempo protrombina prolongado.', 'trombocitopenia', 'prurito', 'hepatomegalia'] #Enfermedad hepática
    terms3 = ['pco2', 'p co2', 'presion parcial co2', 'tension co2', 'presion parcial dioxido carbono', 'co2 parcial'] #Presion parcial de CO2
    terms4 = ['potasio serico', 'concentración potasio', 'niveles potasio', 'nivel potasio', 'kalemia', 'potasio plasmatico', 'K serico'] #Niveles de K
    terms5 = ['nivel bicarbonato sangre', 'bicarbonato serico', 'co2 serico', 'hco3 serico', 'concentracion bicarbonato sangre'] #Niveles de bicarbonato
    terms6 =  ['nitrogeno ureico sangre', ' bun ', 'urea sangre', 'azotemia', 'concentracion nitrogeno ureico', ' nus  '] #Nitrogeno ureico en sangre
    terms7 = ['creatinina sangre', 'creatinina serica', 'creatinina plasmatica', 'creatinina suero', 'concentracion creatinina', 'creatinina'] #Creatinina
    terms8 = ['transaminasa glutamico oxalacetica elevada', 'elevacion tgo', 'tgo alto', 'aspartato transaminasa alta', 'elevacion ast', 'ast elevada', 'niveles elevados tgo', 'aumento tgo', 'enzimas hepaticas elevadas', 'niveles elevados transaminasa glutamico oxalacetica', 'aumento transaminasa glutamico oxalacetica', 'transaminasa glutamico oxalacetica alta', 'valores elevados transaminasa glutamico oxalacetica', 'anormalidad transaminasa glutamico oxalacetica', 'niveles anormales transaminasa glutamico oxalacetica', 'transaminasa glutamico oxalacetica fuera rango', 'sgot anormal', 'sgot elevado'] #SGOT
    terms9 = ['postrada', 'inmovilizada', 'encamada', 'sedentaria', 'inactiva','postrado', 'inmovilizado', 'encamado', 'sedentario', 'inactivo' ] #Paciente postrado
    text_terms = [Find_Syn(terms, f) for terms in [terms1, terms2, terms3, terms4, terms5, terms6, terms7, terms8, terms9]]
    cant_terms = [0] * 7
    for i, text in enumerate(text_terms[:7]):
        if text.Term != 0:
            cant_terms[i] = Find_Cant(text.Term)
            find += f" {cant_terms[i]} {text.Term}"
    text8 = text_terms[7]
    text9 = text_terms[8]
    if text8.Term != 0:
        find += f" {text8.Term}"
    if text9.Term != 0:
        find += f" {text9.Term}"
        Padua.mov = text9.Term
        Padua.mov_p = 3
    if any(text.Term != 0 for text in text_terms):
        Goldman.estado = Detsky.estado = find
        if cant_terms[0] <= 60 or text_terms[1].Term != 0 or cant_terms[2] > 50 or cant_terms[3] < 3 or cant_terms[4] < 20 or cant_terms[5] > 50 or cant_terms[6] > 3 or text8.Term != 0 or text9.Term != 0:
            Goldman.estado_p = 3
            Detsky.estado_p = 5
    print("estado:", Goldman.estado)
    return 0

#Determinar el tipo de cirugía
def Find_OR(f, Goldman, Lee):
    terms = {
        'intraperitoneal': ['laparoscopia', 'laparotomia', 'laparotomia exploratoria', 'cirugia abierta de abdomen', 'colecistectomia', 'apendicectomia', 'reseccion intestinal', 'gastrectomia', 'hemicolectomia', 'cirugia intraperitoneal', 'cirugia abdomen', 'cirugia abdominal', 'reseccion intestinal', 'colectomia', 'gastrectomia', 'herniorrafia', 'histerectomia', 'ooforectomia', 'nefrectomia', 'quistectomia ovarica', 'esplenectomia', 'pancreatectomia'],
        'intratoracica': ['cirugia toracica', 'cirugia de torax', 'cirugia intratoracica', 'toracotomia', 'toracoscopia', 'reseccion pulmonar', 'lobectomia', 'neumonectomia', 'pleurectomia', 'pleurodesis', 'timectomia', 'mediastinoscopia', 'mediastinotomia', 'drenaje toracico', 'cirugia esofago toracico', 'cirugia pared toracica', 'cirugia aorta toracica'],
        'aortica': ['cirugia aortica', 'cirugia aorta', 'cirugia reemplazo aorta', 'cirugia aneurisma aortico', 'cirugia diseccion aortica', 'cirugia valvula aortica', 'cirugia raiz aortica', 'endoprotesis aortica', 'revascularizacion aortica', 'aneurismectomia', 'endarterectomia aortica', 'colocacion stent aortico', 'reparacion aorta', 'transposicion aortica', 'anastomosis aortica', 'arterioplastica aortica', 'bypass aortico'],
        'suprainguinal': ['cirugia suprainguinal vascular', 'cirugia vascular suprainguinal', 'revascularizacion femoral', 'bypass femoral', 'bypass iliaco femoral', 'bypass aortofemoral', 'bypass femoro popliteo', 'endarterectomima femoral', 'endarterectomia iliaca', 'angioplastia femoral', 'trombectomia femoral', 'arterioplastia femoral', 'arterioplastia iliaca', 'stent femoral', 'stent iliaco', 'diseccion aneurisma iliaco', 'diseccion aneurisma femoral', 'reseccion aneurisma iliaco', 'reseccion aneurisma femoral',' ligadura arterial femoral', 'ligadura arterial iliaca']
    }
    text = {}
    for key, value in terms.items():
        text[key] = Find_Syn(value, f)
    if text['intraperitoneal'].Term != 0 or text['intratoracica'].Term != 0 or text['aortica'].Term != 0: #Determinar si se encontró ritmo no sinusal o extrasístoles auriculares
        if  text['intraperitoneal'].Term != 0:
            Goldman.OR = text['intraperitoneal'].Term
        if  text['intratoracica'].Term != 0:
            Goldman.OR = text['intratoracica'].Term
        if  text['aortica'].Term != 0:
            Goldman.OR = text['aortica'].Term
        Goldman.OR_p = 3
    if text['intraperitoneal'].Term != 0 or text['intratoracica'].Term != 0 or text['suprainguinal'].Term != 0: #Determinar si se encontró ritmo no sinusal o extrasístoles auriculares
        if  text['intraperitoneal'].Term != 0:
            Lee.OR = text['intraperitoneal'].Term
        if  text['intratoracica'].Term != 0:
            Lee.OR = text['intratoracica'].Term
        if  text['suprainguinal'].Term != 0:
            Lee.OR = text['suprainguinal'].Term
        Lee.OR_p = 1
    print("Intraperitoneal: %s", text['intraperitoneal'].Term)
    print("Intratoracica: %s", text['intratoracica'].Term)
    print("Aortica: %s", text['aortica'].Term)
    print("Suprainguinal: %s", text['suprainguinal'].Term)
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

#Determinar historial de enfermedad cardíaca isquémica
def Find_isq(f,Lee):
    terms = ['enfermedad coronaria', 'angina de pecho', 'infarto de miocardio', 'sindrome coronario agudo', 'cardiopatia isquemica', 'cardiopatia coronaria', 'arteriopatia coronaria', 'isquemia miocardica', 'isquemia cardiaca', 'isquemia coronaria', 'enfermedad cardiaca isquemica']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Lee.isq = text.Term
        Lee.isq_p = 1
    print("isq: %s", text.Term)
    return 0

#Determinar historial de insuficiencia cardíaca congestiva
def Find_cong(f,Lee):
    terms =  ['enfermedad cardiaca congestiva', 'insuficiencia cardiaca', 'insuficiencia cardiaca congestiva', 'insuficiencia ventricular', 'insuficiencia ventricular izquierda', 'insuficiencia ventricular derecha', 'cardiopatia congestiva', 'insuficiencia cardiaca cronica', 'insuficiencia cardiaca aguda', 'insuficiencia cardiaca aguda descompensada', '  icc ']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Lee.cong = text.Term
        Lee.cong_p = 1
    print("cong: %s", text.Term)
    return 0

#Determinar historial de enfermedad cerebrovascular
def Find_CV(f,Lee):
    terms = ['enfermedad cerebrovascular', 'accidente cerebrovascular', ' ictus ', 'derrame cerebral', 'infarto cerebral', 'embolia cerebral', 'hemorragia cerebral', 'apoplejia', 'ataque cerebral', 'isquemia cerebral', 'accidente isquemico transitorio', ' acv ', ' evc ', 'evc isquemico', 'evc hemorragico', 'hemorragia subaracnoidea', 'evento cerebral vascular']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Lee.CV = text.Term
        Lee.CV_p = 1
    print("CV: %s", text.Term)
    return 0

#Determinar si hay terapia de insulina para diabetes
def Find_diab(f,Lee):
    terms = ['insulina accion rapida', 'insulina accion ultra rapida', 'insulina accion intermedia', 'insulina accion prolongada', 'insulina glargina', 'insulina detemir', 'insulina nph', 'insulina aspart', 'insulina glulisina', 'insulina lispro', 'terapia insulina', 'insulina', 'tratamiento insulina', 'insulina diabetes', 'insulina diabeticos', 'terapia insulinodependiente', 'tratamiento insulinodependiente', 'tratamiento diabetes tipo 1', 'diabetes insulinodependiente', 'diabetes tipo 1']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Lee.diab = text.Term
        Lee.diab_p = 1
    print("Diab: %s", text.Term)
    return 0

#Determinar creatinina preoperatoria
def Find_Cr(f,Lee):
    terms = ['creatinina preoperatoria', 'creatinina previa cirugia', 'creatinina preoperatoria tomada', 'creatinina preoperatoria realizada', 'evaluacion creatinina preoperatoria']
    unit1 = ['mg/dl', 'mg / dl', 'miligramos decilitro']
    unit2 = ['micromol/l', 'micromolar', 'micromol litro']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        x = Find_Cant(text.Term)
        for i in unit1:  # Determinar la cantidad de creatinina en mg/dL
            if i in text.Term and x >= 2:
                Lee.Cr = text.Term
                Lee.Cr_p = 1
                break
        for i in unit2:  # Determinar la cantidad de creatinina en micromol/L
            if i in text.Term and x >= 177:
                Lee.Cr = text.Term
                Lee.Cr_p = 1
                break
    print("Cr: %s", text.Term)
    return 0

#Determinar angina segun la Sociedad Cardiovascular Canadiense
def Find_ang(f,Detsky):
    terms1 = ['marcada limitacion actividad fisica ordinaria', 'limitacion significativa actividad fisica habitual', 'restriccion notable actividad fisica diaria', 'limitacion pronunciada actividad fisica rutinaria', 'dificultad marcada actividad fisica ordinaria', 'clase iii', 'clase 3', 'dificultad subir escaleras',  'problemas caminar distancias cortas', 'dificultad caminar ritmo normal']
    terms2 = ['incapacidad actividad fisica molestias', 'limitacion realizar actividad fisica', 'dificultad ejercer actividad fisica molestias', 'molestia realizar actividad fisica', 'imposibilidad actividad fisica molestias', 'angina reposo', 'sindrome isquemico coronario agudo reposo', ' sica reposo', 'dolor toracico reposo', 'angina pecho reposo', 'dolor pecho reposo', 'clase iv', 'clase 4']
    text1 = Find_Syn(terms1, f)
    text2 = Find_Syn(terms2, f)
    if text1.Term != 0:
        Detsky.ang = text1.Term
        Detsky.ang_p = 10
    if text2.Term != 0:
        Detsky.ang = text2.Term
        Detsky.ang_p = 20
    print("Angina canadidense: %s", Detsky.ang)
    return 0

#Determinar angina inestable
def Find_angina(f,Detsky):
    terms = ['sindrome isquemico coronario agudo', 'sica', 'dolor toracico opresivo', 'angina inestable', 'dolor toracico inestable', 'dolor precordial inestable', 'sindrome coronario agudo sin elevacion st ', 'insuficiencia coronaria aguda', 'angor inestable']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Detsky.angina = text.Term
        Detsky.angina_p = 10
    print("Angina inestable: %s", text.Term)
    return 0

#Determinar edema pulmonar
def Find_edema(f,Detsky):
    terms = ['edema pulmonar', 'insuficiencia respiratoria aguda', 'congestion pulmonar', 'edema agudo pulmon', 'sindrome dificultad respiratoria aguda', ' sdra ']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Detsky.edema = text.Term
        Detsky.edema_p = 5
        x = Find_Cant(text.Term)
        if ("semana" in text.Term and x <= 1) or ("dia" in text.Term and x <= 8): #Determinar si el edema ocurrió hace menos de una semana
            Detsky.edema_p = 10
    print("Edema: %s", text.Term)
    return 0

#Determinar cáncer activo
def Find_cancer(f,Padua):
    terms = ['cancer activo', 'tumor maligno', 'neoplasia', 'cancer', 'enfermedad neoplasica', 'enfermedad oncologica', 'radioterapia', 'terapia radiacion', 'tratamiento radiante', 'irradiacion', 'terapia radiante', 'radiacion terapeutica', 'metastasis', 'metastasizado', 'diseminacion metastasica', 'propagacion metastasica']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Padua.cancer = text.Term
        Padua.cancer_p = 3
    print("Cancer: %s", text.Term)
    return 0

#Determinar TEV
def Find_TEV(f,Padua):
    terms = ['trombosis venosa profunda', 'tromboembolia pulmonar', ' tvp ', ' tep ', 'tromboembolismo venoso', ' tev ', 'trombosis venosa profunda', 'embolia pulmonar']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Padua.TEV = text.Term
        Padua.TEV_p = 3
    print("TEV: %s", text.Term)
    return 0

#Determinar condición trombofilia conocida
def Find_trombo(f,Padua):
    terms = ['trombosis venosa profunda', 'tromboembolia pulmonar', ' tvp ', ' tep ', 'tromboembolismo venoso', ' tev ', 'trombosis venosa profunda', 'embolia pulmonar']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Padua.trombo = text.Term
        Padua.trombo_p = 3
    print("Trombo: %s", text.Term)
    return 0

#Determinar trauma reciente o cirugía
def Find_trauma(f,Padua):
    terms = ['trauma', 'lesion', 'accidente', 'herida', 'evento traumatico', 'cirugia', 'intervencion quirurgica', 'procedimiento quirurgico', 'operacion', 'acto quirurgico', 'intervencion operatoria', 'procedimiento operatorio']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        x = Find_Cant(text.Term)
        if ("semana" in text.Term and x <= 4) or ("dia" in text.Term and x <= 31) or ("mes" in text.Term and x <= 1) or ("una semana" in text.Term): #Determinar si el edema ocurrió hace menos de una semana
            Padua.OR = text.Term
            Padua.OR_p = 2
    print("Trauma: %s", text.Term)
    return 0

#Determinar falla respiratoria o cardíaca
def Find_falla(f,Padua):
    terms = ['falla cardiaca', 'insuficiencia cardiaca', 'insuficiencia ventricular', 'insuficiencia ventricular', 'disfuncion ventricular', 'falla ventricular', 'cardiopatia congestiva', 'disfuncion sistolica', 'insuficiencia respiratoria', 'hipercarbia', 'hipercapnia', 'hipoxemia', 'hipoxia', 'insuficiencia respiratoria', 'fracaso respiratorio', 'dificultad respiratoria', 'alteracion respiratoria', 'falla pulmonar', 'insuficiencia pulmonar', 'falla respiratoria', 'disnea']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Padua.falla = text.Term
        Padua.falla_p = 1
    print("Falla: %s", text.Term)
    return 0

#Determinar desorder reumatologico
def Find_reuma(f,Padua):
    terms = ['artritis reumatoide aguda', 'lupus eritematoso sistemico agudo', 'esclerodermia aguda', 'polimiositis aguda', 'dermatomiositis aguda', 'sindrome Sjogren agudo', 'desorden reumatologico agudo']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Padua.IAM = text.Term
        Padua.IAM_p = 1
    print("Reuma: %s", text.Term)
    return 0

#Determinar obesidad
def Find_BMI(f,Padua):
    terms = ['obesidad', 'sobrepeso', 'indice masa corporal elevado', 'adiposidad', 'exceso grasa corporal', 'hiperadiposidad', 'hiperplasia adiposa', 'sindrome metabolico', 'exceso peso', 'peso elevado', ' bmi ', ' imc ', 'indice masa corporal']
    unit1 = [' bmi ', ' imc ', 'indice masa corporal']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Padua.BMI = text.Term
        Padua.BMI_p = 1
        for i in unit1:  # Determinar la cantidad de creatinina en mg/dL
            if i in text.Term:
                x = Find_Cant(text.Term)
                if x < 30:
                    Padua.BMI_p = 0
                break
    print("BMI: %s", text.Term)
    return 0

#Determinar terapia hormonal
def Find_TH(f,Padua):
    terms = ['tratamiento hormonal', 'terapia hormonal', 'hormonoterapia', 'tratamiento hormonas', 'terapia hormonas', 'terapia hormona', 'tratamiento hormona']
    text = Find_Syn(terms,f)
    if text.Term != 0: #Determinar si se encontró una coincidencia
        Padua.TH = text.Term
        Padua.TH_p = 1
    print("TH: %s", text.Term)
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

    Goldman.total = sum(int(getattr(Goldman, x)) for x in G_class if getattr(Goldman, x) != -1)
    Detsky.total = sum(int(getattr(Detsky, x)) for x in D_class if getattr(Detsky, x) != -1)
    Lee.total = sum(int(getattr(Lee, x)) for x in L_class if getattr(Lee, x) != -1)
    Padua.total = sum(int(getattr(Padua, x)) for x in P_class if getattr(Padua, x) != -1)

    if 0 <= Goldman.total <= 5:
        Goldman.eval = "El paciente presenta un riesgo del 1% de presentar complicaciones"
    elif 6 <= Goldman.total <= 11:
        Goldman.eval = "El paciente presenta un riesgo del 7% de presentar complicaciones"
    elif 12 <= Goldman.total <= 24:
        Goldman.eval = "El paciente presenta un riesgo del 14% de presentar complicaciones"
    elif 25 <= Goldman.total <= 52:
        Goldman.eval = "El paciente presenta un riesgo del 28% de presentar complicaciones"

    if 0 <= Detsky.total <= 5:
        Detsky.eval = "El paciente presenta un riesgo del 6% de presentar complicaciones"
    elif 6 <= Detsky.total <= 11:
        Detsky.eval = "El paciente presenta un riesgo del 7% de presentar complicaciones"
    elif 12 <= Detsky.total <= 24:
        Detsky.eval = "El paciente presenta un riesgo del 20% de presentar complicaciones"
    elif 25 <= Detsky.total <= 100:
        Detsky.eval = "El paciente presenta un riesgo del 100% de presentar complicaciones"

    if Lee.total == 0:
        Lee.eval = "El paciente presenta un riesgo del 0.4% de presentar complicaciones"
    elif Lee.total == 1:
        Lee.eval = "El paciente presenta un riesgo del 0.9% de presentar complicaciones"
    elif Lee.total == 2:
        Lee.eval = "El paciente presenta un riesgo del 6.6% de presentar complicaciones"
    elif Lee.total >= 3:
        Lee.eval = "El paciente presenta un riesgo del 11% de presentar complicaciones"

    if Padua.total >= 4:
        Padua.eval = "El paciente tiene un riesgo incrementado de tromboembolismo venoso"
    else:
        Padua.eval = "El paciente no tiene un riesgo incrementado de tromboembolismo venoso"
    return 0