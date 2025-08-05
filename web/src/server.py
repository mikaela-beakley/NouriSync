from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/", methods=['GET']) # Index route

def index():
    result = 200
    return render_template('index.html')

@app.route("/questionnaire", methods=['GET']) # Questionnaire route

def test():
    result = 200
    return render_template('questionnaire.html')

@app.route("/questionnaire-patient-info", methods=['GET', 'POST'])

def post_patient_answers():
    print(request.form)
    form_answers = request.form
    print(form_answers['scale-question-1'])
    print(form_answers['scale-question-2'])
    print(form_answers['comments'])
    return redirect("/questionnaire")

@app.route("/questionnaire-caregiver-info", methods=['GET', 'POST'])

def post_caregiver_answers():
    form_answers = request.form
    print(form_answers['scale-question-1'])
    print(form_answers['scale-question-2'])
    print(form_answers['comments'])
    return redirect("/")



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)