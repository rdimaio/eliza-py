import json

from utils.rules import process_decomp_rules

def setup(general_script_path, script_path):
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
    general_script = load_script(general_script_path)
    script = load_script(script_path)
    
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