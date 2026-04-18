from flask import Flask, render_template, request, redirect, url_for
from pptx import Presentation
import difflib
import re
import os

app = Flask(__name__)

ppt_text = ""


# ---------- EXTRACT PPT ----------
def extract_ppt_text(file):
    prs = Presentation(file)
    text = ""

    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "

    return text.lower()


# ---------- LOGIN ----------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('index.html')


# ---------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('signup.html')


# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# ---------- UPLOAD ----------
@app.route('/upload', methods=['POST'])
def upload():
    global ppt_text

    file = request.files.get('ppt')

    if file:
        ppt_text = extract_ppt_text(file)

    return redirect(url_for('dashboard'))


# ---------- ANALYZE ----------
# ---------- ANALYZE ----------
@app.route('/analyze', methods=['POST'])
def analyze():
    global ppt_text

    spoken = request.form.get('text', '').lower()

    if spoken.strip() == "":
        return render_template('dashboard.html', error="No speech detected")

    # -------- CLEAN WORDS --------
    spoken_words = re.findall(r'\b\w+\b', spoken.lower())
    ppt_words = set(re.findall(r'\b\w+\b', ppt_text.lower()))

    # -------- ACCURACY --------
    if spoken_words and ppt_words:
        match_count = sum(1 for word in spoken_words if word in ppt_words)
        accuracy = (match_count / len(spoken_words)) * 100
    else:
        accuracy = 0

    # -------- FILLERS --------
    filler_list = ["um", "uh", "like", "basically", "actually"]
    fillers = sum(1 for word in spoken_words if word in filler_list)

    # -------- PAUSES --------
    pauses = len(spoken_words) // 7

    # -------- SPEED --------
    wpm = len(spoken_words)

    # -------- FEEDBACK --------
    feedback = []

    if accuracy < 40:
        feedback.append("Follow PPT more closely")
    else:
        feedback.append("Good alignment")

    if fillers > 3:
        feedback.append("Reduce filler words")

    if wpm < 70:
        feedback.append("Speak faster")
    elif wpm > 150:
        feedback.append("Slow down")

    if pauses > 3:
        feedback.append("Too many pauses")

    return render_template(
        'dashboard.html',
        spoken=spoken,
        accuracy=round(accuracy, 2),
        fillers=fillers,
        pauses=pauses,
        wpm=wpm,
        feedback=feedback
    )
