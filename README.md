# eliza.py

The `doctor` script has been filled according to the appendix in the original paper (p. 9), including ranks.

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
- The ID of the last reassembly rule used for each decomposition rule is stored in the script file.
    - This way, Weizenbaum's concept of making the program feel less repetitive during a given session
    is extended to feel less repetitive throughout multiple sessions.
    - (note that the memory stack discussed in the paper does not persist through sessions, like the original;
    otherwise the program would "remember" your input (or another user's input) from past sessions,
    even though each session should only focus on the current user's present thoughts.)
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
J. Weizenbaum, “ELIZA—a computer program for the study of natural language communication between man and machine,” Communications of the ACM, vol. 9, no. 1, pp. 36–45, Jan. 1966. [Link](https://dl.acm.org/doi/10.1145/365153.365168)