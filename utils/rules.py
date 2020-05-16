import re

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
                    reassembly_rule = get_reassembly_rule(rule)
                    break
            break

    return comps, reassembly_rule

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

def preprocess_decomp_rule(in_str):
    """Preprocess a decomposition rule before converting to regex.

    Parameters
    ----------
    in_str : str
        String representing a decomposition rule.

    Returns
    -------
    in_str: str[]
        List of components in decomposition rule.
    """
    # The input is of the form: e.g. (0 YOU 0)
    # Strip parenthesis
    in_str = re.sub('[()]', '', in_str)

    # Split string into space separated list
    return in_str.split()


def decomp_to_regex(in_str, tags):
    """Convert decomposition rules from Weizenbaum notation to regex.
    An example of Weizenbaum notation is: (0 KEYWORD1 0 KEYWORD2 0).

    Parameters
    ----------
    in_str : str
        Decomposition rule in Weizenbaum notation to convert to regex.
    tags : dict
        Tags to consider when converting to regex.

    Returns
    -------
    out_str : str
        Decomposition rule converted to regex form.
        
    """
    out_str = ''

    in_str = preprocess_decomp_rule(in_str)

    for w in in_str:
        w = regexify(w, tags)
        # Parentheses are needed to properly divide sentence into components
        # \s* matches zero or more whitespace characters 
        out_str += '(' + w + r')\s*' 

    return out_str

def regexify(w, tags):
    """Convert a single component of a decomposition rule
    from Weizenbaum notation to regex.

    Parameters
    ----------
    w : str
        Component of a decomposition rule.
    tags : dict
        Tags to consider when converting to regex.

    Returns
    -------
    w : str
        Component of a decomposition rule converted to regex form.
    
    """
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
        w = tag_to_regex(tag_name, tags)
    else:
        # Add word boundaries to match on a whole word basis
        w = r'\b' + w + r'\b'
    return w

def tag_to_regex(tag_name, tags):
    """Convert a decomposition rule tag into regex notation.
    
    Parameters
    ----------
    tag_name : str
        Tag to convert to regex notation.
    tags : dict
        Tags to consider when converting to regex.

    Returns
    -------
    w : str
        Tag converted to regex notation. Empty if `tag_name` is not in `tags`.
    """
    w = ''
    if tag_name in tags:
        # Make a regex separating each option with OR operator (e.g. x|y|z)
        w = r'\b(' + '|'.join(tags[tag_name]) + r')\b'
    return w

def update_last_used_reassembly_rule(rule):
    """Update the `last_used_reassembly_rule` ID for a given decomposition `rule`.
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

def get_reassembly_rule(rule):
    """Return reassembly rule for a given decomposition rule.

    Parameters
    ----------
    rule : dict
        Rule containing a decomposition rule, 
        one or more reassembly rules and a `last_used_reassembly_rule` counter.

    Returns
    -------
    reassembly_rule : str
        Reassembly rule used to assemble a response for the user.
    """   
    reassembly_rule = rule['reassembly'][rule['last_used_reassembly_rule']]
    update_last_used_reassembly_rule(rule)
    return reassembly_rule