# Author: Ankur Mishra
# Email: 2018amishra@gmail.com
# RAKE Algorithm implemented in Python3 and uses NLTK
# Singularizes nouns, uses cosine similarity to check if phrases are alike, and replaces acronyms
# Specifically designed for parsing medical journals
import operator
import nltk
from nltk.tokenize import PunktSentenceTokenizer
import string
from string import digits
import re
import inflect
import traceback
import cosine_sim as cs

p = inflect.engine()

sample_text ="""
Feasibility, safety, and outcomes of a single-step endoscopic ultrasonography-guided drainage of pancreatic fluid collections without fluoroscopy using a novel electrocautery-enhanced lumen-apposing, self-expanding metal stent. There are currently limited data available regarding the safety of endoscopic ultrasound (EUS)-guided drainage of pancreatic fluid collections (PFCs) using the lumen-apposing metal stent without fluoroscopic guidance. This study aims to evaluate clinical outcomes and safety of EUS-guided drainage of pancreatic fluid collections without fluoroscopy using a novel electrocautery-enhanced lumen-apposing, self-expanding metal stent. There are currently limited data available regarding the safety of endoscopic ultrasound (EUS)-guided drainage of pancreatic fluid collections using the electrocautery-enhanced lumen-apposing metal stents (EC-LAMSs) without fluoroscopic guidance. We conducted a retrospective study on patients with symptomatic pancreatic fluid collections without fluoroscopy using a novel electrocautery-enhanced lumen-apposing, self-expanding metal stent. There are currently limited data available regarding the safety of endoscopic ultrasound (EUS)-guided drainage of pancreatic fluid collections who underwent EUS-guided drainage using EC-LAMS without fluoroscopy. All patients were followed clinically until resolution of their pancreatic fluid collections without fluoroscopy using a novel electrocautery-enhanced lumen-apposing, self-expanding metal stent. There are currently limited data available regarding the safety of endoscopic ultrasound (EUS)-guided drainage of pancreatic fluid collections Technical success (successful placement of EC-LAMS), number of patients who achieved complete resolution of pancreatic fluid collections without fluoroscopy using a novel electrocautery-enhanced lumen-apposing, self-expanding metal stent. There are currently limited data available regarding the safety of endoscopic ultrasound (EUS)-guided drainage of pancreatic fluid collections without additional intervention and adverse events were noted. We evaluated 25 patients, including three with pancreatic pseudocysts and 22 with walled-off necrosis (WON). The etiology of the patient's pancreatitis was gallstones (42%), alcohol (27%), and other causes (31%). The mean cyst size was 82 mm (range, 60-170 mm). The indications for endoscopic drainage were abdominal pain, infected WON, or gastric outlet obstruction. Technical success with placement of the EC-LAMS was achieved in all 25 patients. There were no procedure-related complications. The mean patient follow-up was 7.8 months. PFCs resolved in 24 (96%) patients; the one failure was in a patient with WON. Stent occlusion was seen in one patient. There was a spontaneous migration of one stent into the enteral lumen after resolution of WONs. The EC-LAMS were successfully removed using a snare in all the remaining patients. The median number of endoscopy sessions to achieve PFCs resolution was 2 (range, 2-6). Single-step EUS-guided drainage of PFCs without fluoroscopic guidance using the novel EC-LAMS is a safe and effective endoscopic technique for drainage of PFCs with excellent technical and clinical success rates and no complications. Due to its ease of use, EC-LAMS may simplify and streamline EUS-guided management of PFC and help in its widespread adoption as an alternative to surgery.
"""

l = []
read = open("stat_words.txt", "r") # Statistic words aren't that important in Medical Articles ∴ filter them
for i in read:
    l.append(i.rstrip('\n'))

filter_phrases = set(l)

custom_sent_tokenizer = PunktSentenceTokenizer(sample_text) # POS Tagging

def switchAccs(para): # acronyms are used a lot in medical articles, so we have to switch them out
    para = re.sub(r'\.([a-zA-Z])', r'. \1', para)
    st = para.split(" ")
    acc_to_full_word = dict()
    for i in range(len(st)):
        # st[i] = singularize(st[i])
        if(st[i].startswith("(") and st[i].endswith(")")):
             firstChar = st[i][st[i].index("(")+1]
             acronym = st[i][st[i].index("(")+1:st[i].index(")")]
             acronym = singularize(acronym)
            #  print(acronym)
             if(acronym != None):
                 for j in range(i):
                     word = st[i-j].lower()
                     if(len(acronym) > 0 and word.startswith(acronym[0].lower())):
                         full_word = st[i-j:i]
                         acc_to_full_word[acronym] = full_word
    if(len(acc_to_full_word) > 0):
        for i in range(len(st)):
            if(i < len(st) and acc_to_full_word.get(st[i].replace(".", "")) != None):
                try:
                    st[i:i+1] = acc_to_full_word.get((st[i].replace(".", "")))
                except TypeError:
                    # print(st)
                    print("acronym", st[i])
                    print(singularize(st[i]))
                    print(acc_to_full_word.get(singularize(st[i])))
                    print("Error: ",st[i]," and ", st[i:i+1])
    return " ".join(st)

def is_digit(word):
    try:
        float(word) if '.' in word else int(word)
        return True
    except ValueError:
        return False

def singularize(word):
    if(word == "is" or word == "was" or word.endswith("ous") or word.endswith("sis") or word.endswith("xis") or word.endswith("ess") or word == ("thus") or word == ("this") or word.endswith("oss") or word.endswith("ass")):
        return word
    if(p.singular_noun(word) != False):
        word = p.singular_noun(word)
    return word

class RAKE:

    def __init__(self):
        self.stopwords = set(nltk.corpus.stopwords.words())
        self.top_fraction = 1 # consider top third candidate keywords by score
    def _generate_candidate_keywords(self, sentences, lower, upper):
        phrase_list = []
        for sentence in sentences:
            words = ["|" if x.lower() in self.stopwords else x for x in nltk.word_tokenize(sentence)]
            for w in range(len(words)):
                words[w] = singularize(words[w])
                words[w] = re.sub('[^A-Za-z|\d\s]+', ' ', words[w])
                words[w] = re.sub(r'_u\d_v\d', '_u%d_v%d', words[w])
            phrase = []
            for word in words:
                if word == "|" or nltk.tag.pos_tag([word])[0][1] == ('IN') or word.endswith("ing") or word.endswith("ed"):
                    if len(phrase) >= lower and len(phrase) <= upper :
                        if nltk.tag.pos_tag(phrase[-1])[0][1].startswith('R'):
                            phrase.pop()
                        phrase_list.append(phrase)
                        phrase = []
                else:
                    if word != " ":
                        phrase.append(word)
        return phrase_list

    def _calculate_word_weights(self, phrase_list):
        word_freq = nltk.FreqDist()
        word_weight = nltk.FreqDist()
        for phrase in phrase_list:
            weight = len([x for x in phrase if not is_digit(x)]) - 1
            for x in range(len(phrase)):
                phrase = [x for x in phrase if x]
                # mess with weighting here
                if(phrase[x].lower() in filter_phrases or phrase[x].lower() == 'surgery' or phrase[x].lower() == 'surgical'): # filter these
                    weight = -10
                if(len(phrase[x]) > 5): #if words more complex, gets higher weighting
                    weight = weight + 1
            for word in phrase:
                word_freq.update([word])
                word_weight[word] += weight
        for word in list(word_freq.keys()):
            word_weight[word] = word_weight[word] + 1.7 * word_freq[word] # Frequency > Complexity
        word_weights = {}
        for word in list(word_freq.keys()):
            word_weights[word] = word_weight[word] / word_freq[word]
        return word_weights

    def _calculate_phrase_scores(self, phrase_list, word_weights):
        phrase_scores = {}
        for phrase in phrase_list:
            phrase_score = 0
            for word in phrase:
                word = singularize(word)
                if(word_weights.get(word) != None):
                    phrase_score += word_weights[word]
            temp =  " ".join(phrase).lower()
            temp = re.sub(' +',' ', temp)
            phrase_scores[temp] = phrase_score
        # Check if two phrases are similar
        for phrase1 in phrase_list:
            for phrase2 in phrase_list:
                s1 = " ".join(phrase1).lower()
                s2 = " ".join(phrase2).lower()
                if s1 == s2:
                    continue
                vector1 = cs.text_to_vector(s1)
                vector2 = cs.text_to_vector(s2)
                cosine = cs.get_cosine(vector1, vector2)
                if(cosine >= .32):
                    if not (phrase_scores.get(s1) == None or phrase_scores.get(s2) == None):
                        if phrase_scores.get(s1) > phrase_scores.get(s2):
                            phrase_scores.pop(s1, None)
                        elif phrase_scores.get(s1) < phrase_scores.get(s2):
                            phrase_scores.pop(s2, None)
        return phrase_scores

    def extract(self, text, lower, upper):
        text = switchAccs(text)
        sentences = nltk.sent_tokenize(text)
        phrase_list = self._generate_candidate_keywords(sentences, lower, upper)
        word_weights = self._calculate_word_weights(phrase_list)
        phrase_scores = self._calculate_phrase_scores(
            phrase_list, word_weights)
        sorted_phrase_scores = sorted(iter(phrase_scores.items()),
                                      key=operator.itemgetter(1), reverse=True)
        n_phrases = len(sorted_phrase_scores)
        return sorted_phrase_scores[0:int(n_phrases/self.top_fraction)]

def test():
    rake = RAKE()
    keywords = rake.extract(sample_text, 1, 3)
    print("Keywords:", keywords)

if __name__ == "__main__":
    test()
