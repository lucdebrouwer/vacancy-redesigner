
import string
from nltk import word_tokenize
def strip_text(inp):
    # Tokenize the text
    # Strip the text from punctuation.
    return "No love for you"


def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def check_readability():
    return "Hello from the readability side 3"


def count_sentences(inp):
    amt_of_sentences = len(inp)
    #print(f"Amount of sentences in text: {amt_of_sentences}")
    return amt_of_sentences


def count_words(inp):

    # Definition of a word: everything that is not a special character, symbol or punctuation. 
    rmved_punctuation_string = inp.translate((str.maketrans('', '', string.punctuation)))

    tokenized = word_tokenize(rmved_punctuation_string)
    #print(f"TOKENIZED: {tokenized}")
    #input_splitted = inp.split()
    word_count = len(tokenized)
    #print(f"Amount of words in text {word_count}")
    return word_count

def calculate_readability_score(inp):
    avg = inp
    leesniveau = None
    if avg:
        if avg > 1 and avg < 10:
            leesniveau = "A1/A2"
        elif avg >= 10 and avg < 15:
            leesniveau = "B1"
        elif avg >= 15 and avg < 20:
            leesniveau = "B2"
        elif avg >= 20 and avg < 28:
            leesniveau = "C1"
        else:
            leesniveau = "C2"
    else:
        return "No input"
    return leesniveau
