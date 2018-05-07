import os
import re
import sys

if len(sys.argv) < 2:
    print('Usage: python3 ScrapeDictionary.py <input_file> <out_file>')
    sys.exit(-1)

doc = sys.argv[1]
out_file = sys.argv[2]
if not os.path.isfile(doc):
    print('Could not find file: ', doc)
    print('Usage: python3 ScrapeDictionary.py <input_file> <out_file>')

derogatory_regex = re.compile('<dt>.*</dt>')
remove_dt_tag = re.compile('(^<dt>)(.*)(</dt>)')
remove_a_tag = re.compile('(<a .*>)(.*)(</a>)')
terms = []
with open(doc, mode='r') as in_file:
    for term in in_file:
        # get all dt tags
        is_a_term = derogatory_regex.search(term)

        # remove dt tags
        if is_a_term:
            is_a_term = remove_dt_tag.sub(remove_dt_tag.match(is_a_term.group(0)).group(2), is_a_term.group(0))

            has_a_tags = remove_a_tag.search(is_a_term)

            # remove a tags
            if has_a_tags:
                has_a_tags = has_a_tags.group(2)
                terms.append(has_a_tags)

            else:
                for value in is_a_term.split('/'):
                    if value.strip() != '':
                        terms.append(value.strip())


for term in terms:
    print(term)
