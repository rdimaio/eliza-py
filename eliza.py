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
    """Substitute words in a string according to a dict.

    Parameters
    ----------
    in_str : str
        String to apply substitutions to.
    substitutions : dict
        Key-value pairs where key = word to substitute, value = new word.

    Returns
    -------
    out_str : str
        String with relevant substitutions applied.

    """
    out_str = ''
    # Cycle through all words in string
    for word in in_str.split():
        word = word.lower()
        # If substitutions specifies a substitution for this word, substitute it
        if word in substitutions:
            out_str += substitutions[word] + ' '
        # Otherwise carry over the same word
        else:
            out_str += word + ' '

    return out_str

def rank(sentences, script, substitutions):
    """Rank keywords according to a script.
    Only returns the sentence with the highest ranked keyword.

    Parameters
    ----------
    sentences : str[]
        Array of sentences.

    script : dict[]
        JSON object containing ranks of different keywords.

    substitutions : dict
        Key-value pairs where key = word to substitute, value = new word.

    Returns
    -------
    sentences[max_index] : str
        Sentence with highest ranked keyword in `sentences`.
    sorted_keywords : str[]
        Words in `sentences[max_index]` sorted in descending order based on their rank.

    """

    all_keywords = []
    all_ranks = []
    maximums = []

    # Iterating using index so that sentences in the list can be modified directly
    for i in range(0, len(sentences)):
        # Remove all punctuation
        sentences[i] = re.sub(r'[#$%&()*+,-./:;<=>?@[\]^_{|}~]', '', sentences[i])
        # Substitute keywords
        sentences[i] = substitute(sentences[i], substitutions)

        # Check if sentence is not empty at this point
        if sentences[i]:
            keywords = sentences[i].lower().split()
            all_keywords.append(keywords)
            
            # Get ranks for this sentence
            ranks = get_ranks(keywords, script)

            # Append maximum rank in this sentence
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

def get_ranks(keywords, script):
    """Return ranks of queried keyword in a given script.

    Parameters
    ----------
    keywords : str[]
        Array of keywords to search in the script.
    script : dict[]
        JSON object containing ranks of different keywords.
    
    Returns
    -------
    ranks : int[]
        Array of integers in the same order as their respective keywords
    
    """

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
    
    return ranks

def decompose(keyword, in_str, script):
    """Find matching decomposition rule for a given keyword and string, if possible.

    Parameters
    ----------
    keyword : str
        Keyword used to query the script for decomposition rules.
    in_str : str
        String used as input to the decomposition rules.
    script : dict[]
        JSON object containing decomposition rules for various keywords.

    Returns
    -------
    comps : str[]
        List of components decomposed according to the matching decomposition rule.
        Empty if no matching decomposition rule is found.
    reassembly_rule : str
        Reassembly rule that must be used to reassemble comps.
        Empty if no matching decomposition rule is found.

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
                    update_last_used_reassembly_rule(rule)
                    break
            break

    return comps, reassembly_rule

def update_last_used_reassembly_rule(rule):
    """Update the `last_used_reassembly_rule` ID for a given `rule`.
    Cycle back to 0 if all reassembly rules for the respective decomposition rule have been used.

    Parameters
    ----------
    rule : dict
        Rule containing a decomposition rule, 
        one or more reassembly rules and a `last_used_reassembly_rule` counter.

    Returns
    -------
    next_id : int
        Value to assign to `last_used_reassembly_rule` for the input `rule`.
    """

    # Update last used reassembly rule ID
    next_id = rule['last_used_reassembly_rule']+1
    # If all reassembly rules have been used, start over
    if next_id >= len(rule['reassembly']):
        next_id = 0
    rule['last_used_reassembly_rule'] = next_id

def reset_all_last_used_reassembly_rule(script):
    """Reset all `last_used_reassembly_rule` in a script to 0.

    Parameters
    ----------
    script : dict[]
        JSON object with keywords and associated rules.
    """

    for d in script:
        for rule in d['rules']:
            rule['last_used_reassembly_rule'] = 0

def reassemble(components, reassembly_rule):
    """Reassemble a list of strings given a reassembly rule.
    Note: reassembly rules are 1-indexed, according to the original paper.
    
    Parameters
    ----------
    components : str[]
        Components to be assembled according to `reassembly_rule`.
    reassembly_rule : str
        Rule stating how to reassemble `components`.

    Returns
    -------
    response : str
        Reassembled components.

    """

    response = 'Eliza: '

    # Split reassembly rule into its components
    reassembly_rule = reassembly_rule.split() 

    for comp in reassembly_rule:
        # If comp is a number, then place the component at that index
        if comp.isnumeric():
            # int(comp)-1 due to the fact that 
            # reassembly rules in Weizenbaum notation are 1-indexed
            response += components[int(comp)-1] + ' '
        # Otherwise, place the word itself
        else:
            response += comp + ' '

    # Remove trailing space
    response = response[:-1]

    return response

def prepare_response(response):
    """Processes the program's response before being shown to the user.
    
    Parameters
    ----------
    response : str
        String to process.

    Returns
    -------
    response : str
        Processed string.

    """
    response = clean_string(response)
    response += "\nYou: "
    return response

def clean_string(in_str):
    """Removes superfluous characters from a string.
    
    Parameters
    ----------
    in_str : str
        String to clean.

    Returns
    -------
    in_str : str
        Cleaned string.

    """
    # Remove extra whitespaces
    in_str = ' '.join(in_str.split())
    # Remove whitespaces before punctuation
    in_str = re.sub(r'\s([?.!"](?:\s|$))', r'\1', in_str)

    return in_str

def generate_response(in_str, script, substitutions, memory_stack, memory_inputs):
    """Generate response from user input, according to a script.

    Parameters
    ----------
    in_str : str
        User input.
    script : dict[]
        JSON object containing information on keywords and rules.
    substitutions : dict
        Key-value pairs where key = word to substitute, value = new word.
    memory_stack : str[]
        Stack of responses generated when `generate_memory_response` is prompted.
    memory_inputs : str[]
        Keywords that prompt `generate_memory_response`.

    Returns
    -------
    response : str
        Generated response.

    """
    # Break down input into punctuation-delineated sentences
    sentences = re.split(r'[.,!?](?!$)', in_str)

    # Get sentence in input with highest ranked word and sort keywords by rank
    sentence, sorted_keywords = rank(sentences, script, substitutions)

    # Find a matching decomposition rule
    for keyword in sorted_keywords:
        comps, reassembly_rule = decompose(keyword, sentence, script)
        # Break if matching decomposition rule has been found
        if comps:
            # For certain keywords, generate an additional response to push onto memory stack
            if keyword in memory_inputs:
                generate_memory_response(sentence, script, memory_stack)
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
            response = generate_generic_response(script)

    response = prepare_response(response)
    return response

def generate_generic_response(script):
    """Generate a generic response that is independent of the user input.

    Parameters
    ----------
    script : dict[]
        JSON object containing information on keywords and rules.

    Returns
    -------
    response : str
        Generic response.
    
    """
    # '$' is the generic answer keyword
    comps, reassembly_rule = decompose('$', '$', script)
    return reassemble(comps, reassembly_rule)

def generate_memory_response(sentence, script, memory_stack):
    """Generate a response for the memory stack.

    Parameters
    ----------
    sentence : str
        Current sentence to decompose and reassemble.
    script : dict[]
        JSON object containing information on keywords and rules.
    memory_stack : str[]
        Stack of responses generated when `generate_memory_response` is prompted.
    
    """
    # '^' is the memory stack keyword
    mem_comps, mem_reassembly_rule = decompose('^', sentence, script)
    mem_response = reassemble(mem_comps, mem_reassembly_rule)
    memory_stack.append(mem_response)

def main():
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
            reset_all_last_used_reassembly_rule(script)
            in_str = input('Eliza: Reset complete.\nYou:')
            continue

        response = generate_response(in_str, script, general_script['substitutions'], memory_stack, memory_inputs)

        # Get next user input
        in_str = input(response)

    print("Eliza: Goodbye.\n")

if __name__=="__main__":
   main()