"""
This file contains an example search engine that will search the inverted index that we build as part of our assignments in units 3 and 5.
"""
import sys,os,re
import math
import sqlite3
import time

# use simple dictionary data structures in Python to maintain lists with hash keys
docs = {}
resultslist = {}
term = {}

# regular expression or: extract words, extract ID rom path, check or hexa value
chars = re.compile(r'\W+')
pattid= re.compile(r'(\d{3})/(\d{3})/(\d{3})')

#
# Docs class: Used to store information about each unit document. In this is the Term object which stores each
# unique instance of termid or a docid.
#
class Docs():
    terms = {}

#
# Term class: used to store information or each unique termid
#
class Term():
    docfreq = 0
    termfreq = 0
    idf = 0.0
    tfidf = 0.0

# split on any chars
def splitchars(line) :
    return chars.split(line)

# this small routine is used to accumulate query idf values
def elenQ(elen, a):
    return(float(math.pow(a.idf ,2))+ float(elen))

# this small routine is used to accumulate document tfidf values
def elenD(elen, a):
    return(float(math.pow(a.tfidf ,2))+ float(elen))



"""
================================================================================================
>>> main

This section is the 'main' or starting point o the indexer program. The python interpreter will find this 'main' routine and execute it first.
================================================================================================
"""
if __name__ == '__main__':
#
# Create a sqlite database to hold the inverted index. The isolation_level statement turns
# on autocommit which means that changes made in the database are committed automatically
#
    con = sqlite3.connect("indexer_part2.db") 
    con.isolation_level = None
    cur = con.cursor()

    #
    #
    #
    line = input('Enter the search terms, each separated by a space: ')

    #
    # Capture the start time of the search so that we can determine the total running
    # time required to process the search
    #
  
    t2 = time.localtime() 
    print('Processing Start Time: %.2d:%.2d:%.2d' % (t2.tm_hour, t2.tm_min, t2.tm_sec))
    

    #
    # This routine splits the contents of the line into tokens
    l = splitchars(line)

    #
    # Get the total number of documents in the collection
    #
    q = "select count(*) from documentdictionary"
    cur.execute(q)
    row = cur.fetchone()
    documents = row[0]

    # Initialize maxterms variable. This will be used to determine the maximum number of search
    # terms that exists in any one document.
    #
    maxterms = float(0)

    # process the tokens (search terms) entered by the user
    for elmt in l:
        # This statement removes the newline character if found
        elmt = elmt.replace('\n','')
        # This statement converts all letters to lower case
        lowerElmt = elmt.lower().strip()

        #
        # Execute query to determine if the term exists in the dictionary
        #
        q = "select count(*) from TermDictionary where term = '%s'" % (lowerElmt)
        cur.execute(q)
        row = cur.fetchone()

        #
        # If the term exists in the dictionary retrieve all documents for the term and store in a list
        #
        if row[0] > 0:
            q = "select distinct docid, tfidf, docfreq, termfreq, posting.termid from termdictionary,posting where posting.termid = termdictionary.termid and term = '%s' order by docid, posting.termid" % (lowerElmt)

            cur.execute(q)
            for row in cur:
                i_termid = row[4]
                i_docid = row[0]

                if not ( i_docid in docs.keys()):
                     docs[i_docid] = Docs()
                     docs[i_docid].terms = {}

                if not (i_termid in docs[i_docid].terms.keys()):
                    docs[i_docid].terms[i_termid] = Term()
                    docs[i_docid].terms[i_termid].docfreq = row[2]
                    docs[i_docid].terms[i_termid].termfreq = row[3]
                    docs[i_docid].terms[i_termid].idf = 0.0
                    docs[i_docid].terms[i_termid].tfidf = 0.0

    # Calculate tfidf values for both the query and each document
    # Using the tfidf (or weight) value, accumulate the vectors and calculate
    # the cosine similarity between the query and each document

    # Calculate tf-idf values for query
    query_tfidf = {}
    for term in l:
        # Calculate tf value
        tf = l.count(term) / len(l)
        
        # Calculate idf value

        q = "select count(*) from TermDictionary where term = '%s'" % (lowerElmt)
        cur.execute(q)
        row = cur.fetchone()

        idf = math.log(len(docs) / row[0])
        # Calculate tf-idf value
        tfidf = tf * idf
        # Add tf-idf value to query vector
        query_tfidf[term] = tfidf

    # Calculate tf-idf values for each document
    document_tfidf = {}
    for doc_id in docs:
        document_tfidf[doc_id] = {}
        for term in l:
            if term in docs[doc_id].terms:
                # Calculate tf value
                tf = docs[doc_id].terms[term].termfreq / docs[doc_id].terms[term].docfreq
                # Calculate idf value
                idf = math.log(len(docs) / docs[doc_id].terms[term].docs)
                # Calculate tf-idf value
                tfidf = tf * idf
                # Add tf-idf value to document vector
                document_tfidf[doc_id][term] = tfidf

    # Calculate cosine similarity between query and each document
    cosine_similarity = {}
    for doc_id in document_tfidf:
        # Calculate dot product of query and document vectors
        dot_product = sum(query_tfidf[term] * document_tfidf[doc_id][term] for term in query_tfidf if term in document_tfidf[doc_id])
        # Calculate magnitudes of query and document vectors
        query_magnitude = math.sqrt(sum(query_tfidf[term] ** 2 for term in query_tfidf))
        document_magnitude = math.sqrt(sum(document_tfidf[doc_id][term] ** 2 for term in document_tfidf[doc_id]))
        # Calculate cosine similarity
        try:
            cosine_similarity[doc_id] = dot_product / (query_magnitude * document_magnitude)
        except:
            cosine_similarity[doc_id] = 0

    #
    # Calculate the denominator which is the euclidean length of the query
    # multiplied by the euclidean length of the document
    #

    query_length = math.sqrt(sum([i**2 for i in query_tfidf.values()]))

    doc_terms = docs[doc_id].terms.keys()
    doc_length = 0.0

    for term_id in doc_terms:
        term_freq = docs[doc_id].terms[term_id].termfreq
        doc_freq = docs[doc_id].terms[term_id].docfreq
        idf = docs[doc_id].terms[term_id].idf
        tfidf = term_freq * idf
        doc_length += tfidf**2

    doc_length = math.sqrt(doc_length)

    #
    # This search engine will match on any number of terms and the cosine similarity of a
    # document matches on 1 term that appears in a document in the collection tends to score highly
    # the float(no_terms/maxtersm) portion of the equation is designed to give a higher weight
    # to documents that match on more than 1 term in queries that have multiple terms.
    # The remainder of the equation calculates the cosine similarity
    #
    for doc in cosine_similarity:
        print(cosine_similarity[doc])

    #
    # Sort the results found in order of decreasing cosine similarity. Because we cannot use a float
    # value as an index to a list, I multiplied the cosine similarity value by 10,000 and converted
    # to an integer. For example i the cosine similarity was calculated to be .98970 multiplying
    # it by 10,000 would produce 9897.0 and converting to an integer would result in 9897 which can be
    # used as an index that we can then sort in reverse order.   To display the cosine similarity
    # correctly in the results list we simply convert it back to a float value and divide by 10,000
    #

    keylist = resultslist.keys()

    # sort in descending order
    keylist.sort(reverse=True)
    i = 0

    for key in keylist:
        i += 1
        if i > 20:
            continue
        q = "select DocumentName from documentdictionary where docid = %d" % (resultslist[key])
        cur.execute(q)
        row = cur.fetchone()
        print('Document: %s Has Relevance o %f' % (row[0], float(key)/10000))
    con.close()

#
# Print ending time to show the processing duration of the query.
#
t2 = time.localtime()
print('End Time: %.2d:%.2d:%.2d' % (t2.tm_hour, t2.tm_min, t2.tm_sec))