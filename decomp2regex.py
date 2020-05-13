# Convert decomposition rules from notation used in ELIZA paper to standard regex

import re

def decomp_to_regex(in_str, general_script):
    out_str = ''

    # The input is of the form: e.g. (0 YOU 0)
    # Strip parenthesis
    in_str = re.sub('[()]', '', in_str)

    # Split string into space separated list
    in_str = in_str.split()

    for w in in_str:
        # 0 means "an indefinite number of words"
        if w == '0': 
            w = '.*'
        # A positive non-zero integer means "this specific amount of words"
        elif w.isnumeric() and int(w) > 0:
            w = '(?:\b\w+\b[\s\r\n]*){' + w + '}'
        # A word starting with @ signifies a tag
        elif w[0] == "@":
            # Get tag name
            tag_name = w[1:]
            w = ''
            if tag_name in general_script['tags']:
                for synonym in general_script['tags'][tag_name]:
                    w += synonym + '|'
            # Make a regex separating each option with OR operator e.g. x|y|z
        
        out_str += '(' + w + ')\s*'

    return out_str


