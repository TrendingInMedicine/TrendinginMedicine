# Ankur Mishra
# 2018amishra@gmail.com
# Adapted from: http://sujitpal.blogspot.jp/2013/03/implementing-rake-algorithm-with-nltk.html to work with python and singularizes words
import operator
import nltk
import string
import inflect
from string import digits
import re

p = inflect.engine()

def isPunct(word):
  return len(word) == 1 and word in string.punctuation

def isNumeric(word):
  try:
    float(word) if '.' in word else int(word)
    return True
  except ValueError:
    return False

class RakeKeywordExtractor:

  def __init__(self):
    self.stopwords = set(nltk.corpus.stopwords.words())
    self.top_fraction = 1 # consider top third candidate keywords by score
  def _singularize(self, word):
    if(word.endswith("ous") == True or word.endswith("sis") == True or word.endswith("xis") == True):
        return word
    if(p.singular_noun(word) != False):
        word = p.singular_noun(word)
    return word
  def _generate_candidate_keywords(self, sentences, lower, upper):
    phrase_list = []
    for sentence in sentences:
    #   print(sentence)
      words = ["|" if x in self.stopwords else x for x in nltk.word_tokenize(sentence.lower())]
      for w in range(len(words)):
          words[w] = self._singularize(words[w])
          words[w] = re.sub('[^A-Za-z|\d\s]+', '', words[w])
        #   print([words[w]])
      #print("Words", words)
      phrase = []
      for word in words:
        if word == "|" or isPunct(word):
          if len(phrase) >= lower and len(phrase) <= upper:
            phrase_list.append(phrase)
            phrase = []
        else:
          phrase.append(word)
    return phrase_list

  def _calculate_word_scores(self, phrase_list):
    word_freq = nltk.FreqDist()
    word_degree = nltk.FreqDist()
    for phrase in phrase_list:
      degree = len([x for x in phrase if not isNumeric(x)]) - 1
      for word in phrase:
        word_freq.update([word])
        word_degree[word] += degree
        # word_degree.update([word], degree) # other words
    for word in list(word_freq.keys()):
      word_degree[word] = word_degree[word] + word_freq[word] # itself
    # word score = deg(w) / freq(w)
    word_scores = {}
    for word in list(word_freq.keys()):
      word_scores[word] = word_degree[word] / word_freq[word]
    return word_scores

  def _calculate_phrase_scores(self, phrase_list, word_scores):
    phrase_scores = {}
    for phrase in phrase_list:
      phrase_score = 0
      for word in phrase:
        phrase_score += word_scores[word]
      phrase_scores[" ".join(phrase)] = phrase_score
    return phrase_scores

  def extract(self, text, lower, upper, incl_scores=False):
    sentences = nltk.sent_tokenize(text)
    phrase_list = self._generate_candidate_keywords(sentences, lower, upper)
    word_scores = self._calculate_word_scores(phrase_list)
    phrase_scores = self._calculate_phrase_scores(
      phrase_list, word_scores)
    sorted_phrase_scores = sorted(iter(phrase_scores.items()),
      key=operator.itemgetter(1), reverse=True)
    n_phrases = len(sorted_phrase_scores)
    if incl_scores:
      return sorted_phrase_scores[0:int(n_phrases/self.top_fraction)]
    else:
      return [x[0] for x in sorted_phrase_scores[0:int(n_phrases/self.top_fraction)]]

def test():
  rake = RakeKeywordExtractor()
  keywords = rake.extract("""
The use of contralateral prophylactic mastectomies (CPMs) among patients with invasive unilateral breast cancer has increased substantially during the past decade in the United States despite the lack of evidence for survival benefit. However, whether this trend varies by state or whether it is correlated with changes in proportions of reconstructive surgery among these patients is unclear.To determine state variation in the temporal trend and in the proportion of CPMs among women with early-stage unilateral breast cancer treated with surgery.A retrospective cohort study of 1.2 million women 20 years of age or older diagnosed with invasive unilateral early-stage breast cancer and treated with surgery from January 1, 2004, through December 31, 2012, in 45 states and the District of Columbia as compiled by the North American Association of Central Cancer Registries. Data analysis was performed from August 1, 2015, to August 31, 2016.Contralateral prophylactic mastectomy.Temporal changes in the proportion of CPMs among women with early-stage unilateral breast cancer treated with surgery by age and state, overall and in relation to changes in the proportions of those who underwent reconstructive surgery.Among the 1 224 947 women with early-stage breast cancer treated with surgery, the proportion who underwent a CPM nationally increased between 2004 and 2012 from 3.6% (4013 of 113 001) to 10.4% (12 890 of 124 231) for those 45 years or older and from 10.5% (1879 of 17 862) to 33.3% (5237 of 15 745) for those aged 20 to 44 years. The increase was evident in all states, although the magnitude of the increase varied substantially across states. For example, among women 20 to 44 years of age, the proportion who underwent a CPM from 2004-2006 to 2010-2012 increased from 14.9% (317 of 2121) to 24.8% (436 of 1755) (prevalence ratio [PR], 1.66; 95% CI, 1.46-1.89) in New Jersey compared with an increase from 9.8% (162 of 1657) to 32.2% (495 of 1538) (PR, 3.29; 95% CI, 2.80-3.88) in Virginia. In this age group, CPM proportions for the period from 2010 to 2012 were over 42% in the contiguous states of Nebraska, Missouri, Colorado, Iowa, and South Dakota. From 2004 to 2012, the proportion of reconstructive surgical procedures among women aged 20 to 44 years who were diagnosed with early-stage breast cancer and received a CPM increased in many states; however, it did not correlate with the proportion of women who received a CPM.The increase in the proportion of CPMs among women with early-stage unilateral breast cancer treated with surgery varied substantially across states. Notably, in 5 contiguous Midwest states, nearly half of young women with invasive early-stage breast cancer underwent a CPM from 2010 to 2012. Future studies should examine the reasons for the geographic variation and increasing trend in the use of CPMs.
  """, 1, 3, incl_scores=True)
  print("Keywords:", keywords)

if __name__ == "__main__":
  test()
