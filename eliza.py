import os

from utils.startup import setup
from utils.rules import reset_all_last_used_reassembly_rule
from utils.response import generate_response

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_DIR = os.path.join(PROJECT_DIR, 'scripts')
GENERAL_SCRIPT_PATH = os.path.join(SCRIPT_DIR, 'general.json')
SCRIPT_PATH = os.path.join(SCRIPT_DIR, 'doctor.json')


def main():
    memory_stack = []
    general_script, script, memory_inputs, exit_inputs = setup(GENERAL_SCRIPT_PATH, SCRIPT_PATH)

    # Get first user input
    in_str = input("Eliza: Welcome.\nYou: ")
    in_str_l = in_str.lower()

    # Main execution loop
    while in_str_l not in exit_inputs:

        # str.lower().islower() is a fast way of checking
        # if a string contains any characters of the alphabet.
        # Source: https://stackoverflow.com/a/59301031
        if not in_str_l.islower():
            in_str = input('Eliza: Please, use letters. I am human, after all.\nYou:')
            continue

        if in_str_l == 'reset':
            reset_all_last_used_reassembly_rule(script)
            in_str = input('Eliza: Reset complete.\nYou:')
            continue

        response = generate_response(in_str, script, general_script['substitutions'], memory_stack, memory_inputs)

        # Get next user input
        in_str = input(response)
        in_str_l = in_str.lower()

    print("Eliza: Goodbye.\n")

if __name__=="__main__":
   main()