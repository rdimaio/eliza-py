import re

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
        # If substitutions specifies a substitution for this word, substitute it
        if word.lower() in substitutions:
            out_str += substitutions[word.lower()] + ' '
        # Otherwise carry over the same word
        else:
            out_str += word + ' '

    return out_str