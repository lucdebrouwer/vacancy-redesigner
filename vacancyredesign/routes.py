#from nltk.tokenize import sent_tokenize, word_tokenize
from flask import render_template, url_for, redirect, request

# package related imports
from vacancyredesign import app
from vacancyredesign.modules.readability import check_readability, count_sentences, count_words, remove_html_tags, calculate_readability_score
from vacancyredesign.modules.genderwording import load_data, check_for_exact_masculine_words, check_for_exact_feminine_words, print_length_of_genderwording_lists, calculate_ratio, check_for_partial_feminine_words, check_for_partial_masculine_words

import re
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
app.config['CKEDITOR_HEIGHT'] = 600 # Set RTE textarea height

@app.route("/", methods=['POST', 'GET'])
def index():

    # Genderwording functionality
    genderwords = load_data()
    length_of_lists = print_length_of_genderwording_lists(genderwords)
    job_text = None
    #ratio = None
    if request.method == 'POST':

        if job_text == None:
            if RTE_ENABLED:
                job_text = request.form.get('ckeditor')
            else:
                job_text = request.form['job_text']

            # html_less_job_text = remove_html_tags(job_text) <-- old/original method
            # Parse HTML from text
            soup = BeautifulSoup(job_text, "lxml")
            # Retrieve the text
            soup_txt = soup.get_text()

            
            # Parse text into unicode and thus removing encoding like &amp; and \xa0
            job_desc_text_cleaned = unicodedata.normalize("NFKD", soup_txt)
            job_desc_text_cleaned = job_desc_text_cleaned.replace('’', '') # Remove quotes, otherwise it will be seen as a sentence
            job_desc_text_cleaned = job_desc_text_cleaned.replace('‘', '')

            # Declare segmenter done by PyBSD
            seg = pysbd.Segmenter(language="nl", clean=False)
            job_desc_sentences = seg.segment(job_desc_text_cleaned) # Apply Sentence Boundary Detection based on "Golden Rules"

            print(f"Type: {type(job_desc_sentences)}")
            print(f"No. Sentences: {len(job_desc_sentences)}")

            

            # Variable declaration for statistics
            accurate_list = []
            length_list = [] 
            filtered_sent_length = [] # Is used to store sentences that are smaller than 3 words and shouldn't be considered a sentence

            # Determine the length of each sentence in the sentence list
            # It is debatable whether a sentence should be taken into consideration for a fixed length
            # i.e. if a sentence contains 3 words, can it be considered a sentence? 
            # Also needs to consider the minimum sentence length before there can be an accurate no of sentence calculation
            # for sent in job_desc_sentences:
            for sentence in job_desc_sentences:
                words = sentence.split()
                length_of_sentence = len(words)
                length_list.append(length_of_sentence)

                if length_of_sentence > 3:
                    accurate_list.append(sentence)
                else:
                    filtered_sent_length.append(sentence)

            if filtered_sent_length:
                print(filtered_sent_length)
                 

            # Get statistics from the segmented sentences
            min_sent_length = min(length_list)
            max_sent_length = max(length_list)
            avg = round(sum(length_list) / len(length_list))
            
            n_sentences = len(accurate_list)    # Retrieve the no of sentences
            n_lines = job_text.count('<p>')     # Retrieve all paragraphs
            n_lists = job_text.count('<ul>')    # Retrieve all bullets being used in the job description
            
            # Statistics debugging
            print(f"The min. sent. length is: {min_sent_length}")
            print(f"The max. sent. length is: {max_sent_length}")
            print(f"The length of the ist is: {len(accurate_list)}")
            print(f"The average sent. length is: {avg}")

            sentence_list_as_tuple = tuple(length_list)

            median = statistics.median(sentence_list_as_tuple)
            print(f"Median is: {median}")
            print(f"Length list: {length_list}")

            #leesniveau = None

            
            leesniveau = calculate_readability_score(avg) # Get readability score
            n_words = count_words(job_desc_text_cleaned)  # get number of words

            # if n_words and n_sentences:
            #     gem_woorden_per_zin = round(n_words / n_sentences)
            # else:
            #     gem_woorden_per_zin = 0


            asterix_count = job_text.count("<li>")
            if asterix_count and n_lists:
                gem_aantal_bullets_per_lijst = round(asterix_count / n_lists)
            else:
                gem_aantal_bullets_per_lijst = 0

            # Where the gender bias magic happens
            masculine_matches = check_for_exact_masculine_words(
                job_text, genderwords)
            feminine_matches = check_for_exact_feminine_words(
                job_text, genderwords)

            # Where the partial gender bias magic happens
            partial_masc_matches = check_for_partial_masculine_words(
                job_text, genderwords)
            partial_fem_matches = check_for_partial_feminine_words(
                job_text, genderwords)

            length_of_lists = print_length_of_genderwording_lists(genderwords)
            # Where the calculation magic happens
            ratio = 0
            #bias_score = None
            if len(masculine_matches) or len(feminine_matches) > 0:
                ratio = calculate_ratio(masculine_matches, feminine_matches)
            else:
                ratio = calculate_ratio(masculine_matches, feminine_matches)


            if ratio['female_ratio'] == 50 and ratio['male_ratio'] == 50:
                bias_score = "Neutraal"
            elif ratio['female_ratio'] > 50 and ratio['female_ratio'] <= 60:
                bias_score = "Enigzins vrouwelijk gestuurd"
            elif ratio['female_ratio'] > 60 and ratio ['female_ratio'] <= 80:
                bias_score = "Redelijk vrouwelijk gestuurd"
            elif ratio['female_ratio'] > 80:
                bias_score = "Sterk Vrouwelijk gestuurd"
            elif ratio['male_ratio'] > 50 and ratio['male_ratio'] <= 60:
                bias_score = "Enigzins mannelijk gestuurd"
            elif ratio['male_ratio'] > 60 and ratio ['male_ratio'] <= 80:
                bias_score = "Redelijk mannelijk gestuurd"
            elif ratio['male_ratio'] > 80:
                bias_score = "Sterk Mannelijk gestuurd"
            else:
                bias_score = "Geen score"  

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

    return render_template("main.html", name="",
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



@app.route('/main', methods=['GET'])
def main():
    return render_template("main.html",
                                   rte=RTE_ENABLED,
                                   job_desc_full="",
                                   segment="",
                                   longest_sent="",
                                   smallest_sent="",
                                   n_words="",
                                   leesniveau="",
                                   n_sentences="",
                                   median="",
                                   n_words_x_sentence="",
                                   bias="",
                                   n_bullets_x_lists="",
                                   n_lists="",
                                   n_lines="",
                                   n_bullets="",
                                   f_matches="",
                                   m_matches="",
                                   pm_matches="",
                                   pf_matches="",
                                   available_words="",
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
