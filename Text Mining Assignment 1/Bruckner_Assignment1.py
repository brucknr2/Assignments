"""Lorin Bruckner - SP16LIS590TXL Assignment 1

This script was written in Python 3 to complete Assignment 1 and should be located in the same root directory as the
"Part1" folder containing the NSF Research Award records that were provided for the assignment.

Please note that this script may take 25 minutes or more to run and requires installation of the Natural Language
Toolkit (www.nltk.org).

The output consists of 4 files to fulfill the requirements of the assignment:

    awards.csv          A spreadsheet containing the name, number of awards, and total award amount for each NSF
                        organization

    abstracts.txt       A text file in which each line contains the Abstract ID, sentence number and sentence in the
                        abstract portion of the award record. The lines are written in the format required by the
                        assignment. (This file will be shortened before being uploaded so that it doesn't
                        exceed Moodle's file limit.)

    distribution.csv    A spreadsheet containing the distribution of sentence quantities for the abstracts (for easy
                        copying and pasting into the assignment template)

    problem_files.txt   Lists files that could not be processed because they have encoding problems or are missing data

"""


from nltk.corpus.reader import PlaintextCorpusReader    # Natural Language Toolkit Plain Text Reader
import re                                               # Regular Expressions


awd_num = 1             # Number of awards for each organization
award_recs = {}         # Records containing the name, number of awards, and total award amount for each organization
problem_files = []      # A list of files that can't be parsed because they have encoding problems or are missing data
label_pos = 0           # The position of the "Abstract" label in the first sentence of the abstract
sent_dist = {}          # Records the distribution of sentence quantities for abstracts


def GetOrg():

    """This function obtains the NSF organization name from the award record.

    It doesen't accept arguments but is used on each sentence of the award record to perform regex searches.

    """

    # Leave function if org name has already been found
    global org_found
    if org_found == 1: return

    # Do a regex search to find the sentence with the org name
    if re.search("'NSF', 'Org'", str(sent)) is not None:

        # Extract org name from sentence
        global org
        org = re.findall("'NSF', 'Org', ':', '(.*)', 'Latest'", str(sent))

        # Indicate that we've found the org name
        org_found = 1


def GetAmt():

    """This function obtains the award amount from the award record.

    It doesen't accept arguments but is used on each sentence of the award record to perform regex searches.

    """

    # Leave function if award amount has already been found
    global amt_found
    if amt_found == 1: return

    # Do a regex search to find the first sentence with a dollar sign
    if re.search("[\$]", str(sent)) is not None:

        # Extract award amount from sentence
        global amt
        amt = re.findall("\$', '(.*)', '\(', 'Estimated'", str(sent))

        # Indicate that we've found the amount
        amt_found = 1


def GetAbstract():

    """This function obtains the abstract from the award record.

    It doesn't accept arguments but is used on each paragraph of the award record to perform regex searches.

    In some cases, the abstract content begins on a new paragraph after the "Abstract" label. In other cases, NLTK
    puts the "Abstract" label and part of the abstract content in the same paragraph (and often in the same sentence)
    while the rest of the abstract content is located on another paragraph. Because of this, both paragraphs and
    sentences have to be combed through to find the exact location of the abstract.

    """

    # Leave function if abstract has already been found
    global abstract_found
    if abstract_found == 1: return

    # Get total number of paragraphs in file
    total_paras = len(corpus.paras(fileid))

    # Do a regex search to find the paragraph where the abstract begins
    if re.search("'Abstract'", str(para)) is not None:

        # Loop through sentences in paragraph
        for sent in para:

            # Do a regex search to find the abstract label
            if re.search("'Abstract'", str(sent)) is not None:

                # Get sentence length
                sent_len = len(sent)

                # If the abstract label is at the end of the sentence, get abstract starting with next paragraph
                if (sent[sent_len - 1]) == ":":
                    global abstract
                    abstract = corpus.paras(fileid)[(para_num + 1):total_paras]

                    # If abstract isn't empty, remove it from enclosing list
                    if abstract != []: abstract = abstract[0]

                # If the abstract label is in the middle of a sentence, get abstract starting with current paragraph
                else:
                    abstract = corpus.paras(fileid)[para_num:total_paras]

                    # Remove abstract from enclosing list
                    abstract = abstract[0]

                    # Loop through each token in the first sentence to find the abstract label
                    tok_num = 0
                    for token in abstract[0]:

                        # Iterate a counter for each token
                        tok_num += 1

                        # Find the abstract label with a regex search and keep track of its position in the sentence
                        if re.search("Abstract", token) is not None:
                            global label_pos
                            label_pos = tok_num

                    # Remove the part of the sentence that doesn't belong in the abstract
                    abstract[0][0:label_pos] = []

                    # Remove blank lines or colons from the beginning of the abstract
                    if abstract[0] == []:
                        del(abstract[0])
                    else:
                        del(abstract[0][0])

        # Indicate that we've found the abstract
        abstract_found = 1


# Clear the abstracts text file
with open("abstracts.txt", "w") as out_file:
    out_file.write("")

# Create a corpus from the files using NLTK
corpus = PlaintextCorpusReader("./Part1/", ".*\.txt")

# Loop through each file in the corpus
for fileid in corpus._fileids:

    # Set flags to 0
    org_found = 0           # Flag for when the NSF organization name has been found in the file
    amt_found = 0           # Flag for when the award amount has been found in the file
    abstract_found = 0      # Flag for when the abstract has been found in the file

    # Try to loop through each sentence in the file and apply GetOrg and GetAmt functions.
    try:
        for sent in corpus.sents(fileid):
            GetOrg()
            GetAmt()

    # If a file cannot be decoded to utf-8, add it to the problem file list and skip it.
    except UnicodeDecodeError:
        problem_files.append(fileid)
        continue

    # If there is missing data, add the file to the problem file list and skip it.
    if org==[] or org==['null'] or amt==[] or amt==['null']:
        problem_files.append(fileid)
        continue

    # Extract single values from list objects
    org = org[0]
    amt = int(amt[0])

    # Handle orgs with weird names
    if org == "O', '/', 'D": org = "O/D"

    # If an org doesn't already exist in our records, add it along with the award number and award amount.
    if org not in award_recs:
        award_recs[org] = [awd_num,amt]

    # If an org does exist in our records, add the award number and award amount to the totals for that org.
    else:
        award_recs[org][0] += 1
        award_recs[org][1] += amt

    # Write the total awards and award amounts for each NSF organization to a csv file
    with open("awards.csv", "w") as out_file:
        out_file.write("Org,# of Awards,Total Award Amount\n")
        for rec in award_recs:
            out_file.write(rec + "," + str(award_recs[rec][0]) + "," + str(award_recs[rec][1]) + "\n")

    # Extract abstract ID from filename
    abstractID = fileid.replace(".txt", "")
    abstractID = re.split("[\/]", abstractID)
    abstractID = abstractID[2]

    # Reset counter for the number of sentences in the abstract
    sent_num = 0

    # Find abstract by looping through paragraphs, counting them, and applying the GetAbstract function
    para_num = -1
    for para in corpus.paras(fileid):
        para_num += 1
        GetAbstract()

    # If the abstract is blank, add 1 to the distribution for 0 sentences
    if abstract == []:
        if 0 not in sent_dist:
            sent_dist[0] = 1
        else:
            sent_dist[0] += 1

    # Loop through each sentence in the abstract
    for line in abstract:

        # Iterate the sentence counter
        sent_num += 1

        # Flatten the sentence
        sent=" ".join(line)

        # Clean up punctuation
        sent=sent.replace(" ,", ",")
        sent=sent.replace(" .", ".")
        sent=sent.replace(" - ", "-")
        sent=sent.replace(" / ", "/")
        sent=sent.replace("( ", "(")
        sent=sent.replace(" )", ")")
        sent=sent.replace(" ?", "?")
        sent=sent.replace(" ' ", "'")
        sent=sent.replace(" :", ":")
        sent=sent.replace(" ;", ";")

        # Write sentences to text file in the format required by the assignment
        with open("abstracts.txt", "a+") as out_file:
            out_file.write(abstractID + "|" + str(sent_num) + "|" + sent + "\n")

    # If the number of sentences in our abstract doesn't already exist in the distribution records, add it.
    if sent_num not in sent_dist:
        sent_dist[sent_num] = 1

    # If the number of sentences in our abstract already exists in the distribution records, add 1 to the distribution.
    else:
        sent_dist[sent_num] += 1

# Write the total awards and award amounts for each NSF organization to a csv file
with open("distribution.csv", "w") as out_file:
    out_file.write("# of sentences,# of abstracts\n")
    for sent in sent_dist:
        out_file.write(str(sent) + "," + str(sent_dist[sent]) + "\n")

# Write the problem files to a text file
with open("problem_files.txt", "w") as out_file:
    out_file.write("The following files were not included in the analysis because they can't be decoded or are missing "
                   "data:\n")
    out_file.write("\n")
    for file in problem_files:
        out_file.write(file + "\n")