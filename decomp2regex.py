# Convert decomposition rules from notation used in ELIZA paper to standard regex

import re

def decomp_to_regex(in_str, tags):
    """
    Parameters
    ----------

    Returns
    -------
    """
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
            w = r'(?:\b\w+\b[\s\r\n]*){' + w + '}'
        # A word starting with @ signifies a tag
        elif w[0] == "@":
            # Get tag name
            tag_name = w[1:].lower()
            w = ''
            if tag_name in tags:
                # Make a regex separating each option with OR operator e.g. x|y|z
                for synonym in tags[tag_name]:
                    w += synonym + '|'
                # Remove last |
                w = w[:-1]
                # Add word boundaries
                w = r'\b(' + w + r')\b'
        else:
            # Add word boundaries to match on a whole word basis
            w = r'\b' + w + r'\b'
        
        # Parentheses are needed to properly divide sentence into components
        # \s* matches zero or more whitespace characters 
        out_str += '(' + w + r')\s*' 

    return out_str


