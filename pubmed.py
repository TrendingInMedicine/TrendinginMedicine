import requests
import json
import collections
import string
import nltk
import time
from collections import OrderedDict
from firebase import firebase
from nltk.corpus import stopwords

fb = firebase.FirebaseApplication("https://trendinginmedicine-f41fc.firebaseio.com/")
journals = set()
keyWords = dict()
translator = str.maketrans('', '', string.punctuation)
commonWords = stopwords.words('english') + ['review', "surgery", "report", "peer", "patients", "systematic", "surgical", "management", "meta-analysis", "versus", "total", "factors", "controlled", "repair", "cancer", "randomized", "study", "outcomes", "reconstruction", "safety", "open", "analysis", 'metaanalysis', '“comparison', '“the', 'study”', "cancer:", "clinical", "case", "oral", "treatment", "chapter", "—", "using", "cell", "cases", "head", "evaluation", "literature", "neck", "patient", "technique", "retrospective", "flap", "facial", "experience", "use", "following", "approach", "comparison", "syndrome", "threedimensional", "disease", "bone", "joint", "implants", "postoperative", "postoperative", "rare", "effect", "outcome", "dental", "artery", "carcinoma","risk", "associated", 'therapy', 'acute', 'lower', "maxillary", 'resection', 'bypass', "vascular", "longterm", "graft", "cohort", "transplantation", "preoperative", "prospective", "injury", "mortality", "care", "extremity", "discussion", "trial", "primary", "impact", "quality", "complications", "surgeons", "undergoing", "intraoperative", "research", "volume", "hospital", "survival", "improves", "role", "results", "prognosis", "prognostic", "control", "lung", "function", "centers", "center", "multicenter", "heart", "association", "coronary", "cardiovascular", "failure", "american", "valve", "atrial", "cardiac", "left", "pulmonary", "fibrillation", "pressure", "perceutaneous", "aortic", "infaraction", "blood", "chronic", "college", "stroke", "reply", "events", "guidelines", "women", "mitral", "data", "trials", "laparoscopic", "breast", "general", "model", "early", "invasive", "novel", "value", "time", "training", "score", "medical", "single", "portal", "development", "years", "emergency", "recovery"]
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
        journal = "&id=" + str(i)
        output = "&retmode=json&rettype=json"
        r = requests.get(searchURL + journal + output)
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
        titles.append(title)
        for word in title.split():
            word = word.lower()
            word = word.translate(translator)
            if word not in commonWords and len(word) > 3:
                if word in keyWords:
                    alist = keyWords[word]
                    alist.add(articleinfo)
                else:
                    tempset = set()
                    tempset.add(articleinfo)
                    keyWords[word] = tempset
    keyWords = OrderedDict(sorted(keyWords.items(),key=lambda t: len(t[1]), reverse=True))
    print(str(len(journals)) + " journals found")
    return keyWords

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
storeInDatabase()
t2 = time.time()
print(t2-t1)
# result = fb.get('surgery', '3 abdominal')
# print(result)