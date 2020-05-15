import os
import re
import json

from decomp2regex import decomp_to_regex

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_DIR = os.path.join(PROJECT_DIR, 'scripts')
GENERAL_SCRIPT_PATH = os.path.join(SCRIPT_DIR, 'general.json')
SCRIPT_PATH = os.path.join(SCRIPT_DIR, 'doctor.json')

def setup():
    """Set up the program, loading the JSON scripts.
    
    Returns
    -------
    general_script : dict
        General script, containing information about language and tags.
    script : dict[]
        Custom script, containing keywords, ranks, decomposition and reassembly rules.
    memory_inputs : str[]
        Array of keywords that prompt the generation of an additional response added to the memory stack.
    exit_inputs : str[]
        array of keywords that can be used to quit the program

    """
    # Load scripts
    general_script = load_script(GENERAL_SCRIPT_PATH)
    script = load_script(SCRIPT_PATH)
    
    # Process decomposition rules in custom script
    script = process_decomp_rules(script, general_script['tags'])
    
    # Get information needed for program execution
    memory_inputs = general_script['memory_inputs']
    exit_inputs = general_script['exit_inputs']

    return general_script, script, memory_inputs, exit_inputs

def load_script(script_path):
    """Load script from a JSON file.
    
    Parameters
    ----------
    script_path : str
        Path to JSON file.

    Returns
    -------
    script : dict or dict[]
        Loaded JSON object.

    """
    with open(script_path) as f:
        script = json.load(f)
    return script

def process_decomp_rules(script, tags):
    """Processes decomposition rules in a script from Weizenbaum notation to regex.

    Parameters
    ----------
    script : dict[]
        JSON object containing decomposition rules in Weizenbaum notation.
    tags : dict[]
        Array of tags, where each tag is an array of words within the same semantic field.

    Returns
    -------
    script : dict[]
        JSON object containing decomposition rules in regex. 

    """
    # Cycle through each dict in the JSON script
    for d in script:
        # Cycle through all the rules in each dict
        for rule in d['rules']:
            # Convert decomposition rule from Weizenbaum notation to regex
            rule['decomp'] = decomp_to_regex(rule['decomp'], tags) 
    return script

def substitute(in_str, substitutions):
    """
    Parameters
    ----------
    in_str : str
        String to apply substitutions to.

    substitutions : dict
        Key-value pairs where the key must be substituted by its value.

    Returns
    -------
    out_str : str
        String with relevant substitutions applied.

    """
    out_str = ''
    for word in in_str.split():
        word = word.lower()
        if word in substitutions:
            out_str += substitutions[word] + ' '
        else:
            out_str += word + ' '

    return out_str

def rank(sentences, script, substitutions):
    """Rank keywords according to script.
    Only considers sentence with highest ranked word.
    Returns the actual sentence with highest ranked word,
    and the descending sorted list of keywords for that sentence.

    Parameters
    ----------

    Returns
    -------
    """

    all_keywords = []
    all_ranks = []
    maximums = []

    # Iterating using index so that sentences in the list can be modified directly
    for i in range(0, len(sentences)):
        sentences[i] = re.sub(r'[#$%&()*+,-./:;<=>?@[\]^_{|}~]', '', sentences[i])
        sentences[i] = substitute(sentences[i], substitutions)

        # Check if sentence is not empty at this point
        if sentences[i]:
            keywords = sentences[i].lower().split()
            all_keywords.append(keywords)
            
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

    return sentences[max_index], sorted_keywords

def decompose(keyword, in_str, script):
    """Find matching decomposition rule for a given keyword.
    If a matching decomposition rule is found, 
    it returns a list of components broken down according to the decomposition rule,
    along with the reassembly rule to use.
    If a matching decomposition rule is not found,
    it returns an empty list and an empty string.

    Parameters
    ----------

    Returns
    -------
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
    Parameters
    ----------

    Returns
    -------
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

def prepare_response(response):
    """
    Parameters
    ----------

    Returns
    -------
    """
    response = clean_string(response)
    response += "\nYou: "
    return response

def clean_string(in_str):
    """
    Parameters
    ----------

    Returns
    -------
    """
    # Remove extra whitespaces
    in_str = ' '.join(in_str.split())
    # Remove whitespaces before punctuation
    in_str = re.sub(r'\s([?.!"](?:\s|$))', r'\1', in_str)

    return in_str

memory_stack = []

general_script, script, memory_inputs, exit_inputs = setup()

# Get first user input
in_str = input("Eliza: Welcome.\nYou: ")

# Main execution loop
while in_str not in exit_inputs:

    # str.upper().isupper() is a fast way of checking
    # if a string contains any characters of the alphabet.
    # Source: https://stackoverflow.com/a/59301031
    if not in_str.upper().isupper():
        in_str = input('Eliza: Please, use letters. I am human, after all.\nYou:')
        continue

    if in_str.lower() == 'reset':
        # Reset "last_used_reassembly_rule" for all rules
        for d in script:
            for rule in d['rules']:
                rule['last_used_reassembly_rule'] = 0
        in_str = input('Eliza: Reset complete.\nYou:')
        continue

    # Break down input into punctuation-delineated sentences
    sentences = re.split(r'[.,!?](?!$)', in_str)

    # Get sentence in input with highest ranked word and sort keywords by rank
    sentence, sorted_keywords = rank(sentences, script, general_script['substitutions'])

    # Find a matching decomposition rule
    for keyword in sorted_keywords:
        comps, reassembly_rule = decompose(keyword, sentence, script)
        # Break if matching decomposition rule has been found
        if comps:
            # For certain keywords, generate an additional response to push onto memory stack
            if keyword in memory_inputs:
                # '^' is the memory stack keyword
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
            # '$' is the generic answer keyword
            comps, reassembly_rule = decompose('$', '$', script)
            response = reassemble(comps, reassembly_rule)

    response = prepare_response(response)

    # Get next user input
    in_str = input(response)

print("Eliza: Goodbye.\n")