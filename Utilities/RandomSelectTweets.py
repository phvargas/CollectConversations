import sys
import os
import json
import random
from time import strftime, localtime, time

"""
This Python program
    randomly selects documents contained in a JSON file, using as a parameter the file containing the tweets and the number
    of documents to select. 
"""
__author__ = 'Plinio H. Vargas'
__date__ = 'Wed,  Nov 08, 2017 at 12:12:58'
__email__ = 'pvargas@cs.odu.edu'


def select_documents(filename, outfile, amount, corpus_size):
    """
    Parameters used in make_json:
       filename: path of filename where JSON file resides

       :parameter outfile - outfile name containing randomly selected documents

       :parameter amount number of tweets to be randomly selected

       :parameter corpus_size - number of documents in the corpus
    """

    # seed randomness to system time
    random.seed()

    # generate n random numbers
    random_index = set()
    while len(random_index) < amount:
        random_index.add(random.randint(0, corpus_size - 1))

    print(random_index)

    """
    #with open(filename, mode='r', encoding='utf-8') as json_file:
    #    with open(outfile, "w", encoding='utf-8') as f_out:
            data = json.load(json_file)

            counter = 0
            code = 20360
            for account in data:
                for document in account['tweets']:
                    if counter in random_index:
                        print(counter, document[0])
                        code += 1
                        f_out.write("%d\tN\t%s\n" % (code, document[0]))
                    counter += 1
    print('Total number of documents:', counter)
    """
    counter = 0
    code = 15001
    with open(filename, mode='r', encoding='utf-8') as text_file:
        with open(outfile, mode='w', encoding='utf-8') as f_out:
            for document in text_file:
                if counter in random_index:
                    print(counter, document.strip())
                    f_out.write("%d\tN\t%s\n" % (code, document.strip()))
                    code += 1
                counter += 1

    return


if __name__ == '__main__':
    # record running time
    start = time()
    print('Starting Time: %s' % strftime("%a,  %b %d, %Y at %H:%M:%S", localtime()))

    # argument example /data/harassment/tweets/all_tweets.json /data/harassment/tweets/rnd_selected_tweets.dat 100 337341

    # checks for argument
    if len(sys.argv) != 5:
        print('\nUsage: python3 RandomSelectTweets.py <inputfile> <outputfile> <n_selection> <corpus_size>')
        sys.exit(-1)

    infile = sys.argv[1]
    if not os.path.isfile(infile):
        print('\nCould not find document: ', infile)
        print('Usage: python3 RandomSelectTweets.py <inputfile> <outputfile> <n_selection>  <corpus_size>')
        sys.exit(-1)

    out = sys.argv[2]

    try:
        n = int(sys.argv[3])
        size = int(sys.argv[4])

    except ValueError:
        n = sys.argv[3]
        size = sys.argv[4]
        print('\nNumber of randomly selected documents and corpus size MUST be an integer: ', n, size)
        print('Usage: python3 RandomSelectTweets.py <inputfile> <outputfile> <n_selection> <corpus_size>')
        sys.exit(-1)

    select_documents(infile, out, n, size)

    print('\nEnd Time:  %s' % strftime("%a,  %b %d, %Y at %H:%M:%S", localtime()))
    print('Execution Time: %.2f seconds' % (time()-start))
    sys.exit(0)
