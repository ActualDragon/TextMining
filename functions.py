import filetype
import aspose.words as aw #Lectura de archivos
import spacy #Procesamiento de lenguaje natural
import os #usar funcionalidades dependientes del sistema operativo

nlp = spacy.load('es_core_news_sm') #Cargar el modelo en español de spaCy
nlp.Defaults.stop_words -= {"sin", "dia", "dias", "hoy"} #Conservar algunas palabras vacías necesarias para el procesamiento
stopwords = nlp.Defaults.stop_words

class Search:
    Term = "0"
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
            i = i.replace("\\", "/").replace('"','\\"').replace("'","\'").replace("-"," ")#Escapar caracteres especiales
            i = i.replace('\n', '').replace('\r', '') #Eliminar saltos de linea y el retorno de carro
            i = i.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u") #Eliminar acentos para facilitar procesamiento
            text.append(i)
    return text

#Procesar el txto
def Process_Text(text):
    lemma_sentences = []  # Utilizamos un conjunto para evitar duplicados
    for sentence in text:
        doc = nlp(sentence)#Procesar el texto con spacy
        lemma_sentence = ' '.join(token.lemma_ for token in doc if (token.lemma_ not in stopwords and token.lemma_ != "de" and token.lemma_ != "el")) #Quitar palabras vacías (de, por, en, la, etc) y pasar la palabra a su forma básica (sin congujar)
        lemma_sentence = lemma_sentence.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("-"," ") #Eliminar acentos para facilitar procesamiento
        lemma_sentences.append(lemma_sentence)
    f = lemma_sentences  # Convertimos el conjunto a lista
    print(f)
    return f

#Encontrar coincidencias en el texto
def Find_Syn(terms, f):
    IAM = Search()
    for j, text in enumerate(f): #Ir recorriendo la lista de términos para buscar coincidencias en el texto
        for term in terms:
            if term in text: #Si encuentra coincidencias, agregarla al objeto
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
    j = next((x for x, item in enumerate(f) if "antecedente" in item), None)
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

#Las funciones Find_ contienen un arreglo llamado "terms" o "terms1", "terms2", etc.
#En estos arreglos se encuentran los "diccionarios" de posibles formas en las que podemos encontrar los criterioss en el expediente
#Puede parecer que estos tienen errores ortográficos o de sintaxis, pero es porque pasaron por el mismo proceso de tokenización, procesamiento y lemmatización que el expediente para incrementar la probabilidad de encontrar una coincidencia

#Determinar si ha habido infarto agudo de miocardio
def Find_IAM(f, og, Goldman, Detsky, Padua):
    terms =[' ima ', 'sindromar isquemico coronario agudo', 'sindromar coronario agudo', 'insuficiencia coronario agudo', 'crisis coronario agudo', 'necrosis miocardico agudo', 'evento coronario agudo', 'ataque corazon', ' sica ', 'infarto cardiaco', 'sindromar isquemio miocardico agudo', ' iam ', 'evento coronario isquemico agudo', 'ataque cardiaco', 'infarto miocardico', 'infarto miocardio', 'infarto agudo miocardio', ' im ']
    text = Find_Syn(terms, f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Goldman.IAM = Detsky.IAM = Padua.IAM = og[text.Line]
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
    print("IAM: %s" % Padua.IAM)
    return 0


#Determinar si hay distensión de la vena yugular o ruido cardíaco en S3
def Find_JVD(f, og, Goldman):
    terms1 = ['ingurgitacion vena yugular', 'aumento presion venós yugular', 'pletoro yugular', 'distension vena yugular', 'distension yugular', 'signo de kussmaul', 'reflujo hepatoyugular', 'turgencia yugular', 'vena yugular externo dilatado', 'turgencia vena yugular', 'yugular prominente', 'pletoro vena yugular', ' JVD ', 'yugular ingurgitado', 'triado de beck', 'ingurgitacion yugular']
    terms2 = ['ruido cardiaco s3', 'sonido cardiaco s3', 'rocir pericardico s3', 'galope ventricular protodiastolico', 'galope protodiastolico', 'ruido llenado protodiastolico', ' s3 ', 'tercer ruido', 'tercer ruido cardiaco', 'tono cardiaco s3', 'ruido cardiaco tercero fase', 'sonido galope ventricular', 'ruido llenado ventricular rapido', 'tercer componente ruido cardiaco', 'soplo']
    text1 = Find_Syn(terms1, f)
    text2 = Find_Syn(terms2, f)
    if text1.Term != "0": #Determinar si se encontró una coincidencia
        Goldman.JVD = og[text1.Line]
        Goldman.JVD_p = 11
    elif text2.Term != "0":
        Goldman.JVD = og[text2.Line]
        Goldman.JVD_p = 11
    if " sin " in text1.Term or " sin " in text2.Term:
        Goldman.JVD_p = 0
    print("JVD: %s" % Goldman.JVD)
    return 0


#Determinar si hay estenosis aórtica
def Find_EA(f, og, Goldman, Detsky):
    terms = ['estenosis aorto', 'sortar estenotico', 'valvulopatia aortico', '  eao', 'estenosis valvular aortico', 'estenosis aortico', 'aortoestenosis', 'obstruccion aortico', ' ear ',]
    text = Find_Syn(terms,f)
    if text.Term != "0" : #Determinar si se encontró una coincidencia
        Goldman.EA = Detsky.EA = og[text.Line]
        if " sin " in text.Term:
            Goldman.EA_p = Detsky.EA_p = 0
        else:
            Goldman.EA_p = 3
            Detsky.EA_p = 20
    print("EA: %s", Goldman.EA)
    return 0

#Determinar si hay ritmo distinto del sinusal o extrasistoles auriculares
def Find_ECG(f, og, Goldman, Detsky):
    terms1 = ['wenckebach', 'flutter auricular', 'arritmia', 'ritmo no sinusal', 'bloqueo av', 'bloqueo de rama', 'ritmo de escape', 'paro sinusal', 'bloqueo sino auricular', 'fibrilacion', 'ritmo cardiaco no sinusal', 'taquiarritmia', 'bradicardio', 'bloqueo sino-auricular', 'bloqueo sinoauricular', 'bradiarritmio', 'ritmo cardiaco anormal', 'taquicardio', 'mobitz', 'ritmo distinto sinusal', 'extrasistol', 'bloqueo auriculoventricular']
    terms2 = ['contraccion auricular prematuro', 'latido auricular prematuro', '  cap', 'arritmia auricular', 'contraccion auriculares prematuro', 'ritmo auricular prematuro', 'palpitacion auricular', 'extrasistol auricular', 'extrasisto el auricular', 'sisto el prematura', 'complejo auricular prematuro', 'latido prematuro auricular']
    antiterm = ['ritmo cardiaco regular', 'ritmo cardíaco regular sinusal', 'ritmo regular sinusal', 'ritmo sinusal regular', 'ritmo regular cardiaco sinusal', 'ritmo cardiaco normal', 'ritmo cardiaco sinusal normal', 'ritmo sinusal normal']
    text1 = Find_Syn(terms1, f)
    text2 = Find_Syn(terms2, f)
    antitext = Find_Syn(antiterm, f)
    if text1.Term != "0" or text2.Term != "0":
        if text1.Term != "0":
            Goldman.ECG = Detsky.ECG = og[text1.Line]
            Detsky.ECG_p = 5
            Goldman.ECG_p = 7
        if text2.Term != "0":
            Detsky.ECG = og[text2.Line]
            Detsky.ECG_p = 5
    elif antitext.Term != "0":
            Goldman.ECG = Detsky.ECG = og[antitext.Line]
            Detsky.ECG_p = Goldman.ECG_p = 0
    print("ritmo sinusal:", Goldman.ECG)
    print("extrasistoles:", Detsky.ECG)
    return 0

#Determinar si hay contracciones auriculares prematuras
def Find_CAP(f,og,Goldman,Detsky):
    terms = ['contraccion auricular prematuro', 'contraccion auriculares prematuro', '  cap', 'sisto el prematura', 'arritmia auricular', 'latido auricular prematuro', 'extrasistol auricular']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Detsky.CAP = Goldman.ECG = og[text.Line]
        Goldman.ECG_p = 7
        x = Find_Cant(text.Term)
        if x >= 5: Detsky.CAP_p = 5
        else: Detsky.CAP_p = 0
    if " sin " in text.Term:
        Goldman.ECG = Detsky.CAP_p = 0
    print("CAP 2: %s", Detsky.CAP)
    return 0

#Determinar si hay contracciones ventriculares prematuras
def Find_CVP(f,og,Goldman):
    terms = ['contraccion ventricular prematuro', 'contraccion ventricular prematura', 'arritmio ventricular', 'latido ventricular prematuro', 'extrasistol ventricular']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        if " sin " in text.Term:
            Goldman.CVP_p = 0
        else:
            Goldman.CVP = og[text.Line]
            x = Find_Cant(text.Term)
            if x >= 5: #Determinar si ha habido >5 CVP/min
                Goldman.CVP_p = 5
    print("CVP: %s", Goldman.CVP)
    return 0


#Determinar estado general
def Find_estado(f, og, Goldman, Detsky, Padua):
    find = ""
    terms1 = ['presion arterial oxigeno', 'presion oxigeno', 'tension parcial oxigeno', 'presion parcial oxigeno', 'nivel oxigeno', ' pao2 ', ' po2 '] #Presión parcial de O2
    terms2 = ['cancer hepatico', 'daño hepatico cronico', 'prurito', 'insuficiencia hepatico cronico', 'prueba funcion hepatico alterado', 'colangitis biliar', 'cabeza medusar', 'elastografia hepatico', 'esteatosis hepatico', 'hiperbilirrubinemiar', 'variz esofagica', 'elevacion transaminasas', 'enfermedad hepatico', 'fibrosis hepatico', 'caput medusae', 'bilirrubin elevado', 'encefalopatia hepatico', 'trombocitopenia', 'cirrosis', 'asciti', 'nivel elevado enzima hepatica', 'tiempo coagulacion alterado', 'hepatomegalia', 'ictericia', 'hepatopatia', 'hepatitis', 'cancer higado', 'hipertension portal', 'albuminar bajo', 'tiempo protrombinar prolongado'] #Enfermedad hepática
    terms3 = ['presion parcial co2', 'p co2', 'tension co2', 'presion parcial dioxido carbono', 'co2 parcial', 'pco2', 'hipocarbiar', 'hipocapneo', 'hipocapnia'] #Presion parcial de CO2
    terms4 = ['concentracion potasio', 'potasio serico', 'kalemia', 'k serico', 'nivel potasio', 'potasio plasmatico'] #Niveles de K
    terms5 = ['hco3 serico', 'nivel bicarbonato sangre', 'bicarbonato serico', 'concentracion bicarbonato sangre', 'co2 serico'] #Niveles de bicarbonato
    terms6 = [' nus ', 'nitrogeno ureico sangre', 'urea sangre', '  bun', 'concentracion nitrogeno ureico', 'azotemiar'] #Nitrogeno ureico en sangre
    terms7 = ['creatinina serico', 'creatinina plasmatico', 'concentracion creatinin', 'creatininar', 'creatinina sangre', 'creatinina suero'] #Creatinina
    terms8 = ['elevacion tgo', 'nivel anormal transaminasar glutamico oxalacetico', 'tgo alto', 'enzima hepatica elevado', 'ast elevado', 'nivel elevado transaminasa glutamico oxalacetico', 'transaminasa glutamico oxalacetico alto', 'anormalidad transaminas glutamico oxalacetico', 'sgot elevado', 'elevacion ast', 'aumento transaminasa glutamico oxalacetico', 'aspartato transaminasa alto', 'transaminasa glutamico oxalacetico elevado', 'aumento tgo', 'sgot anormal', 'nivel elevado tgo', 'valor elevado transaminasa glutamico oxalacetico', 'transaminasa glutamico oxalacetico ser rango'] #SGOT
    terms9 = ['inactivo', 'encamado', 'postrado', 'inmovilizado', 'reposo'] #Paciente postrado
    text_terms = [Find_Syn(terms, f) for terms in [terms1, terms2, terms3, terms4, terms5, terms6, terms7, terms8, terms9]]
    cant_terms = [0] * 9
    for i, text in enumerate(text_terms):
        if text.Term != "0":
            find += f" {og[text.Line]}"
            cant_terms[i] = Find_Cant(text.Term)
    if text_terms[8].Term != "0":
        Padua.mov = og[text_terms[8].Line]
        Padua.mov_p = 3
    Goldman.estado = Detsky.estado = find
    if cant_terms[0] <= 60 or text_terms[1].Term != "0" or cant_terms[2] > 50 or cant_terms[3] < 3 or cant_terms[4] < 20 or cant_terms[5] > 50 or cant_terms[6] > 3 or text_terms[7].Term != "0" or text_terms[8].Term != "0":
        Goldman.estado_p = 3
        Detsky.estado_p = 5
    print("estado:", Goldman.estado)
    return 0

#Determinar el tipo de cirugía
def Find_OR(f, og, Goldman, Lee):
    terms1 =['cirugia abdominal', 'pancreatectomia', 'nefrectomia', 'quistectomia ovarico', 'hemicolectomia', 'gastrectomiar', 'laparotomia exploratorio', 'cirugia abdomen', 'apendicectomio', 'histerectomiar', 'reseccion intestinal', 'colectomia', 'cirugia abierto abdomen', 'ooforectomio', 'herniorrafia', 'esplenectomia', 'laparotomiar', 'cirugia intraperitoneal', 'laparoscopio', 'colecistectomio'] #intraperitoneal
    terms2 = ['cirugia aorto toracico', 'cirugia toracico', 'timectomia', 'mediastinotomia', 'neumonectomia', 'drenaje toracico', 'lobectomia', 'pleurectomiar', 'toracoscopia', 'cirugia pared toracico', 'pleurodesis', 'cirugia esofago toracico', 'cirugia intratoracico', 'mediastinoscopia', 'cirugia torax', 'reseccion pulmonar', 'toracotomia'] #intratoracica
    terms3 = ['endoprotesis aortico', 'endarterectomia aortico', 'colocacion stent aortico', 'revascularizacion aortico', 'transposicion aortico', 'arterioplastico aortico', 'cirugia aorto', 'reparacion aorto', 'cirugia valvula aortico', 'cirugia raiz aortico', 'anastomosis aortico', 'aneurismectomia', 'cirugia aortico', 'cirugia diseccion aortico', 'cirugia aneurismo aortico', 'cirugia reemplazo aorto', 'bypass aortico'] #aortica
    terms4 = ['revascularizacion femoral', 'angioplastia femoral', 'bypass femoral', 'reseccion aneurisma femoral', 'bypass femoro popliteo', 'stent iliaco', 'bypass iliaco femoral', 'diseccion aneurismo femoral', 'arterioplastia iliaca', 'reseccion aneurisma iliaco', 'stent femoral', 'trombectomia femoral', 'arterioplastia femoral', 'bypass aortofemoral', 'cirugia suprainguinal vascular', 'cirugia vascular suprainguinal', 'endarterectomia iliaco', 'endarterectomimo femoral', 'ligadura arterial femoral', 'diseccion aneurismo iliaco', 'ligadura arterial iliaco'] #suprainguinal vascular
    text1 = Find_Syn(terms1,f)
    text2 = Find_Syn(terms2,f)
    text3 = Find_Syn(terms3,f)
    text4 = Find_Syn(terms4,f)
    if text1.Term != "0" or text2.Term != "0": #Determinar si se encontró ritmo no sinusal o extrasístoles auriculares
        if  text1.Term != "0":
            Goldman.OR = Lee.OR = og[text1.Line]
        if  text2.Term != "0":
            Goldman.OR = Lee.OR = og[text2.Line]
        Goldman.OR_p = 3
        Lee.OR_p = 1
    elif text3.Term != "0": #Determinar si se encontró ritmo no sinusal o extrasístoles auriculares
        Goldman.OR = og[text3.Line]
        Goldman.OR_p = 3
    elif text4.Term != "0": #Determinar si se encontró ritmo no sinusal o extrasístoles auriculares
        Lee.OR = og[text4.Line]
        Lee.OR_p = 1
    print("Intraperitoneal: %s", og[text1.Line])
    print("Intratoracica: %s", og[text2.Line])
    print("Aortica: %s", og[text3.Line])
    print("Suprainguinal: %s", og[text4.Line])
    return 0

#Determinar si la operacion es de emergencia
def Find_ER(f,og,Goldman, Detsky):
    terms = ['procedimiento quirurgico critico', 'intervencion emergencia', 'cirugia criticar', 'tratamiento quirurgico vital', 'tratamiento quirurgico emergencia', 'cirugia emergencia', 'pprocedimiento vital', 'intervencion urgencia', 'procedimiento rescate', 'cirugia rescate', 'cirugia inmediato', 'procedimiento quirurgico emergencia', 'cirugia urgencia', 'tratamiento quirurgico urgencia', 'intervencion criticar', 'procedimiento salvamiento']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Goldman.ER = Detsky.ER = og[text.Line]
        Goldman.ER_p = 4
        Detsky.ER_p = 10
    print("ER: %s", Goldman.ER)
    return 0

#Determinar historial de enfermedad cardíaca isquémica
def Find_isq(f,og,Lee):
    terms = ['infarto miocardio', 'cardiopatia coronario', 'arteriopatia coronario', 'enfermedad coronario', 'isquemio coronario', 'sindromar coronario agudo', 'angin pecho', 'enfermedad cardiaco isquemico', 'isquemiar miocardica', 'cardiopatia isquemico', 'isquemio cardiaco']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Lee.isq = og[text.Line]
        Lee.isq_p = 1
    print("isq: %s", Lee.isq)
    return 0

#Determinar historial de insuficiencia cardíaca congestiva
def Find_cong(f,og,Lee):
    terms = ['enfermedad cardiaca congestiva', 'insuficiencia cardiaco', 'insuficiencia cardiaca congestiva', 'insuficiencia ventricular', 'insuficiencia ventricular izquierda', 'insuficiencia ventricular derecha', 'cardiopatia congestiva', 'insuficiencia cardiaca cronica', 'insuficiencia cardiaca aguda', 'insuficiencia cardiaca aguda descompensada', ' icc']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Lee.cong = og[text.Line]
        Lee.cong_p = 1
    print("cong: %s", Lee.cong)
    return 0

#Determinar historial de enfermedad cerebrovascular
def Find_CV(f,og,Lee):
    terms = ['accidente isquemico transitorio', '  ictus', 'ataque cerebral', '  evc', 'infarto cerebral', 'embolia cerebral', 'apoplejia', 'derrame cerebral', 'hemorragia subaracnoidea', '  acv', 'evc isquemico', 'hemorragia cerebral', 'isquemio cerebral', 'accidente cerebrovascular', 'enfermedad cerebrovascular', 'evc hemorragico', 'evento cerebral vascular']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Lee.CV = og[text.Line]
        Lee.CV_p = 1
    print("CV: %s", Lee.CV)
    return 0

#Determinar si hay terapia de insulina para diabetes
def Find_diab(f,og,Lee):
    terms = ['tratamiento diabet tipo 1', 'tratamiento insulinodependiente', 'terapia insulinodependiente', 'insulin nph', 'insulin glulisin', 'insulina lispro', 'tratamiento insulin', 'insulina aspart', 'insulina diabetico', 'insulina accion ultra rapido', 'insulina accion rapido', 'insulina accion prolongado', 'insulin detemir', 'terapia insulin', 'insulina accion intermedia', 'insulina', 'diabetes insulinodependiente', 'diabet tipo 1', 'insulina glargin', 'insulin diabetes']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Lee.diab = og[text.Line]
        Lee.diab_p = 1
    print("Diab: %s", Lee.diab)
    return 0

#Determinar creatinina preoperatoria
def Find_Cr(f,og,Lee):
    terms = ['creatinina preoperatorio', 'creatinina preoperatorio tomado', 'creatinina preoperatorio realizado', 'creatinina previo cirugia', 'evaluacion creatinin preoperatoria']
    unit1 = ['mg/dl', 'mg / dl', 'miligramo decilitro']
    unit2 = ['micromolar', 'micromol litro', 'micromol / l']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Lee.Cr = og[text.Line]
        x = Find_Cant(text.Term)
        for i in unit1:  # Determinar la cantidad de creatinina en mg/dL
            if i in text.Term and x >= 2:
                Lee.Cr_p = 1
                break
        for i in unit2:  # Determinar la cantidad de creatinina en micromol/L
            if i in text.Term and x >= 177:
                Lee.Cr_p = 1
                break
    print("Cr: %s", Lee.Cr)
    return 0

#Determinar angina segun la Sociedad Cardiovascular Canadiense
def Find_ang(f,og,Detsky):
    terms1 = ['limitacion pronunciado actividad fisico rutinario', 'marcado limitacion actividad fisico ordinario', 'clase iii', 'clase 3', 'dificultad subir escalera', 'dificultad marcado actividad fisico ordinario', 'dificultad caminar ritmo normal', 'limitacion significativo actividad fisico habitual', 'restriccion notable actividad fisico diario', 'problema caminar distancia corto']
    terms2 = ['angin pecho reposo', 'clase iv', 'angina reposo', 'limitacion realizar actividad fisico', 'angina pecho reposo', 'sica reposo', 'sindromar isquemico coronario agudo reposo', 'dolor toracico reposo', 'dificultad ejercer actividad fisico molestia', 'molestia realizar actividad fisico', 'incapacidad actividad fisico molestia', 'clase 4', 'imposibilidad actividad fisico molestia', 'dolor pecho reposo']
    text1 = Find_Syn(terms1, f)
    text2 = Find_Syn(terms2, f)
    if text1.Term != "0":
        Detsky.ang = og[text1.Line]
        Detsky.ang_p = 10
    elif text2.Term != "0":
        Detsky.ang = og[text2.Line]
        Detsky.ang_p = 20
    print("Angina canadidense: %s", Detsky.ang)
    return 0

#Determinar angina inestable
def Find_angina(f,og,Detsky):
    terms = ['angor inestable', 'dolor toracico inestable', 'dolor precordial inestable', 'angina inestable', 'sindromar isquemico coronario agudo', 'dolor toracico opresivo', 'insuficiencia coronario agudo', 'sica', 'sindromar coronario agudo sin elevacion st']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Detsky.angina = og[text.Line]
        Detsky.angina_p = 10
    print("Angina inestable: %s", Detsky.angina)
    return 0

#Determinar edema pulmonar
def Find_edema(f,og,Detsky):
    terms = ['congestion pulmonar', 'sdra', 'sindromir dificultad respiratorio agudo', 'edema agudo pulmon', 'edema pulmonar', 'insuficiencia respiratorio agudo']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Detsky.edema = og[text.Line]
        Detsky.edema_p = 5
        x = Find_Cant(text.Term)
        if ("semana" in text.Term and x <= 1) or ("dia" in text.Term and x <= 8): #Determinar si el edema ocurrió hace menos de una semana
            Detsky.edema_p = 10
    print("Edema: %s", Detsky.edema)
    return 0

#Determinar cáncer activo
def Find_cancer(f,og,Padua):
    terms = ['radioterapia', 'cancer', 'diseminacion metastasico', 'tratamiento radiante', 'tumor maligno', 'neoplasio', 'metastasizado', 'cancer activo', 'enfermedad neoplasico', 'terapia radiacion', 'metastasi', 'propagacion metastasico', 'radiacion terapeutico', 'enfermedad oncologico', 'terapia radiante', 'irradiacion']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Padua.cancer = og[text.Line]
        Padua.cancer_p = 3
    print("Cancer: %s", Padua.cancer)
    return 0

#Determinar TEV
def Find_TEV(f,og,Padua):
    terms = ['embolia pulmonar', 'trombosis venos profundo', 'tromboembolia pulmonar', '  tep', '  tvp', 'tromboembolismo venoso', '  tev', 'dimero d elevado']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Padua.TEV = og[text.Line]
        Padua.TEV_p = 3
    print("TEV: %s", Padua.TEV)
    return 0

#Determinar condición trombofilia conocida
def Find_trombo(f,og,Padua):
    terms = ['defecto protein s', 'problema coagulacion sanguineo', 'enfermedad tromboembolico', 'coagulopatia hereditario', 'defecto antitrombin', 'anormalidad coagulacion', 'factor v leidir', 'trastorno hipercoagulabilidad', 'sindromar antifosfolipido', 'defecto proteinar c', 'trombofilia', 'trastorno tromboembolico', 'mutacion protrombin g20210a', 'trastorno trombotico', 'hipercoagulabilidad', 'enfermedad trombotico']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Padua.trombo = og[text.Line]
        Padua.trombo_p = 3
    print("Trombo: %s", Padua.trombo)
    return 0

#Determinar trauma reciente o cirugía
def Find_trauma(f,og,Padua):
    terms = ['intervencion quirurgico', 'intervencion operatoria', 'evento traumatico', 'acto quirurgico', 'procedimiento operatorio', 'trauma ', 'operacion', 'procedimiento quirurgico', 'accidente', 'lesion', 'cirugia', 'herido']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Padua.OR = og[text.Line]
        x = Find_Cant(text.Term)
        if ("semana" in text.Term and x <= 4) or ("dia" in text.Term and x <= 31) or ("mes" in text.Term and x <= 1) or ("una semana" in text.Term): #Determinar si el edema ocurrió hace menos de una semana
            Padua.OR_p = 2
    print("Trauma: %s" % Padua.OR)
    return 0

#Determinar falla respiratoria o cardíaca
def Find_falla(f,og,Padua):
    terms = ['hipoxia', 'alteracion respiratorio', 'disneo', 'atelectasio', 'consolidacion basal', 'derrame pleural', 'falla ventricular', 'insuficiencia respiratorio', 'hipoxemiar', 'insuficiencia cardiaco', 'dificultad respiratorio', 'hipercapnia', 'falla respiratorio', 'disfuncion sistolico', 'falla cardiaco', 'cardiopatia congestivo', 'fracaso respiratorio', 'disfuncion ventricular', 'hipercarbia', 'insuficiencia pulmonar', 'insuficiencia ventricular', 'fallo pulmonar', 'sibilancia', ]
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Padua.falla = og[text.Line]
        Padua.falla_p = 1
    print("Falla: %s" % Padua.falla)
    return 0

#Determinar desorden reumatologico
def Find_reuma(f,og,Padua):
    print(Padua.IAM)
    terms = ['sindromar Sjogren agudo', 'artritis reumatoidir agudo', 'polimiositis agudo', 'desorden reumatologico agudo', 'esclerodermia agudo', 'lupus eritematoso sistemico agudo', 'dermatomiositis agudo']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Padua.IAM = og[text.Line]
        Padua.IAM_p = 1
    print("Reuma: %s" % Padua.IAM)
    return 0

#Determinar obesidad
def Find_BMI(f,og,Padua):
    terms = ['hiperplasia adipos', 'sobrepeso', 'sindromar metabolico', 'exceso peso', 'indecir masa corporal elevado', 'adiposidad', 'hiperadiposidad', 'exceso grasa corporal', 'peso elevado', 'obesidad']
    unit1 = ['  bmi', 'indicar masa corporal', '  imc']
    text_unit = Find_Syn(unit1,f)
    if text_unit.Term != "0":
        Padua.BMI = og[text_unit.Line]
        x = Find_Cant(text_unit.Term)
        if x >= 30:
            Padua.BMI_p = 1
    else:
        text = Find_Syn(terms,f)
        if text.Term != "0": #Determinar si se encontró una coincidencia
            Padua.BMI = og[text.Line]
            Padua.BMI_p = 1
    print("BMI: %s", Padua.BMI)
    return 0

#Determinar terapia hormonal
def Find_TH(f,og,Padua):
    terms = ['terapia hormonal', 'tratamiento hormonar', 'terapia hormona', 'tratamiento hormona', 'hormonoterapia', 'tratamiento hormonal']
    text = Find_Syn(terms,f)
    if text.Term != "0": #Determinar si se encontró una coincidencia
        Padua.TH = og[text.Line]
        Padua.TH_p = 1
    print("TH: %s", Padua.TH)
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