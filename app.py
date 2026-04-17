from flask import Flask, render_template, request, redirect
from pptx import Presentation
import difflib
import os

app = Flask(__name__)

# GLOBAL STORAGE (IMPORTANT FIX)
ppt_text_global = ""


# ----------- EXTRACT PPT TEXT -----------
def extract_ppt_text(file):
    prs = Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "
    return text.lower()


# ----------- ACCURACY -----------
def calculate_accuracy(ppt_text, spoken_text):
    return round(difflib.SequenceMatcher(None, ppt_text, spoken_text).ratio() * 100, 2)


# ----------- FILLERS -----------
def count_fillers(text):
    fillers = ["um", "uh", "like", "you know", "basically", "and"]
    count = 0
    for word in fillers:
        count += text.lower().count(word)
    return count


# ----------- PAUSES -----------
def count_pauses(text):
    return text.count("...")


# ----------- AI FEEDBACK -----------
def generate_ai_feedback(acc, fillers, wpm, pauses):
    feedback = []

    if acc < 40:
        feedback.append("You need to follow PPT more closely.")
    else:
        feedback.append("Good clarity.")

    if fillers > 3:
        feedback.append("Reduce filler words.")
    else:
        feedback.append("Good fluency.")

    if wpm < 70:
        feedback.append("Speak faster.")
    elif wpm > 150:
        feedback.append("Slow down.")
    else:
        feedback.append("Good pace.")

    if pauses > 5:
        feedback.append("Too many pauses.")
    else:
        feedback.append("Good flow.")

    return feedback


# ----------- ROUTES -----------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/dashboard')
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', done=False)


# ----------- UPLOAD PPT -----------
@app.route('/upload', methods=['POST'])
def upload():
    global ppt_text_global

    file = request.files.get('ppt')

    if not file:
        return render_template('dashboard.html', error="No file uploaded")

    file_path = "uploaded.pptx"
    file.save(file_path)

    ppt_text_global = extract_ppt_text(file_path)

    return render_template('dashboard.html', message="PPT uploaded successfully!")


# ----------- ANALYZE (TRIGGERED BY STOP BUTTON) -----------
@app.route('/analyze', methods=['POST'])
def analyze():
    global ppt_text_global

    if not ppt_text_global:
        return render_template('dashboard.html', error="Upload PPT first")

    spoken_text = request.form.get('text', '').lower()

    if not spoken_text.strip():
        return render_template('dashboard.html', error="No speech detected")

    acc = calculate_accuracy(ppt_text_global, spoken_text)
    fillers = count_fillers(spoken_text)
    pauses = count_pauses(spoken_text)
    wpm = len(spoken_text.split())

    feedback = generate_ai_feedback(acc, fillers, wpm, pauses)

    return render_template(
        'dashboard.html',
        done=True,
        spoken=spoken_text,
        accuracy=acc,
        fillers=fillers,
        pauses=pauses,
        wpm=wpm,
        feedback=feedback
    )


if __name__ == '__main__':
    app.run(debug=True)
