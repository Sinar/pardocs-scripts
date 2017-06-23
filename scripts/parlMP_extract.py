#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, pickle 
from nltk.corpus import wordnet
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from fuzzywuzzy import process
    
#Nalay stopwords
from nltk.corpus import stopwords
malay_stops = set(stopwords.words('malay'))
#Malay stemmer
factory = StemmerFactory()
ZSMstemmer = factory.create_stemmer()

class MyWordNet:
    
    def __init__(self, wn):
        self._wordnet = wn
    
    def synsets(self, word, pos=None, lang= "zsm"):
        return self._wordnet.synsets(word, pos=pos, lang=lang)


def processText(doc):
    stemmed = ZSMstemmer.stem(doc)
    stop_free = " ".join([t for t in stemmed.split() if t not in malay_stops and len(t)>3])
    return stop_free

def cleanText(txt):
    txt = re.sub(r'[^\w@]', ' ', re.sub(r'\.', '', txt))
    txt = " ".join(txt.lower().split())
    return txt
    
def ministryMatch(s):
    ministries = ['perdana menteri', 
'menteri dalam negeri', 
'menteri kewangan', 
'menteri pendidikan', 
'menteri kesihatan', 
'menteri pertanian dan industri asas tani',
'menteri perdagangan dalam negeri koperasi dan kepenggunaan',
'menteri sumber asli dan alam sekitar',
'menteri tenaga teknologi hijau dan air',
'menteri sumber manusia',
'menteri pembangunan wanita keluarga dan masyarakat',
'menteri pertahanan',
'menteri perdagangan antarabangsa dan industri',
'menteri kerja raya',
'menteri pelancongan dan kebudayaan',
'menteri belia dan sukan',
'menteri perusahaan perladangan dan komoditi',
'menteri wilayah persekutuan',
'menteri komunikasi dan multimedia',
'menteri pengangkutan',
'menteri pendidikan tinggi',
'menteri luar negeri',
'menteri kemajuan luar bandar dan wilayah',
'menteri kesejahteraan bandar perumahan dan kerajaan tempatan',
'menteri sains teknologi dan inovasi' 
]
    if len(s)>3:
        closestMatch = process.extract(s, ministries, limit=1)
        return closestMatch[0][0]
    else:
        return ""

def extractMinistry(text):
    responderMatch = re.findall('minta(.*?)\s?menyatakan', text, re.DOTALL|re.IGNORECASE)
    if responderMatch:
        ministry = responderMatch[0]
    else:
        ministry = ""
        
    return ministryMatch(ministry)

def ministerMatch(s):
    ministers = pickle.load(open('ministerNames.p', 'wb'))
    
    if len(s)>3:
        closestMatch = process.extract(s, ministers, limit=1)
        return closestMatch[0][0]
    else:
        return ""
        
    
def extractMinister(text):
    name = ""  
    honorifics= ["\stuan", "puan", "dr", "yb", "tun", "datuk", "dato", "datin", "ybhg", "laksamana", "tan sri", "dato sri", "datuk seri", "tan seri", "pehin"]
    honorifics_OR = "|\s".join(honorifics)
    
    nameMatch_pattern = "("+ honorifics_OR+")*(.*)(" + honorifics_OR + ")(.*)minta (.*)menyatakan"                     
    nameMatch = re.findall(nameMatch_pattern, text, re.DOTALL|re.IGNORECASE)
    if nameMatch:
        name = nameMatch[0][-2]
    
    return ministerMatch(name)

def minister_area(minister):
    match = re.findall('(?<=\[|\()([\w]*)(?=\]|\))', minister, re.DOTALL)
    if match:
        return([match[0], match[1]])
    else:
        return [minister, None]
    
def extractQuestion(raw_text):
    
    questionmatch1= re.findall('soalan(.*?)(?=jawapan|yang di.?pertua)', raw_text, re.DOTALL|re.IGNORECASE)
    if questionmatch1:
        question = questionmatch1[0]
    else:
        question = ""
    
    questionmatch2= re.findall('minta(.*?)\s?menyatakan(.*)(?=jawapan|yang di.?pertua)', raw_text, re.DOTALL|re.IGNORECASE)
    if questionmatch2:
        if not question and len(questionmatch2[0])>1:
            question = questionmatch2[0][1]

    return question

def load_corpus(dirpath):
    file_names = []
    raw_txt = []
    txt = []
    questions = []
    ministries = []
    ministers = []
    areas = []
    
    
    for filename in os.listdir(dirpath):
        file_names.append(filename)
        
        with open(os.path.join(dirpath, filename)) as f:
            raw_text = f.read()
            raw_txt.append(raw_text)
            cleaned_txt = cleanText(raw_text)      
            txt.append(cleaned_txt)
        
            #QUESTION
            question = extractQuestion(raw_text)
            questions.append(cleanText(question))
                
            #MINISTRY
            ministry = extractMinistry(cleaned_txt)
            ministries.append(cleanText(ministry))
            
            #MINISTER, AREA
            minister = extractMinister(question)
                
            if minister:
                minister, area = minister_area(minister)
                
            ministers.append(cleanText(minister))
            areas.append(cleanText(area))
            
    dic = {'file_name': file_names, 'raw_text': raw_txt, 'text': txt, 'question': questions, 'ministry': ministries, 'minister': ministers, 'area': areas}
    return dic



