import flask
import nltk
from PyDictionary import PyDictionary

MAX_WORD_LEN = 45
MAX_RETURN_WORDS = 3

app = flask.Flask(__name__, template_folder="./templates")

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    if flask.request.method == 'POST':
        input_word = flask.request.form['input-text'].strip()
        input_plchold_result_page = "enter your word here and click submit to check for spelling" + "\n\nlast entered word: " + input_word
        result_to_render = None

        if len(input_word) == 0:
            result_to_render = ["Did you forget to input any word? 🤔"]
        elif len(input_word) == 1:
            result_to_render = ["Cannot check spelling for a single letter! 😐"]
        elif len(input_word) > MAX_WORD_LEN:
            result_to_render = ["Word too long! You must be playing around 😋"]
        elif (len(input_word) > 1) and (len(input_word) <= 3):
            near_words = get_near_words(input_word = input_word, n_grams=2, num_return_words=MAX_RETURN_WORDS)
            result_to_render = get_output_content(near_words)
        else:
            near_words = get_near_words(input_word = input_word, n_grams=3, num_return_words=MAX_RETURN_WORDS)
            result_to_render = get_output_content(near_words)
        return flask.render_template("home.html", output_style = "output-with-content", 
                                     input_placeholder = input_plchold_result_page, result = result_to_render)
    else:
        input_plchold = "enter your word here and click submit to check for spelling"
        output_plchold = ["output will be displayed here"]
        return flask.render_template("home.html", output_style = "output-without-content", 
                                     input_placeholder = input_plchold, result = output_plchold)

@app.route("/about", methods=['GET'])
def about():
    return flask.render_template("about.html")

with open("./data/vendor/nltk/vocab_en", "r") as filehandler:
    vocab = [line for line in filehandler]
    
def get_near_words(input_word, n_grams, num_return_words = 3):
    """Function returns a list of tuples of closest words for the input word by using the
        jaccard distance metric for given n_grams.

        Arguments:
            input_word (str): word for which similar words are to be found

            n_grams (int): grouping size for letters within a word. This grouping will be used 
                            to calculate the jaccard distance for dissimilarity

            num_return_words (int): number of words to return

        Returns:
            (list): a sorted list of near words according to jaccard distance. The word at
                     the beginning of the list are more similar than the latter ones. If an exact match
                     for the input word is found then same word is returned else number of words as specified
                     in the parameter is returned
    """
    input_word = input_word.lower()
    vocab_words_list = [w.lower() for w in vocab if w[0].lower()==input_word[0]] # only get the words from vocab which start with same letter as input word
    input_word_ngrams = set(nltk.ngrams([ltr for ltr in input_word], n=n_grams))
    near_words_list = []
    for vocab_word in vocab_words_list:
        vocab_word_ngrams = set(nltk.ngrams([ltr for ltr in vocab_word], n=n_grams))
        jaccard_distance = nltk.jaccard_distance(input_word_ngrams, vocab_word_ngrams)
        near_words_list.append((vocab_word, jaccard_distance))
    near_words_list = sorted(near_words_list, key=lambda x: x[1], reverse=False)
    near_words_list = [item[0] for item in near_words_list] #drop the jaccard distance
    if near_words_list[0] == input_word:
        return near_words_list[:1] #return only the matching word
    else:
        return near_words_list[:num_return_words]

def get_output_content(near_words_list):
    """Function that returns the output to be rendered in the result webpage, after finding
        the similar words, which is passed as a list

    Arguments:
        near_words_list (list): a list of strings

    Returns:
        (list): This list will have the format: 
                 ['message', ['near_word_1',[meaning_n1_1, meaning_n1_2]], ['near_word_2',[meaning_n2_1, meaning_n2_2]]]
                 This format is useful for rendering the content as seperate lines in html using jinja
    """
    if len(near_words_list)==1:
        word_meaning_content = get_word_meaning_content(near_words_list)
        return ["Match found 😁. Did you mean?"] + word_meaning_content
    else:
        word_meaning_content = get_word_meaning_content(near_words_list)
        return ["Wrong spelling 😞 Some suggestions for you:"] + word_meaning_content

def get_word_meaning_content(near_words_list):
    """Function which attachs meaning to each word in the passed list of words
        if it is found in PyDictionary

        Arguments:
            near_words_list (list): a list of strings

        Returns:
        (list): This list will have the format: 
                 [['near_word_1',[meaning_n1_1, meaning_n1_2]], ['near_word_2',[meaning_n2_1, meaning_n2_2]]]
                 This format is useful for rendering the content as seperate lines in html using jinja      
    """
    word_meaning_list = []
    dictionary = PyDictionary(near_words_list)
    for word, entry in dictionary.getMeanings().items():
        word_entry_list = []
        if entry is not None:
            meaning_list = []
            for part_of_speech, meaning in entry.items():
                meaning_list.append("{}: {}".format(part_of_speech, meaning[0]))
            word_entry_list.append([word, meaning_list])
        else:
            no_meaning_found = ["Can't find a meaning in built-in dictionary!"]
            word_entry_list.append([word, no_meaning_found])
        word_meaning_list += word_entry_list
    return word_meaning_list

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
    