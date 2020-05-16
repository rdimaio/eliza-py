import re

from utils.rank import rank
from utils.rules import decompose, reassemble

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
            response = reassemble(comps, reassembly_rule)
            # For certain keywords, generate an additional response to push onto memory stack
            if keyword in memory_inputs:
                generate_memory_response(sentence, script, memory_stack)
            break
    # If no matching decomposition rule has been found
    else:
        # If memory stack is not empty,
        # pop answer from memory stack
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