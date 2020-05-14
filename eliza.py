import os
import re
import json

from decomp2regex import decomp_to_regex

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
GENERAL_SCRIPT_PATH = os.path.join(PROJECT_DIR, 'general.json')
SCRIPT_PATH = os.path.join(PROJECT_DIR, 'doctor.json')

def load_script(script_path):
    """Loads script from JSON file."""
    # Load script
    with open(script_path) as f:
        script = json.load(f)
    return script

def process_decomp_rules(script, general_script):
    # Convert decomposition rules to regex notation
    for d in script:
        for rule in d['rules']:
            rule['decomp'] = decomp_to_regex(rule['decomp'], general_script) 
    return script

def get_exit_inputs(general_script):
    return general_script['exit_inputs']

def substitute(in_str, general_script):
    out_str = ''
    for word in in_str.split():
        word = word.lower()
        if word in general_script['substitutions']:
            out_str += general_script['substitutions'][word] + ' '
        else:
            out_str += word + ' '

    return out_str

def rank(in_str, script, general_script):
    """Rank keywords according to script.
    Only considers sentence with highest ranked word.
    Returns the actual sentence with hgihest ranked word,
    and the descending sorted list of keywords for that sentence."""

    # Break down input into punctuation-delineated sentences
    sentences = re.split(r'[.,!?](?!$)', in_str)

    all_keywords = []
    all_ranks = []
    maximums = []

    # Iterating using index so that sentences in the list can be modified directly
    for i in range(0, len(sentences)):
        sentences[i] = re.sub(r'[#$%&()*+,-./:;<=>?@[\]^_{|}~]', '', sentences[i])
        print("iterating")
        print(sentences[i])

        sentences[i] = substitute(sentences[i], general_script)

        # Check if sentence is not empty at this point
        if sentences[i]:
            keywords = sentences[i].lower().split()
            all_keywords.append(keywords)
            print(keywords)
            
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

            maximums.append(max(ranks))

        all_ranks.append(ranks)
        
    # Return earliest sentence with highest keyword rank
    max_rank = max(maximums)
    max_index = maximums.index(max_rank)
    
    keywords = all_keywords[max_index]
    ranks = all_ranks[max_index]

    # Sort list of keywords according to list of ranks
    sorted_keywords = [x for _,x in sorted(zip(ranks, keywords), reverse=True)]
    
    print(sentences[max_index], sorted_keywords)

    return sentences[max_index], sorted_keywords

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
        # If comp is a number, then place the equivalent component
        if comp.isnumeric():
            response += components[int(comp)-1] + " "
        else:
            response += comp + " "

    # Remove trailing space
    response = response[:-1]

    return response

memory_stack = []

# Load scripts
general_script = load_script(GENERAL_SCRIPT_PATH)
exit_inputs = get_exit_inputs(general_script)
script = load_script(SCRIPT_PATH)
script = process_decomp_rules(script, general_script)

# Get first user input
in_str = input("Eliza: Welcome.\nYou: ")

while in_str not in exit_inputs:

    # str.upper().isupper() is a fast way of checking
    # if a string contains any characters of the alphabet.
    # Source: https://stackoverflow.com/a/59301031
    if not in_str.upper().isupper():
        in_str = input('Eliza: Please, use letters. I am human, after all.\nYou:')
        continue

    # Substitute words if necessary
    #in_str = substitute(in_str, general_script)

    # Get sentence in input with highest ranked word and sort keywords by rank
    sentence, sorted_keywords = rank(in_str, script, general_script)

    # Find a matching decomposition rule
    for keyword in sorted_keywords:
        comps, reassembly_rule = decompose(keyword, sentence, script)
        # Break if matching decomposition rule has been found
        if comps:
            # For certain keywords, generate an additional response to push onto memory stack
            if keyword == 'your':
                mem_comps, mem_reassembly_rule = decompose('^', sentence, script)
                mem_response = reassemble(mem_comps, mem_reassembly_rule)
                memory_stack.append(mem_response)
            response = reassemble(comps, reassembly_rule)
            break
    # If no matching decomposition rule has been found
    else:
        # If memory stack is not empty,
        # assemble an answer relevant to past input
        if memory_stack:
            response = memory_stack.pop()
        # Otherwise, respond with a generic answer
        else:
            comps, reassembly_rule = decompose('$', '$', script)
            response = reassemble(comps, reassembly_rule)

    # Clean up response
    # Remove extra whitespaces
    response = ' '.join(response.split())
    # Remove whitespaces before punctuation
    response = re.sub(r'\s([?.!"](?:\s|$))', r'\1', response)

    response += "\nYou: "

    # Get next user input
    in_str = input(response)

print("ELIZA: Goodbye.\n")