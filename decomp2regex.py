# Convert decomposition rules from notation used in ELIZA paper to standard regex

import re

def decomp_to_regex(in_str):
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
        
        out_str = out_str + w + ' '

    # Remove trailing space
    out_str = out_str[:-1]

    return out_str


