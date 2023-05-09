"""
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