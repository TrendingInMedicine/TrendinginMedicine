import requests
import json
import collections
import string
import nltk
import time
from collections import OrderedDict
from firebase import firebase
from nltk.corpus import stopwords
import xml.etree.ElementTree as ET
import rake_nltk
import operator

fb = firebase.FirebaseApplication("https://trendinginmedicine-f41fc.firebaseio.com/")
rake_object = rake.Rake("SmartStoplist.txt", 3, 3, 1)
journals = set()
keyWords = dict()
translator = str.maketrans('', '', string.punctuation)
idlist = []
titles = []
s = "+"
topic = 'surgery'
#l = ["Journal of the American College of Cardiology[ta]", "JACC. Heart failure[ta]", "JACC. Cardiovascular interventions[ta]", "Chest[ta]", "American heart journal[ta]", "Journal of the American Heart Association[ta]", "\"European heart journal\"[ta]"]
l = ["JAMA surgery[ta]", "World journal of surgery[ta]", "American journal of surgery[ta]", "The Surgical clinics of North America[ta]", "The Journal of surgical research[ta]", "Journal of surgical education[ta]", "Adv Surg[ta]", "European surgical research[ta]", "\"The Journal of the International College of Surgeons\"[ta]", "Journal of the American College of Surgeons[ta]", "\"Bulletin of the American College of Surgeons\"[ta]", "\"Surgery\"[ta]", "International journal of surgery[ta]", "\"The European journal of surgery\"[ta]", "Surgery today[ta]", "Annals of surgery[ta]", "The British journal of surgery[ta]", "The American surgeon[ta]", "\"International journal of surgery and research\"[ta]", "\"Canadian journal of surgery\"[ta]", "\"Current problems in surgery\"[ta]", "Scandinavian journal of surgery[ta]", "Surgical innovation[ta]", "\"Annals of surgical innovation and research\"[ta]", "Updates in surgery[ta]", "Annals of surgical treatment and research[ta]", "Asian journal of surgery[ta]", "\"Southeast Asian journal of surgery\"[ta]", "Journal of investigative surgery[ta]", "Annals of the Royal College of Surgeons of England[ta]", "\"International surgery\"[ta]", "Indian J Surg[ta]"]
print(str(len(l)) + " journals searched for")
searchURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"
date = "&datetype=pdat&mindate=2017/03/01&maxdate=2017/03/31"
count = "&retmax=10000"
output = "&retmode=json"

def getKeyWords():
    global keyWords, idlist, searchURL, date, count, output
    for i in l:
        boshal = i.split(' ')
        journal = "&term=" + s.join(boshal)
        r = requests.get(searchURL + journal + date + count + output)
        jsonobj = json.loads(r.text)
        idlist += jsonobj["esearchresult"]["idlist"]
    print(str(len(idlist)) + " articles found")
    searchURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed"
    for i in idlist:
        id_number = "&id=" + str(i)
        output = "&retmode=json&rettype=json"
        r = requests.get(searchURL + id_number + output)
        jsonobj = json.loads(r.text)
        title = jsonobj["result"][str(i)]["title"]
        journalname = jsonobj["result"][str(i)]["source"]
        journals.add(journalname)
        authors = ""
        for j in jsonobj["result"][str(i)]["authors"]:
            authors += j["name"] + ", "
        authors = authors[:-2]
        authors += ". "
        #print(journalname)
        pubdate = jsonobj["result"][str(i)]["pubdate"]
        articleinfo = authors + title + " " + journalname + ". " + pubdate + ". " + "https://www.ncbi.nlm.nih.gov/pubmed/?term=" + str(i)
        #abstract stuff
        abstractXML = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&rettype=abstract" + id_number
        response = requests.get(abstractXML, stream=True)
        response.raw.decode_content = True
        events = ET.iterparse(response.raw)
        abstractText = ""
        for event, elem in events:
            if(elem.tag == "AbstractText"):
                abstractText = abstractText + elem.text
        if(len(abstractText) != 0):
            print(abstractText)
            keywords = rake_object.run(title + abstractText)
            print("keywords: ", keywords)

def storeInDatabase():
    countten = 0
    counter = 0
    for i in keyWords.keys():
        if countten == 30:
            break
        print(i)
        for j in titles:
            if i in j:
               counter +=1
        #fb.put(topic, str(countten+1), [str(i)] + list(keyWords[i]))
        print(len(keyWords[i]))
        articles = list(keyWords[i])
        # for j in range(len(articles)):
        #     print(str(j) + "\t" + str(articles[j]))
        countten+=1
        print(counter)
        counter = 0

t1 = time.time()
getKeyWords()
# storeInDatabase()
t2 = time.time()
print(t2-t1)
# result = fb.get('surgery', '3 abdominal')
# print(result)
