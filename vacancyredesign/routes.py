from flask import render_template, url_for, redirect, request

# package related imports
from vacancyredesign import app
from vacancyredesign.modules.readability import check_readability
from vacancyredesign.modules.genderwording import load_data, check_for_exact_masculine_words, check_for_exact_feminine_words, print_length_of_genderwording_lists, calculate_ratio, check_for_partial_feminine_words, check_for_partial_masculine_words

import re

# Stackoverflow question ID: 63816168: how to count number of sentence using NLTK for a single string.
from nltk.tokenize import sent_tokenize, word_tokenize
# Routing logic


@app.route("/", methods=['POST', 'GET'])
def hello_world():

    # Genderwording functionality
    genderwords = load_data()
    print_length_of_genderwording_lists(genderwords)

    job_text = None

    if request.method == 'POST':

        if job_text == None:
            job_text = request.form['job_text']
            print(job_text)
            print(type(job_text))

            sentenized = sent_tokenize(job_text)
            print("Sentenized content:")
            print(sentenized)

            # checks if strings contain * or -, if so treat them as bullet points.
            contains_bullets = None

            asterix_count = 0

            test_string = job_text.split("\n")

            for item in test_string:
                if item.startswith(("*", "-")):
                    asterix_count += 1

            #ptrn = len(re.findall(r"[^?!.][?!.]", job_text))
            # print(ptrn)
            # print(str(asterix_count))
            # print(test_string)

            # Split string into separate "sentences" by indicating the end of a sentence with . or ? or !
            # Count the amount of words in each list item
            # n_words =
            n_lines = test_string.count("\n")
            r_lines = test_string.count("\r")
            print(f"Counted r-lines: {r_lines}, counted n-lines: {n_lines}")

            if test_string.count("\r") == 0:
                n_lines = 0
            else:
                n_lines = test_string.count("\r") + 1
            print("N lines is: " + str(n_lines))

            masculine_matches = check_for_exact_masculine_words(
                job_text, genderwords)
            feminine_matches = check_for_exact_feminine_words(
                job_text, genderwords)

            partial_masc_matches = check_for_partial_masculine_words(
                job_text, genderwords)
            partial_fem_matches = check_for_partial_feminine_words(
                job_text, genderwords)

            ratio = 0

            # if masculine_matches != '':
            #     for match in masculine_matches:
            #         print(f"Masculine word matches found: {match}")
            # else:
            #     print("No male matches found")

            # if feminine_matches != '':
            #     for match in feminine_matches:
            #         print(f"Feminine word matches found {match}")
            # else:
            #     print("No female matches found")

            if len(masculine_matches) or len(feminine_matches) > 0:
                ratio = calculate_ratio(masculine_matches, feminine_matches)
                print(calculate_ratio(masculine_matches, feminine_matches))

            return render_template("base.html",
                                   name=job_text,
                                   n_lines=n_lines,
                                   n_bullets=asterix_count,
                                   f_matches=feminine_matches,
                                   m_matches=masculine_matches,
                                   pm_matches=partial_masc_matches,
                                   pf_matches=partial_fem_matches,
                                   ratio=ratio)

    #myvar = request.json('job_text')
    # print(myvar)

    #myInp = check_readability()
    #name = "something extraordinary"
    return render_template("base.html", name="", n_lines="")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
