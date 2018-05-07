import sys
import os
import csv
import json
from time import strftime, localtime, time

"""
This Python program
    converts csv text format into a json format
"""
__author__ = 'Plinio H. Vargas'
__date__ = 'Wed,  Oct 18, 2017 at 20:22:53'
__email__ = 'pvargas@cs.odu.edu'


def make_json(filename):
    """
    Parameters used in make_json:
       filename: path of filename where csv format resides
    """

    counter = 0
    json_obj = []
    json_title = []
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            counter += 1
            json_row = {}

            if counter == 1:
                for title in row:
                    json_title.append(title)
            else:
                idx = 0
                for value in row:
                    # if key is the name or handle DO NOT lower case value
                    if json_title[idx].lower() == 'name' or json_title[idx].lower() == 'handle':
                        json_row[json_title[idx].lower()] = value
                    else:
                        json_row[json_title[idx].lower()] = value.lower()

                    idx += 1

                json_obj.append(json_row)

            print(', '.join(row))

    print(json.dumps(json_obj, sort_keys=True, indent=4))
    fhs = open('ConversationHarassment.dat', 'w')
    json.dump(json_obj, fhs, sort_keys=True, indent=4)
    fhs.close()

    fhs = open('ConversationHarassment.dat', 'r')
    test = json.load(fhs)

    print(test)
    return


if __name__ == '__main__':
    # record running time
    start = time()
    print('Starting Time: %s' % strftime("%a,  %b %d, %Y at %H:%M:%S", localtime()))

    # checks for argument
    if len(sys.argv) != 2:
        print('Usage: python3 MakeJSON.py <filename>')
        sys.exit(-1)

    infile = sys.argv[1]
    if not os.path.isfile(infile):
        print('\nCould not find document: ', infile)
        print('Usage: python3 MakeJSON.py <filename>')
        sys.exit(-1)

    make_json(infile)

    print('\nEnd Time:  %s' % strftime("%a,  %b %d, %Y at %H:%M:%S", localtime()))
    print('Execution Time: %.2f seconds' % (time()-start))
    sys.exit(0)
