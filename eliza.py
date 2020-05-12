import os
import re
import json

from decomp2regex import decomp_to_regex

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_PATH = os.path.join(PROJECT_DIR, 'doctor.json')

def load_script(script_path):
    """Loads script from JSON file."""
    # Load script
    with open(SCRIPT_PATH) as f:
        script = json.load(f)
    
    # Convert decomposition rules to regex notation
    for d in script:
        for rule in d['rules']:
            rule['decomp'] = decomp_to_regex(rule['decomp']) 

    return script



#def load_ranks(script):
#    """Load ranks from script. """
#    ranks = {}
#    for d in script:
#        ranks[d['keyword']] = d['rank']
#    return ranks

def rank(in_str, script):
    """Rank keywords according to script.
    Returns descending sorted list of keywords."""
    keywords = in_str.split()

    ranks = []

    # Populate list of ranks
    for keyword in keywords:
        for d in script:
            if d['keyword'] == keyword:
                ranks.append(d['rank'])
                break
        # If no rank has been specified for a word, set its rank to 0
        else:
            ranks.append(0)
 
    # Sort list of keywords according to list of ranks
    return [x for _,x in sorted(zip(ranks, keywords), reverse=True)]

def decompose(keyword, in_str, script):
    """Find matching decomposition rule for a given keyword.
    If a matching decomposition rule is found, 
    it returns a list of components broken down according to the decomposition rule,
    along with the reassembly rule to use.
    If a matching decomposition rule is not found,
    it returns an empty string.
    """

    for d in script: # Cycle through elements in script
        if d['keyword'] == keyword: # If keyword matches
            for rule in d['rules']: # Cycle through decomp rules for that keyword
                if re.match(rule['decomp'], in_str): # If decomp rule matches
                    reassembly_rule = rule['reassembly'][last]
                    break
            break


# Load script
script = load_script(SCRIPT_PATH)

print(script)

# Get first user input
in_str = input("Welcome.\n")

while True:
    # Sort keys based on rank
    sorted_keywords = rank(in_str, script)
    print(sorted_keywords)

    # Find a matching decomposition rule
    for keyword in sorted_keywords:
        decompose(keyword, in_str)


    # Get next user input
    in_str = input(response)