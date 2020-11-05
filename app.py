import flask

app = flask.Flask(__name__, template_folder="./templates")

@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
def home():
    return flask.render_template("home.html")

@app.route("/about", methods=['GET'])
def about():
    return flask.render_template("about.html")

if __name__ == "__main__":
    pass
    