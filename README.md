# FAQ

## Differences from original implementation
- In the original implementation, the order of keywords is not necessarily sorted descending
- The ID of the last reassembly rule used for each decomposition rule is stored in the script file.
    - This way, Weizenbaum's concept of making the program feel less repetitive during a given session
    is extended to feel less repetitive throughout multiple sessions.

## Why JSON and not CSV?
Keywords do not have a fixed size of decomposition rules,
and each decomposition rule does not have a fixed size of reassembly rules.

I think JSON can store this information in a simpler way than CSV.