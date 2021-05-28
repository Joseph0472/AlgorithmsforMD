import random

DOC_COUNT = 3430 #hardcoded since we already knew the values for this assignment beforehand 
WORD_COUNT = 6906
D = 100 #number of hash functions 
BANDS = 25
ROWS = 4
P = 19540663 #using https://primes.utm.edu/nthprime/index.php#nth
AB = [(random.randrange(0, P), random.randrange(0, P)) for i in range(D)] #generates a and b values
HASH_FUNCTIONS = [[0 for j in range(WORD_COUNT + 1)] for i in range(D)] # HASH_FUNCTIONS[i][wordID] for h_i(wordID)
DOCUMENTS_SET = [set() for i in range(DOC_COUNT + 1)] #0 element is empty but makes it nicer to access DOCUMENTS_SET[docID].
JACCARD = [[0 for j in range(DOC_COUNT + 1)] for i in range(DOC_COUNT + 1)] #0 element is empty but makes it nicer to access JACCARD[docID]. Always use JACCARD[min][max]. 
ESTIMATE = [[0 for j in range(DOC_COUNT + 1)] for i in range(DOC_COUNT + 1)] #0 element is empty but makes it nicer to access ESTIMATE[docID]. Always use ESTIMATE[min][max].
SIGNATURES = [[WORD_COUNT + 1 for j in range(D)] for i in range(DOC_COUNT + 1)] #SIGNATURES[docID][i] to get docID signature at hash function i
BANDS_HASH = [[] for i in range(DOC_COUNT * 1000)] # A large number to minimise collisions at the cost of space. 
CANDIDATE_PAIRS = [set() for i in range(DOC_COUNT + 1)] #CANDIDATE_PAIRS[docID] to get set of cand. pairs

def process():
    with open('kos.txt') as myfile: #All really straightforward stuff - reads line by line and generates a list of lists. I deleted the first 3 lines of my .txt file. 
        line = myfile.readline()
        while line:
            tokens = line.split()
            DOCUMENTS_SET[int(tokens[0])].add(int(tokens[1]))
            line = myfile.readline()

def jaccard(doc1, doc2):
    intersection_count = len(doc1.intersection(doc2))
    union_count = len(doc1) + len(doc2) - intersection_count
    return intersection_count / union_count

def bruteforce(): #not the fastest but it get's the job done, so i didn't really bother with optimising
    avgsum = 0
    count = 0
    with open('bruteforce.txt', 'w') as writefile:
        for i in range(1, len(DOCUMENTS_SET)):
            doc1 = DOCUMENTS_SET[i]
            for j in range(i + 1, len(DOCUMENTS_SET)):
                doc2 = DOCUMENTS_SET[j]
                JACCARD[i][j] = jaccard(doc1, doc2)
                avgsum += JACCARD[i][j]
                count += 1
                writefile.write('{} '.format(round(JACCARD[i][j], 4)))
            writefile.write('\n')
    print("Average Jaccard Similarity: {}".format(avgsum/count, 4))

def generate_signatures(): #generate a signature per hash function for each document 
    for i in range(D):
        a,b = AB[i]
        for j in range(1, len(DOCUMENTS_SET)):
            current = SIGNATURES[j][i]
            for word in DOCUMENTS_SET[j]:
                h = ((a * word + b) % P) % WORD_COUNT
                if h < current:
                    current = h
            SIGNATURES[j][i] = current

def compare_signatures(): #code to generate estimate values off signature comparisons between document pairs 
    for i in range(1, len(ESTIMATE)):
        for j in range(i + 1, len(ESTIMATE)):
            sig1 = SIGNATURES[i]
            sig2 = SIGNATURES[j]
            count = 0
            for k in range(D):
                if sig1[k] == sig2[k]:
                    count += 1
            ESTIMATE[i][j] = count/D

def get_mae(): #code to calculate the MAE values for q3
    mysum = 0
    for i in range(1, len(JACCARD)):
        for j in range(i + 1, len(JACCARD)):
            mysum += abs(JACCARD[i][j] - ESTIMATE[i][j])
    print('MAE for D = {}: {}'.format(D, mysum/(DOC_COUNT * (DOC_COUNT - 1) * 0.5)))

def get_candidate_pairs(): #code for q4 implementing LSH, by taking a band att a time, and hashing the rows inside that band into a very large hash table (one hash per document) 
    A = [random.randrange(0, P) for x in range(ROWS)]
    for band in range(BANDS):
        BANDS_HASH = [[] for i in range(DOC_COUNT * 10000)] # reset this for every band to save space
        for docID in range(1, len(SIGNATURES)):
            hashval = 0
            for row in range(ROWS):
                i = band * ROWS + row
                hashval += SIGNATURES[docID][i] * A[row]
            hashval = (hashval % P) % len(BANDS_HASH)
            BANDS_HASH[hashval].append(docID)
        for bucket in BANDS_HASH:
            if not len(bucket) > 1:
                continue
            else:
                for i in range(len(bucket)):
                    candidates = bucket[:i] + bucket[i+1:]
                    for c in candidates:
	                    CANDIDATE_PAIRS[bucket[i]].add(c) 

def run_tests(): #code to calculate the values for q4 e.g. false candidacy etc - rather straightforward (counts x and y then gives x/y)
    num_pairs = 0
    num_bad_pairs = 0
    for docID in range(1, len(CANDIDATE_PAIRS)):
        pairs = CANDIDATE_PAIRS[docID]
        num_pairs += len(pairs)
        for pair in pairs:
            if JACCARD[min(docID, pair)][max(docID, pair)] < 0.6:
                num_bad_pairs += 1
    print('{}/{} = {}'.format(num_bad_pairs, num_pairs, round(num_bad_pairs/num_pairs, 4)))  

    num_pairs = 0
    num_bad_pairs = 0
    for docID in range(1, len(CANDIDATE_PAIRS)):
        pairs = CANDIDATE_PAIRS[docID]
        for pair in pairs:
            if JACCARD[min(docID, pair)][max(docID, pair)] <= 0.3:
                num_bad_pairs += 1
        
        for j in range(docID + 1, len(CANDIDATE_PAIRS)):
            if JACCARD[docID][j] <= 0.3:
                num_pairs += 1
    
    num_pairs = num_pairs * 2 #since we count the bad_pairs twice e.g. ij and ji, but the overall pairs once i.e ij.   
    print('{}/{} = {}'.format(num_bad_pairs, num_pairs, round(num_bad_pairs/num_pairs, 4)))          



#process()
#bruteforce()
#generate_signatures()
#get_candidate_pairs()
#compare_signatures()
#get_mae()
#run_tests()

    

