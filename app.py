import flask
import pickle
import nltk

JACCARD_CUTOFF = 0.6
MAX_RETURN_WORDS = 4

app = flask.Flask(__name__, template_folder="./templates")

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    if flask.request.method == 'GET':
        output_style = "output-place-holder"
        in_placeholder = "enter your word here and click submit to check for spelling"
        out_placeholder = ["output will be displayed here"]
        return flask.render_template("home.html", output_style = output_style, 
                                     input_placeholder = in_placeholder, output = out_placeholder)
    else:
        output_style = "output-text"
        input_word = flask.request.form['input-text']
        in_placeholder = "enter your word here and click submit to check for spelling" 
        if len(input_word) == 0:
            closest_words = ["Did you forget to input any word? 🤔"]
        elif len(input_word) == 1:
            closest_words = ["Cannot check spelling for a single letter! 😐"]
        elif len(input_word) == 2:
            closest_words = get_nearest_words(input_word, n_grams=2)
            in_placeholder+="\n\nlast entered word: " + input_word
        elif len(input_word) > 45:
            closest_words = ["Word too long! You must be playing around 😋"]
        else:
            closest_words = get_nearest_words(input_word, n_grams=3)
            in_placeholder+="\n\nlast entered word: " + input_word
        return flask.render_template("home.html", output_style = output_style, 
                                     input_placeholder = in_placeholder, output = closest_words)

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
    spelling_correct = is_spelling_correct(input_word, closest_word_list)
    if spelling_correct:
        return ["Match found 😁. Did you mean?"] + [input_word]
    else:
        return_list = []
        for n in range(MAX_RETURN_WORDS):
            if closest_word_list[n][1] < JACCARD_CUTOFF:
                return_list.append(closest_word_list[n][0])
        if len(return_list) == 0:
            return ["Strange word! You must be playing around 😋"]
        else:
            return ["Wrong spelling 😞 Do you mean?"] + return_list

def is_spelling_correct(word, closest_word_list):
    if closest_word_list[0][0] == word:
        return True
    else:
        return False

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
    