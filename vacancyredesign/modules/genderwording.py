import json
import os
import math
import re

from flask import Flask, current_app as app

# Functionality planning:
# Create a masculine list and feminine list
# Store user text input
# - Possibility that user text input needs to be tokenized -
# Check if user text input is in masculine list/feminine list
# if in both or either lists, count the occurences of each listing
# also store the index of the word so the matched words can be printed later on
# Construct a list containing:
# Matches found in masculine list: <total num>
# Masculine Words that occured in job description: <word 1, word2, word3>
# Matches found in feminine list: <total num>
# Feminine Words that occured in job description: <word 1, word2, word3>
# Return output to user


def load_data():

    # Solution: https://stackoverflow.com/questions/21133976/flask-load-local-json
    # Initial try to import files result in PATH errors, solution is to use Flask's built-in static-folder attribute
    filename = os.path.join(app.static_folder, 'data', 'genderwords.json')
    #print("FN: " + filename)
    with open(filename) as genderwords:
        data = json.load(genderwords)
        return data


def check_for_exact_masculine_words(inp, words_to_check):

    # Load data and convert it to lowercase
    input_lowercased = inp.lower()

    # Initialize empty lists
    masculine = []

    # Retrieve the masculine gender words from the JSON data file and append them to a normal list
    for male_words in words_to_check['masculine']:
        masculine.append(male_words.lower())

    exact_masculine_matches = []
    for word in masculine:
        res = re.search(r'\b{}\b'.format(re.escape(word)), input_lowercased)
        if res:
            exact_masculine_matches.append(res.group(0))
            #print(f"masculine matches: {res.group(0)}")
        else:
            pass
    return exact_masculine_matches


def check_for_exact_feminine_words(inp, words_to_check):
    # Load data, input and convert to lowercase
    input_lowercased = inp.lower()
    feminine = []

    for female_words in words_to_check['feminine']:
        feminine.append(female_words.lower())

    exact_feminine_matches = []

    for word in feminine:
        res = re.search(r'\b{}\b'.format(re.escape(word)), input_lowercased)
        if res:
            exact_feminine_matches.append(res.group(0))
            #print(f"feminine matches: {res.group(0)}")
        else:
            pass

    return exact_feminine_matches

# Based on SO question: https://stackoverflow.com/questions/3389574/check-if-multiple-strings-exist-in-another-string/3389611


def check_for_partial_masculine_words(inp, words_to_check):
    # Initialize empty lists
    masculine = []

    # Retrieve the masculine gender words from the JSON data file and append them to a normal list
    for male_words in words_to_check['masculine']:
        masculine.append(male_words.lower())

    # Finds partial matches, check if the string is within the list.
    # Find all non-duplicate matches from the user input with the masculine gender wording list in the order of appereance
    masculine_matches = []
    input_lowercased = inp.lower()
    for x in masculine:
        if x in input_lowercased and x not in masculine_matches:
            masculine_matches.append(x)
            #print(f"masculine matches: {x}")

    return masculine_matches


def check_for_partial_feminine_words(inp, words_to_check):
    input_lowercased = inp.lower()
    feminine = []
    # Retrieve the feminibe gender words from the JSON data file and append them to a normal list
    for female_words in words_to_check['feminine']:
        feminine.append(female_words.lower())

    # Finds partial matches, check if the string is within the list.
    # Find all non-duplicate matches from the user input with the feminine gender wording list in the order of appereance
    feminine_matches = []
    for x in feminine:
        if x in input_lowercased and x not in feminine_matches:
            feminine_matches.append(x)
            #print(f"feminine matches: {x}")
    return feminine_matches


def print_length_of_genderwording_lists(data):

    length_of_lists = {
        "masculine": len(data['masculine']),
        "feminine": len(data['feminine'])
    }

    # print("Amount of available masculine words: " +
    #       str(len(data['masculine'])))
    # print("Amount of available feminine words: " + str(len(data['feminine'])))

    return length_of_lists


def calculate_ratio(male_matches, female_matches):

    # Calculate the length of each match list
    male_match_length = len(male_matches)
    female_match_length = len(female_matches)

    match_total = male_match_length + female_match_length
    # Print the outcome of each list to debug funtionality
    # uncomment for debugging purposes when in production
    #print(
    #    f"The length of the matched masculine list is: {male_match_length} \nThe length of the matched feminine list is {female_match_length}")

    ratio_dct = {
        "male_ratio": 0,
        "female_ratio": 0
    }
    # If there are matches present in the matching list, calculate the male/female ratio, store it in a dictionary and return it to the user interface
    if male_match_length or female_match_length > 0:
        male_ratio = round(male_match_length / match_total * 100)
        female_ratio = round(female_match_length / match_total * 100)

        # Edit the dictionary and feed it with RT-values
        ratio_dct["male_ratio"] = male_ratio
        ratio_dct["female_ratio"] = female_ratio

        # Debug the outcome for functionality purpose
        #print(f"Male ratio: {male_ratio}, female ratio: {female_ratio}")
    else:
        ratio_dct["male_ratio"] = 0
        ratio_dct["female_ratio"] = 0

    return ratio_dct
