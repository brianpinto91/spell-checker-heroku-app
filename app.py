import flask
import pickle
import nltk
from PyDictionary import PyDictionary

JACCARD_CUTOFF = 1.0
MAX_RETURN_WORDS = 3

app = flask.Flask(__name__, template_folder="./templates")

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    if flask.request.method == 'POST':
        output_style = "output-text"
        input_word = flask.request.form['input-text']
        in_placeholder = "enter your word here and click submit to check for spelling" 
        if len(input_word) == 0:
            closest_words = ["Did you forget to input any word? 🤔"]
        elif len(input_word) == 1:
            closest_words = ["Cannot check spelling for a single letter! 😐"]
        elif (len(input_word) > 1) and (len(input_word) <= 3):
            closest_words = get_nearest_words(input_word, n_grams=2)
            in_placeholder+="\n\nlast entered word: " + input_word
        elif len(input_word) > 45:
            closest_words = ["Word too long! You must be playing around 😋"]
        else:
            closest_words = get_nearest_words(input_word, n_grams=3)
            in_placeholder+="\n\nlast entered word: " + input_word
        return flask.render_template("home.html", output_style = output_style, 
                                     input_placeholder = in_placeholder, output = closest_words)
    else:
        output_style = "output-place-holder"
        in_placeholder = "enter your word here and click submit to check for spelling"
        out_placeholder = ["output will be displayed here"]
        return flask.render_template("home.html", output_style = output_style, 
                                     input_placeholder = in_placeholder, output = out_placeholder)

@app.route("/about", methods=['GET'])
def about():
    return flask.render_template("about.html")

with open("./data/vendor/nltk/vocab.pkl", "rb") as filehandler:
    vocab = pickle.load(filehandler)
    
def get_nearest_words(input_word, n_grams=3):
    input_word = input_word.lower().strip()
    word_vocab = [w.lower() for w in vocab if w[0].lower()==input_word[0]] # only get the words from vocab whuch start with same letter as input word
    input_word_ngrams = set(nltk.ngrams([w for w in input_word], n=n_grams))
    jaccard_distance_list = []
    for word in word_vocab:
        word_ngrams = set(nltk.ngrams([w for w in word], n=n_grams))
        jaccard_distance = nltk.jaccard_distance(input_word_ngrams, word_ngrams)
        jaccard_distance_list.append((word, jaccard_distance))
    closest_word_list = sorted(jaccard_distance_list, key=lambda x: x[1], reverse=False)
    closest_word_list = filter_closest_word_list(closest_word_list)
    spelling_correct = is_spelling_correct(input_word, closest_word_list)
    output_text = get_output_text(spelling_correct, input_word, closest_word_list)
    return output_text

def filter_closest_word_list(closest_word_list):
    return_list = []
    for n in range(MAX_RETURN_WORDS):
        if closest_word_list[n][1] < JACCARD_CUTOFF:
            return_list.append(closest_word_list[n][0])
    return return_list

def is_spelling_correct(word, closest_word_list):
    if closest_word_list[0] == word:
        return True
    else:
        return False

def get_output_text(spelling_correct, input_word, closest_word_list):
    if spelling_correct:
        dictionary = PyDictionary(input_word)
        meanings_dict = dictionary.getMeanings()[input_word]
        meaning_text = []
        if meanings_dict is not None:
            for key, value in meanings_dict.items():
                meaning_text.append("{}: {}".format(key, value[0])) #include only first entry for each category of noun, verb etc
            return ["Match found 😁. Did you mean?"] + [[input_word, meaning_text]]
        else:
            return ["Match found 😁. Did you mean?"] + [[input_word, 
                    ["This word is in English vocab, but its meaning could not be found in built-in dictionary"]]]    
    else:
        if len(closest_word_list) == 0:
            return ["Strange word! You must be playing around 😋"]
        else:
            word_plus_meaning_list = []
            for word in closest_word_list:
                dictionary = PyDictionary(word)
                meanings_dict = dictionary.getMeanings()[word]
                meaning_text = []
                if meanings_dict is not None:
                    for key, value in meanings_dict.items():
                        meaning_text.append("{}: {}".format(key, value[0])) #include only first entry for each category of noun, verb etc
                    word_plus_meaning_list.append([word, meaning_text])
            return ["Wrong spelling 😞 Some suggestions for you:"] + word_plus_meaning_list

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
    