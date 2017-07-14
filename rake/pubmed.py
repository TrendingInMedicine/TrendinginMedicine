import requests
import json
import collections
import string
import nltk
import time
import sqlite3
import datetime
from collections import OrderedDict
# from firebase import firebase
from nltk.corpus import stopwords
import xml.etree.ElementTree as ET
import rake_nltk as rn
import operator

# fb = firebase.FirebaseApplication("https://trendinginmedicine-f41fc.firebaseio.com/")
rake = rn.RAKE()

journals = set()
translator = str.maketrans('', '', string.punctuation)
idlist = []
titles = []
s = "+"
topic = 'surgery'
#topic = 'cardiology'
#l = ["Journal of the American College of Cardiology[ta]", "JACC. Heart failure[ta]", "JACC. Cardiovascular interventions[ta]", "Chest[ta]", "American heart journal[ta]", "Journal of the American Heart Association[ta]", "\"European heart journal\"[ta]"]

now = datetime.datetime.now()
m = now.month
month = ""
if m < 10:
    month = '0' + str(m)
else:
    month = str(m)

year = str(now.year)

l = ["JAMA surgery[ta]", "World journal of surgery[ta]", "American journal of surgery[ta]", "The Surgical clinics of North America[ta]", "The Journal of surgical research[ta]", "Journal of surgical education[ta]", "Adv Surg[ta]", "European surgical research[ta]", "\"The Journal of the International College of Surgeons\"[ta]", "Journal of the American College of Surgeons[ta]", "\"Bulletin of the American College of Surgeons\"[ta]", "\"Surgery\"[ta]", "International journal of surgery[ta]", "\"The European journal of surgery\"[ta]", "Surgery today[ta]", "Annals of surgery[ta]", "The British journal of surgery[ta]", "The American surgeon[ta]", "\"International journal of surgery and research\"[ta]", "\"Canadian journal of surgery\"[ta]", "\"Current problems in surgery\"[ta]", "Scandinavian journal of surgery[ta]", "Surgical innovation[ta]", "\"Annals of surgical innovation and research\"[ta]", "Updates in surgery[ta]", "Annals of surgical treatment and research[ta]", "Asian journal of surgery[ta]", "\"Southeast Asian journal of surgery\"[ta]", "Journal of investigative surgery[ta]", "Annals of the Royal College of Surgeons of England[ta]", "\"International surgery\"[ta]", "Indian J Surg[ta]",'The American journal of surgical pathology', 'Annals of surgical oncology', 'Surgical endoscopy', 'Microsurgery', 'Journal of surgical oncology', 'European journal of surgical oncology : the journal of the European Society of Surgical Oncology and the British Association of Surgical Oncology', 'Surgical oncology clinics of North America', 'Seminars in pediatric surgery', 'Surgical infections', 'World journal of emergency surgery : WJES', 'World journal of surgical oncology', 'Minimally invasive surgery', 'ANZ journal of surgery', 'Pediatric surgery international', 'International journal of surgical pathology']
print(str(len(l)) + " journals searched for")
searchURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"
date = "&datetype=pdat&mindate="+year+"/"+month+"/01&maxdate="+year+"/"+month+"/31"
count = "&retmax=10000"
output = "&retmode=json"

sqlTableName = topic + month +'-'+ year
conn = sqlite3.connect(sqlTableName + '.db')
curs = conn.cursor()
curs.execute('''CREATE TABLE topPhrases (phrase text, article text)''')

phrase_to_journal = dict()

def getKeyWords():
    global phrase_to_journal, idlist, searchURL, date, count, output, junk
    silly_var = 0
    junk = 0
    t1 = time.time()
    for i in l:
        boshal = i.split(' ')
        journal = "&term=" + s.join(boshal)
        r = requests.get(searchURL + journal + date + count + output)
        if r.text == None:
            r.text = ""
            return
        jsonobj = json.loads(r.text)
        idlist += jsonobj["esearchresult"]["idlist"]
    t2 = time.time()
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
        t1 = time.time()
        abstractXML = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&rettype=abstract" + id_number
        response = requests.get(abstractXML, stream=True)
        response.raw.decode_content = True
        events = ET.iterparse(response.raw)
        abstractText = ""
        silly_var = silly_var + 1
        for event, elem in events:
            if(elem.tag == "AbstractText") and elem.text != None:
                abstractText = abstractText + elem.text
        if(len(abstractText) != 0):
            # print(abstractText)
            t1 = time.time()
            rakePhrases = rake.extract(title + abstractText, 1, 4)
            t2 = time.time()
            # print(t2-t1)

            # print(abstractText + "\n")
            # print("rakePhrases: ", rakePhrases)

            rakePhrases = dict(rakePhrases)

            for phrase in rakePhrases:
                if rakePhrases[phrase] >= 10:
                    if phrase in phrase_to_journal:
                        alist = phrase_to_journal[phrase]
                        alist.add(articleinfo)
                    else:
                        tempset = set()
                        tempset.add(articleinfo)
                        phrase_to_journal[phrase] = tempset
        else:
            junk = junk + 1
    print(str(len(idlist)-junk) + " articles found.")
    phrase_to_journal = OrderedDict(sorted(phrase_to_journal.items(),key=lambda t: len(t[1]), reverse=True))
    return phrase_to_journal

def storeInDatabase():
    countten = 0
    counter = 0
    for i in phrase_to_journal.keys():
        if countten == 15:
            break
        for j in titles:
            if i in j:
               counter +=1
        # fb.put(topic, str(countten+1), [str(i)] + list(phrase_to_journal[i]))
        # print("\n"+i)
        for k in phrase_to_journal[i]:
            try:
                # print("\t" + str(k))
                curs.execute("INSERT INTO topPhrases VALUES (\'" + str(i) + "\',\'" + str(k) + "\')")
            except sqlite3.OperationalError:
                print("Error!", i, k)

        # print(i, len(phrase_to_journal[i]))
        articles = list(phrase_to_journal[i])
        # for j in range(len(articles)):
        #     print(str(j) + "\t" + str(articles[j]))
        countten+=1
        counter = 0



t1 = time.time()
getKeyWords()
storeInDatabase()
t2 = time.time()
print(t2-t1)
conn.commit()
conn.close()
