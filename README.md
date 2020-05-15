# eliza.py
**ELIZA** is a natural language processing program developed from 1964 to 1966 by Joseph Weizenbaum, originally implemented in MAD-SLIP. You can read the 1966 paper [here](https://dl.acm.org/doi/10.1145/365153.365168). 

ELIZA uses pattern matching, decomposition and reassembly rules to emulate a Rogerian psychotherapist.



# Script structure

## `scripts/general.json`
This script handles general English language information that is not necessarily tied into the other script the program uses,
as well as useful inputs for the program.

- `substitutions`: specifies which keywords should be substituted before applying a custom script
- `tags`: specifies keywords that have
- `memory_inputs`: array of keywords that prompt the generation of an additional response added to the memory stack
- `exit_inputs`: array of keywords that can be used to quit the program

## `scripts/doctor.json`
This script simulates a **Rogerian psychotherapist**.
It has been filled according to the appendix in the original paper (p. 9), including ranks.
An additional great reference is the script file from [Charles Hayen's Java implementation of ELIZA](http://chayden.net/eliza/Eliza.html).
Some small additions have been made to make the program feel a bit nicer (e.g. the program responds to greetings).

Each element in the JSON file follows this structure:
- `keyword`: keyword that the program looks for in the user's input (**after substitution**, like in the original implementation)
    - Two special keywords exist:
        - `$`: specifies that a generic answer should be given
        - `^`: specifies that an answer from the memory stack should be given
- `rank`: rank of that keyword
- `rules`: Array of decomposition rules and matching reassembly rules in the form:
    - `decomp`: Decomposition rule (using the same syntax as the original 1966 paper)
    - `reassembly`: Array of reassembly rules to be used with the decomposition rule specified in `decomp`
    - `last_used_reassembly_rule`: ID of last used reassembly rule for this decomposition rule (0-indexed);
    it is incremented everytime the decomposition rule is matched and it cycles back to the beginning
    when the last reassembly rule in the array is used.


# FAQ

## Differences from original implementation

- In the original implementation, the order of keywords is not necessarily sorted descending
- In the original implementation, if a comma/period is encountered and a keyword has already been found,
all subsequent text is deleted (p. 2). In this implementation, sentences are split based on punctuation (—,.:;-),
and the sentence with the highest ranked keyword is chosen to be decomposed.
    - Main reasons:
        - The emphasis of the user's input may not necessarily be in the first section of the sentence
        - The section with the highest ranked keyword has a higher chance of having decomposition rules
        for that keyword, as it has a rank in the first place
- `DLIST` in the original implementation is called `tag` in this implementation. It works the same way.
- In the original implementation, the keyword `my` is associated with the memory stack (p. 6);
in this implementation, the memory stack is called when no matching decomposition rule is found.

## Why JSON and not CSV?
Each keyword has a **variable** amount of decomposition rules,
and each decomposition rule has a **variable** amount of reassembly rules.
I think JSON can store this information structure in a much more intuitive way.

# Future work
- Allow the user to edit the script during a session by typing "edit"
    - (see p. 7 of the paper)
- Could include a randomized delay for each response, so that it feels more human-like
- Could translate to Italian

# References
- J. Weizenbaum, “ELIZA-a computer program for the study of natural language communication between man and machine,” Communications of the ACM, vol. 9, no. 1, pp. 36–45, Jan. 1966. [Link](https://dl.acm.org/doi/10.1145/365153.365168)

- The script file from [Charles Hayen's Java implementation of ELIZA](http://chayden.net/eliza/Eliza.html)