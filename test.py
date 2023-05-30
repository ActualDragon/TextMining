
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
    total = 0
    is_empty = 0

example = Goldman_Index()
atributos = [attr for attr in dir(example) if not callable(getattr(example, attr)) and not attr.startswith("__")]

for atributo in atributos:
    valor = getattr(example, atributo)  # Obtener el valor del atributo

    if not callable(valor):  # Ignorar métodos
        print(f"{atributo}: {valor}")  # Imprimir nombre del atributo y su valor

"""
import os.path

save_path = os.path.join(os.path.expanduser("~"),"Downloads")

name_of_file = "Prueba.doc"

completeName = os.path.join(save_path, name_of_file)

file1 = open(completeName, "w+")

toFile = "Hello World!"

file1.write(toFile)

file1.close()

import spacy
nlp = spacy.load('es_core_news_sm')
nlp.Defaults.stop_words -= {"sin", "dia", "dias", "hoy"}

stopwords = nlp.Defaults.stop_words
#print(type(stopwords))
#print(len(stopwords))
#print(stopwords)



def process_sentence_array(sentence_array):
    lemma_sentences = set() # Utilizamos un conjunto para evitar duplicados
    for sentence in sentence_array:
        doc = nlp(sentence)
        filter = ' '.join(token.lemma_ for token in doc if (token.lemma_ not in stopwords and token.lemma_ != "de" and token.lemma_ != "el"))
        filter = filter.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("-"," ")
        lemma_sentences.add(filter)
    return list(lemma_sentences)  # Convertimos el conjunto a lista

sentence_array = ['remisión']
lemma_sentences = process_sentence_array(sentence_array)

print(lemma_sentences)



    #de, la, que, el, en, y, a, los, del, se, las, por, un, para, con, no, una, su, al, lo, como, más, pero, sus, le, ya, o, este, sí, porque, esta, entre, cuando, muy, sin, sobre, también, me, hasta, hay, donde, quien, desde, todo, nos, durante, todos, uno, les, ni, contra, otros, ese, eso, ante, ellos, e, esto, mí, antes, algunos, qué, unos, yo, otro, otras, otra, él, tanto, esa, estos, mucho, quienes, nada, muchos, cual, poco, ella, estar, estas, algunas, algo, nosotros, mi, mis, tú, te, ti, tu, tus, ellas, nosotras, vosotros, vosotras, os, mío, mía, míos, mías, tuyo, tuya, tuyos, tuyas, suyo, suya, suyos, suyas, nuestro, nuestra, nuestros, nuestras, vuestro, vuestra, vuestros, vuestras, esos, esas, estoy, estás, está, estamos, estáis, están, esté, estés, estemos, estéis, estén, estaré, estarás, estará, estaremos, estaréis, estarán, estaría, estarías, estaríamos, estaríais, estarían, estaba, estabas, estábamos, estabais, estaban, estuve, estuviste, estuvo, estuvimos, estuvisteis, estuvieron, estuviera, estuvieras, estuviéramos, estuvierais, estuvieran, estuviese, estuvieses, estuviésemos, estuvieseis, estuviesen, estando, estado, estada, estados, estadas, estad, he, has, ha, hemos, habéis, han, haya, hayas, hayamos, hayáis, hayan, habré, habrás, habrá, habremos, habréis, habrán, habría, habrías, habríamos, habríais, habrían, había, habías, habíamos, habíais, habían, hube, hubiste, hubo, hubimos, hubisteis, hubieron, hubiera, hubieras, hubiéramos, hubierais, hubieran, hubiese, hubieses, hubiésemos, hubieseis, hubiesen, habiendo, habido, habida, habidos, habidas, soy, eres, es, somos, sois, son, sea, seas, seamos, seáis, sean, seré, serás, será, seremos, seréis, serán, sería, serías, seríamos, seríais, serían, era, eras, éramos, erais, eran, fui, fuiste, fue, fuimos, fuisteis, fueron, fuera, fueras, fuéramos, fuerais, fueran, fuese, fueses, fuésemos, fueseis, fuesen, siendo, sido, sed.




term = "5 contracciones"
for i in term.split():
    try: #intentar convertir el token a float
        cant = float(i)
        break #salir del loop si i es la primera cadena que si es float
    except:
        continue
print("Cantidad: " + str(cant)) #1.5


import spacy
nlp = spacy.load('es_core_news_sm')

text = "El perro no corre por el parque"

doc = nlp(text)

# Remove stop words
filtered_tokens = [token.text for token in doc if not token.is_stop]
filtered_tokens = [token.text for token in doc if not token.is_stop or token.text == 'no']

print(filtered_tokens)


import atexit

print("Started")
input("Press Enter to continue...")

@atexit.register
def goodbye():
    print("You are now leaving the Python sector")

from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Define example sentences
sentence1 = "Infarto agudo de miocardio"
sentence2 ="Infarto agudo de miocardio"

# Tokenize sentences
words1 = word_tokenize(sentence1)
words2 = word_tokenize(sentence2)
stopwords_español = set(stopwords.words('spanish'))
words1 = [palabra for palabra in words1 if palabra not in stopwords_español]
words2 = [palabra for palabra in words2 if palabra not in stopwords_español]
print

# Define function to compute maximum similarity score between two words
def compute_similarity_score(word1, word2):
    synsets1 = wn.synsets(word1, lang="spa")
    synsets2 = wn.synsets(word2, lang="spa")
    max_similarity = 0
    for synset1 in synsets1:
        for synset2 in synsets2:
            similarity = synset1.path_similarity(synset2)
            if similarity is not None and similarity > max_similarity:
                max_similarity = similarity
    return max_similarity

# Compute average similarity score between all pairs of words from the two sentences
total_score = 0
count = 0
print("Sentence",words2)
for word1 in words1:
    for word2 in words2:
        similarity_score = compute_similarity_score(word1, word2)
        print("Word 1:", word1)
        print("Word 2:", word2)
        print("Score: ", similarity_score)
        if similarity_score > 0:
            total_score += similarity_score
            count += 1
if count > 0:
    average_score = total_score / count
else:
    average_score = 0
print("Similarity score:", average_score)



from nltk.corpus import wordnet
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

list1 = ['infarto']
list2 = terms =["ATAQUE_CARDIACO"]
list = []

for word1 in list1:
    for word2 in list2:
        wordFromList1 = wordnet.synsets(word1, lang='spa')
        wordFromList2 = wordnet.synsets(word2.lower(), lang='spa')
        if wordFromList1 and wordFromList2: #Thanks to @alexis' note
            s = wordFromList1[0].wup_similarity(wordFromList2[0])
            list.append(s)

print(max(list))


import aspose.words as aw #Lectura de archivos
from nltk.corpus import wordnet as wn
f = []
s = []
text = []
doc = aw.Document("C:\\Users\\danyg\\Documents\\Internado\\prueba.doc") # Cargar el archivo a leer
    # Leer el contenido de los parrafos tipo nodo
for paragraph in doc.get_child_nodes(aw.NodeType.PARAGRAPH, True) :
    paragraph = paragraph.as_paragraph()
    p = paragraph.to_string(aw.SaveFormat.TEXT)
    p = p.replace("\\", "/").replace('"','\\"').replace("'","\'") #Escapar caracteres especiales
    p = p.replace('\n', '').replace('\r', '') #Eliminar saltos de linea y el retorno de carro
    f.append(p)
size = len(f)
for x in range(1,size-2):
    s.append(f[x])
text = s[0].split(".") #Separar en oraciones

terms = ["INFARTO AGUDO DE MIOCARDIO", "IM", "IMA", "IAM", "INFARTO", "INFARTO CARDIACO", "ATAQUE CARDIACO", "ATAQUE AL CORAZON", "INFARTO DE MIOCARDIO", "INFARTO MIOCARDICO"]
f = ["hOLA", "EL PACIENTE TUVO UN INFARTO AGUDO DE MIOCARDO", "PRUEBAS DEL PROGRAMA"]
list = ""
IAM = []
syn = wn.synonyms('INFARTO', lang='spa')
if syn[0] != []:
    list = syn[0]
    for x in list:
        x = x.upper()
        x = x.replace("_", " ")
        terms.append(x)
terms.append("IAM")
for i in range(len(terms)):
    for j in range(len(f)):
        k = f[j].find(terms[i])
        if k != -1:
            print("Cadena: ", f[j])
            print("Termino:", terms[i])
            print("Encontrado: ", f[j])
            IAM.append(f[j])
if IAM == []:
    IAM.append(0)
print(IAM[0])


syn = wn.lemmas('diabetes', lang='spa')
print("Lemmas: ",syn)
print("Lemmas type: ",type(syn[0]),"\n")

syn = wn.synsets("diabetes", lang='spa')
print("Synsets: ",syn)
eng = syn[0].name()
print("Synset name: ",eng)
print("Synset name type: ",type(eng))
eng = syn[0].lemma_names('spa')
print("Lemma names: ",eng,"\n")

print("Definition: ",syn[0].definition())



class Goldman:
    def age(self, age):
        self.age = age

    def name(self,name):
        self.name = name

    def __str__(self):
        return "Name: %s \n" \
               "Age: %i" % (self.name, self.age)

Dany = Goldman()
Dany.age(5)
Dany.name("Dany")
print(Dany)


class MyClass():
    age = 123
    name =0
Objeto = MyClass()

def Func(Objeto):
    Objeto.age = 666
    #Objeto.name = "Dany"
    return 1

f = Func(Objeto)

print(Objeto.age)
print(Objeto.name)

"""