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
    it returns an empty list and an empty string.
    """

    comps = []
    reassembly_rule = ''

    # Cycle through elements in script
    for d in script: 
        if d['keyword'] == keyword:
            # Cycle through decomp rules for that keyword
            for rule in d['rules']:
                m = re.match(rule['decomp'], in_str, re.IGNORECASE)
                # If decomp rule matches
                if m:
                    # Decompose string according to decomposition rule
                    comps = list(m.groups())
                    # Get reassembly rule
                    reassembly_rule = rule['reassembly'][rule['last_used_reassembly_rule']]
                    # Update last used reassembly rule ID
                    next_id = rule['last_used_reassembly_rule']+1
                    # If all reassembly rules have been used, start over
                    if next_id >= len(rule['reassembly']):
                        next_id = 0
                    rule['last_used_reassembly_rule'] = next_id
                    break
            break

    return comps, reassembly_rule

def reassemble(components, reassembly_rule):
    """Reassemble a list of strings given a reassembly rule.
    Note: reassembly rules are 1-indexed, according to the original paper.
    """

    response = 'Eliza: '

    # Split reassembly rule into its components
    reassembly_rule = reassembly_rule.split() 

    for comp in reassembly_rule:
        if comp.isnumeric():
            response += components[int(comp)] + " "
        else:
            response += comp + " "

    # Substitute trailing space with newline
    response = response[:-1] + "\nYou: "

    return response

# Load script
script = load_script(SCRIPT_PATH)

# Get first user input
in_str = input("Eliza: Welcome.\nYou: ")

while True:
    # Sort keys based on rank
    sorted_keywords = rank(in_str, script)

    # Find a matching decomposition rule
    for keyword in sorted_keywords:
        comps, reassembly_rule = decompose(keyword, in_str, script)
        # Break if matching decomposition rule has been found
        if comps:
            break

    response = reassemble(comps, reassembly_rule)

    # Get next user input
    in_str = input(response)