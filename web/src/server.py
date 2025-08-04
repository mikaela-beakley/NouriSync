from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=['GET'])

def index():
    result = 200
    return render_template('index.html')

@app.route("/questionnaire", methods=['GET'])

def test():
    result = 200
    return render_template('questionnaire.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)