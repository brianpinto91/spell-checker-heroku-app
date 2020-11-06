import flask
import pickle
import nltk

app = flask.Flask(__name__, template_folder="./templates")

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    if flask.request.method == 'GET':
        output_style = "output-place-holder"
        in_placeholder = "enter your word here and click submit to check for spelling"
        out_placeholder = "output will be displayed here"
        return flask.render_template("home.html", output_style = output_style, 
                                     input_placeholder = in_placeholder, output = out_placeholder)
    else:
        output_style = "output-text"
        input_word = flask.request.form['input-text']
        closest_words = get_nearest_words(input_word, 3, 3)
        in_placeholder = "enter your word here and click submit to check for spelling\n\nlast entered word: " + input_word
        return flask.render_template("home.html", output_style = output_style, 
                                     input_placeholder = in_placeholder, output = closest_words)

@app.route("/about", methods=['GET'])
def about():
    return flask.render_template("about.html")

with open("./data/vendor/nltk/vocab.pkl", "rb") as filehandler:
    vocab = pickle.load(filehandler)
    
def get_nearest_words(input_word, n_grams=3, num_return_words=3):
    input_word = input_word.lower()
    word_vocab = [w.lower() for w in vocab if w[0].lower()==input_word[0]] # only get the words from vocab whuch start with same letter as input word
    input_word_ngrams = set(nltk.trigrams([w for w in input_word]))
    jaccard_distance_list = []
    for word in word_vocab:
        word_ngrams = set(nltk.trigrams([w for w in word]))
        jaccard_distance = nltk.jaccard_distance(input_word_ngrams, word_ngrams)
        jaccard_distance_list.append((word, jaccard_distance))
    closest_word_list = sorted(jaccard_distance_list, key=lambda x: x[1], reverse=False)
    spelling_correct = is_spelling_correct(input_word, closest_word_list)
    print(closest_word_list[:10])
    if spelling_correct:
        return input_word
    else:
        return_list = []
        for n in range(num_return_words):
            return_list.append(closest_word_list[n][0])
        return ", ".join(return_list)

def is_spelling_correct(word, closest_word_list):
    if closest_word_list[0][0] == word:
        return True
    else:
        return False

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
    