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

keyWords = dict()
translator = str.maketrans('', '', string.punctuation)
commonWords = stopwords.words('english') + ['review', "surgery", "report", "peer", "patients", "systematic", "surgical", "management", "meta-analysis", "versus", "total", "factors", "controlled", "repair", "cancer", "randomized", "study", "outcomes", "reconstruction", "safety", "open", "analysis", 'metaanalysis', '“comparison', '“the', 'study”', "cancer:", "clinical", "case", "oral", "treatment", "chapter", "—", "using", "cell", "cases", "head", "evaluation", "literature", "neck", "patient", "technique", "retrospective", "flap", "facial", "experience", "use", "following", "approach", "comparison", "syndrome", "threedimensional", "disease", "bone", "joint", "implants", "postoperative", "postoperative", "rare", "effect", "outcome", "dental", "artery", "carcinoma","risk", "associated", 'therapy', 'acute', 'lower', "maxillary", 'resection', 'bypass', "vascular", "longterm", "graft", "cohort", "transplantation", "preoperative", "prospective", "injury", "mortality", "care", "extremity", "discussion", "trial", "primary", "impact", "quality", "complications", "surgeons", "undergoing", "intraoperative", "research", "volume", "hospital", "survival", "improves", "role", "results", "prognosis", "prognostic", "control", "lung", "function", "centers", "center", "multicenter", "heart", "association", "coronary", "cardiovascular", "failure", "american", "valve", "atrial", "cardiac", "left", "pulmonary", "fibrillation", "pressure", "perceutaneous", "aortic", "infaraction", "blood", "chronic", "college", "stroke", "reply", "events", "guidelines", "women", "mitral", "data", "trials"]
idlist = []
titles = []
s = "+"
l = ["Journal of the American College of Cardiology[ta]", "JACC. Heart failure[ta]", "JACC. Cardiovascular interventions[ta]", "Chest[ta]", "American heart journal[ta]", "Journal of the American Heart Association[ta]", "\"European heart journal\"[ta]"]
#l = ["Journal of the American College of Surgeons[ta]", "\"Surgery\"[ta]", "International Journal of Surgery[ta]", "The European journal of surgery[ta]", "The British journal of surgery[ta]", "Surgery today[ta]", "Annals of Surgery[ta]"] #"British Journal of Oral and Maxillofacial Surgery[ta]", "The Journal of Heart and Lung Transplantation[ta]", "Annals of Vascular Surgery[ta]"]
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
    print(len(idlist))
    searchURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed"
    for i in idlist:
        journal = "&id=" + str(i)
        output = "&retmode=json&rettype=json"
        r = requests.get(searchURL + journal + output)
        jsonobj = json.loads(r.text)
        title = jsonobj["result"][str(i)]["title"]
        journalname = jsonobj["result"][str(i)]["source"]
        authors = ""
        for j in jsonobj["result"][str(i)]["authors"]:
            authors += j["name"] + ", "
        authors = authors[:-2]
        authors += ". "
        pubdate = jsonobj["result"][str(i)]["pubdate"]
        articleinfo = authors + title + " " + journalname + ". " + pubdate + ". " + "https://www.ncbi.nlm.nih.gov/pubmed/?term=" + str(i)
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
    return keyWords

def storeInDatabase():
    countten = 0
    for i in keyWords.keys():
        if countten == 10:
            break
        print(i)
        fb.put('cardiology', str(countten+1), [str(i)] + list(keyWords[i]))
        print(len(keyWords[i]))
        articles = list(keyWords[i])
        # for j in range(len(articles)):
        #     print(str(j) + "\t" + str(articles[j]))
        countten+=1

t1 = time.time()
getKeyWords()
storeInDatabase()
t2 = time.time()
print(t2-t1)
# result = fb.get('surgery', '3 abdominal')
# print(result)