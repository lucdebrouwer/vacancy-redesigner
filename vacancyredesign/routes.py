from flask import render_template, url_for, redirect, request

# package related imports
from vacancyredesign import app
from vacancyredesign.modules.readability import check_readability, count_sentences, count_words, remove_html_tags, calculate_readability_score, get_statistics_debugging
from vacancyredesign.modules.genderwording import load_data, check_for_exact_masculine_words, check_for_exact_feminine_words, print_length_of_genderwording_lists, calculate_ratio, check_for_partial_feminine_words, check_for_partial_masculine_words, get_bias_score

import pandas as pd
from bs4 import BeautifulSoup
import matplotlib as pl
import seaborn as sns
import unicodedata
import pysbd
from pysbd.utils import PySBDFactory
import statistics


# Rich Text Editor Feature toggle
RTE_ENABLED = True
app.config['CKEDITOR_HEIGHT'] = 700 # Set RTE textarea height

@app.route("/", methods=['POST', 'GET'])
def index():

    # Genderwording functionality
    genderwords = load_data()                                           # Retrieve gender coded words
    length_of_lists = print_length_of_genderwording_lists(genderwords)  # Print length of gender coded words list
    job_text = None

    if request.method == 'POST':
        if job_text == None:
            # Toggle between Rich Text Editor or regular text editor
            if RTE_ENABLED:
                job_text = request.form.get('ckeditor')
            else:
                job_text = request.form['job_text']

            #=-=-=-=-=-=-=-= READABILITY FUNCTIONALITY =-=-=-=-=-=-=-=
            # 1. Text preprocessing
            # 2. Sentence Segmentation
            # 3. List declarations
            # 4. Calculating summary job description summary statistics
            # 5. Debug readability functionality output        

            # 1. Text preprocessing
            soup = BeautifulSoup(job_text, "lxml")  # Parse HTML from text
            soup_txt = soup.get_text()              # Retrieve text from HTML
           
            # Parse text into unicode and remove quotes
            job_desc_text_cleaned = unicodedata.normalize("NFKD", soup_txt)
            job_desc_text_cleaned = job_desc_text_cleaned.replace('’', '')
            job_desc_text_cleaned = job_desc_text_cleaned.replace('‘', '')

            # 2. Performing sentence segmentation
            seg = pysbd.Segmenter(language="nl", clean=False)
            job_desc_sentences = seg.segment(job_desc_text_cleaned) # Apply Sentence Boundary Detection based on "Golden Rules"

            # 3. Variable declaration for statistics
            accurate_list = []
            length_list = [] 
            filtered_sent_length = [] # Is used to store sentences that are smaller than 3 words and shouldn't be considered a sentence

            # 4. Calculating summary job description summary statistics

            for sentence in job_desc_sentences:
                # For each sentence, split the sentence into words 
                # Get the length of each sentence by calculating the length of the word list
                # Append each length to a list so we can use it for summary statistics
                words = sentence.split()
                length_of_sentence = len(words)
                length_list.append(length_of_sentence)

                # It is debatable whether a sentence should be taken into consideration for a fixed length
                # i.e. if a sentence contains 3 words, can it be considered a sentence? 
                # For now, the minimum sentence length needed to "define" a sentence, is valued at 3.
                if length_of_sentence > 3:
                    accurate_list.append(sentence)                  # Append the filtered sentences to a list so we can use these in summary statistics
                else:
                    filtered_sent_length.append(sentence)           # Save the other sentences as well

            # 4.1 Get summary statistics from the segmented sentences
            if accurate_list:
                n_sentences = len(accurate_list)                    # Retrieve the no of sentences
            else:
                n_sentences = 0                    
            
            if length_list:
                min_sent_length = min(length_list)                  # get the smallest sentence length
                max_sent_length = max(length_list)                  # get the largest sentence length
                avg = round(sum(length_list) / len(length_list))    # Calculate average sentence length
                sentence_list_as_tuple = tuple(length_list)         # Convert list to tuple to support immutable object
                median = statistics.median(sentence_list_as_tuple)  # get median
            else:
                min_sent_length = 0
                max_sent_length = 0
                avg = 0
                median = 0
 
            # 4.2 Get count statistics from the job description
            n_lines = job_text.count('<p>')                         # Retrieve all paragraphs
            n_lists = job_text.count('<ul>')                        # Retrieve all bullets being used in the job description
            asterix_count = job_text.count("<li>")                  # Counts the number of list items
            
            leesniveau = calculate_readability_score(avg)           # Get readability score
            n_words = count_words(job_desc_text_cleaned)            # get number of words


            if asterix_count and n_lists:
                gem_aantal_bullets_per_lijst = round(asterix_count / n_lists)
            else:
                gem_aantal_bullets_per_lijst = 0

            # (Statistics) debugging
            get_statistics_debugging(job_desc_sentences, min_sent_length, max_sent_length, accurate_list, avg, median, length_list, filtered_sent_length)

            # =-=-=-=-=-=-=-= GENDER BIAS FUNCTIONALITY =-=-=-=-=-=-=-=

            length_of_lists = print_length_of_genderwording_lists(genderwords)
    
            # 1. Exact gender wording matching
            masculine_matches = check_for_exact_masculine_words(job_text, genderwords)
            feminine_matches = check_for_exact_feminine_words(job_text, genderwords)
            
            # 2. Partial gender wording matching
            partial_masc_matches = check_for_partial_masculine_words(job_text, genderwords)
            partial_fem_matches = check_for_partial_feminine_words(job_text, genderwords)

            # 3. Calculate ratio gender coded words
            
            ratio = calculate_ratio(masculine_matches, feminine_matches)
            bias_score = get_bias_score(ratio)

            return render_template("main.html",
                                   rte=RTE_ENABLED,
                                   job_desc_full=job_text,
                                   segment=accurate_list,
                                   longest_sent=max_sent_length,
                                   smallest_sent=min_sent_length,
                                   n_words=n_words,
                                   leesniveau=leesniveau,
                                   n_sentences=n_sentences,
                                   median=median,
                                   n_words_x_sentence=avg,
                                   bias=bias_score,
                                   n_bullets_x_lists=gem_aantal_bullets_per_lijst,
                                   n_lists=n_lists,
                                   n_lines=n_lines,
                                   n_bullets=asterix_count,
                                   f_matches=feminine_matches,
                                   m_matches=masculine_matches,
                                   pm_matches=partial_masc_matches,
                                   pf_matches=partial_fem_matches,
                                   available_words=length_of_lists,
                                   ratio=ratio)
    else: 
        return render_template("main.html",
                           bias="",
                           rte=RTE_ENABLED, 
                           n_words="",
                           n_sentences="",
                           n_lines="",
                           n_bullets="",
                           f_matches="",
                           m_matches="",
                           pm_matches="",
                           pf_matches="",
                           available_words=length_of_lists,
                           ratio="")

@app.route('/report', methods=['GET'])
def report():

    # print(job_text)

    # Create a test dataframe
    d = {'labels': ['Simple', 'Fairly Easy', 'Average', 'Fairly Difficult',
                    'Difficult', 'Very difficult', 'Current'], 'values': [13, 14, 17, 21, 25, 29, 0]}
    df = pd.DataFrame(data=d)

    # df.plot()

    print(df.plot())

    return render_template("report.html", df=df)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
