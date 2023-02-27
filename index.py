#  Example code in python programming language demonstrating some of the features of an inverted index.
#  In this example, we scan a directory containing the corpus of files. (In this case the documents are reports on articles
#  and authors submitted to the Journal "Communications of the Association for Computing Machinery"  
#
#  In this example we see each file being read, tokenized (each word or term is extracted) combined into a sorted 
#  list of unique terms.  
#
#  We also see the creation of a documents dictionary containing each document in sorted form with an index assigned to it.
#  Each unique term is written out into a terms dictionary in sorted order with an index number assigned for each term.  
#  From our readings we know that to complete teh inverted index all that we need to do is create a third file that will
#  coorelate each term with the list of documents that it was extracted from.  We will do that in a later assignment.
##
#  We can further develop this example by keeping a reference for each term of the documents that it came from and by 
#  developing a list of the documents thus creating the term and document dictionaries. 
#
#  As you work with this example, think about how you might enhance it to assign a unique index number to each term and to 
#  each document and how you might create a data structure that links the term index with the document index. 

import sys,os,re
import time
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from porterstemmer import PorterStemmer
import string




# define global variables used as counters
tokens = 0
documents = 0
terms = 0
termindex = 0
docindex = 0 

# initialize list variable
#
alltokens = []
alldocs = []

#
# Capture the start time of the routine so that we can determine the total running
# time required to process the corpus
#
t2 = time.localtime()   
p = PorterStemmer()
punc_list = string.punctuation

# routines

# identify stop words
def stop_words_clean(alltokens):
  return [sw for sw in alltokens if sw not in stopwords.words('english')]


def stem_words(alltokens):
  newList = []
  for e in alltokens:
    stemmedWord = p.stem(e, 0,len(e)-1)
    newList.append(stemmedWord)

  return newList

def rm_punctuation(alltokens):
  newList = []
  for e in alltokens:
    if(e[0] not in punc_list):
      newList.append(e)

  return newList

def word_dict(alltokens):
  wordSet = set(alltokens)
  dict1 = dict.fromkeys(wordSet, 0) 
  for i in alltokens:
      dict1[i] += 1
  return dict1

def compute_TF(wordDict, alltokens):
    tfDict = {}
    bowCount = len(alltokens)
    for word, count in wordDict.items():
        tfDict[word] = count/float(bowCount)
    return tfDict

def compute_IDF(docList):
    import math
    idfDict = {}
    N = len(docList)
    
    idfDict = dict.fromkeys(docList[0].keys(), 0)
    for doc in docList:
        for word, val in doc.items():
            if val > 0:
                idfDict[word] += 1
    
    for word, val in idfDict.items():
        idfDict[word] = math.log10(N / float(val))
        
    return idfDict

def compute_TFIDF(tf, idfs):
    tfidf = {}
    for word, val in tf.items():
        tfidf[word] = val*idfs[word]
    return tfidf

# set the name of the directory for the corpus
#
dirname = "cacm"

# For each document in the directory read the document into a string
#
all = [f for f in os.listdir(dirname)]
for f in all:
    documents+=1
    with open(dirname+'/'+f, 'r') as myfile:
        alldocs.append(f)
        data=myfile.read().replace('\n', '')  
        for token in data.split():
            alltokens.append(token)
            tokens+=1

alltokens_cl = stop_words_clean(alltokens=alltokens)

words_matched_stop = len(alltokens) - len(alltokens_cl)


alltokens = rm_punctuation(alltokens=alltokens_cl)
alltokens = stem_words(alltokens=alltokens)
wordDict = word_dict(alltokens)
termFreq = compute_TF(wordDict, alltokens)

idf = compute_IDF([wordDict])
td_idf = compute_TFIDF(termFreq, idf)

##print(td_idf, "The final output");
# Open for write a file for the document dictionary
#
documentfile = open(dirname+'/'+'documents.dat', 'w')
alldocs.sort()
for f in alldocs:
  docindex += 1
  documentfile.write(f+','+str(docindex)+os.linesep)
documentfile.close()

#
# Sort the tokens in the list
alltokens.sort()

#
# Define a list for the unique terms  
g=[]

#
# Identify unique terms in the corpus
for i in alltokens:    
    if i not in g:
       g.append(i)
       terms+=1

##terms = len(g)

# Output Index to disk file. As part of this process we assign an 'index' number to each unique term.  
# 
indexfile = open(dirname+'/'+'index.dat', 'w')
for i in g:
  termindex += 1
  indexfile.write(i+','+str(termindex)+os.linesep)
indexfile.close()


# Print metrics on corpus
#
print('Processing Start Time: %.2d:%.2d' % (t2.tm_hour, t2.tm_min))
print("Documents %i" % documents)
print("Tokens %i" % tokens)
print("Terms %i" % terms)
print("Total number that matched the stop words %i" % words_matched_stop)
t2 = time.localtime()   
print ('Processing End Time: %.2d:%.2d' % (t2.tm_hour, t2.tm_min))


