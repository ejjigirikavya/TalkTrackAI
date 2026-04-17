from flask import Flask, render_template, request, redirect, url_for
from pptx import Presentation
import difflib
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
@app.route('/analyze', methods=['POST'])
def analyze():
    global ppt_text

    spoken = request.form.get('text', '').strip().lower()

    if spoken == "":
        return render_template('dashboard.html', error="No speech detected")

    # ---------- ACCURACY (IMPROVED) ----------
    if ppt_text.strip() != "":
        matcher = difflib.SequenceMatcher(None, spoken, ppt_text)
        accuracy = matcher.ratio() * 100
    else:
        return render_template('dashboard.html', error="Upload PPT first")

    # ---------- FILLER WORDS (IMPROVED) ----------
    filler_words = ["um", "uh", "like", "you know", "basically"]
    words = spoken.split()

    fillers = sum(1 for word in words if word in filler_words)

    # ---------- PAUSES (BETTER LOGIC) ----------
    pauses = (
        spoken.count(",") +      # natural pauses
        spoken.count("...") +    # long pauses
        spoken.count("  ")       # double space hesitation
    )

    # ---------- SPEED (REALISTIC) ----------
    word_count = len(words)
    duration = max(word_count * 0.5, 1)   # assume 0.5 sec per word
    wpm = (word_count / duration) * 60

    # ---------- AI FEEDBACK ----------
    feedback = []

    if accuracy < 40:
        feedback.append("Follow PPT more closely")
    elif accuracy < 75:
        feedback.append("Good attempt, improve alignment")
    else:
        feedback.append("Excellent alignment with PPT")

    if fillers == 0:
        feedback.append("Great! No filler words used")
    elif fillers > 3:
        feedback.append("Reduce filler words")

    if pauses == 0:
        feedback.append("Smooth speech delivery")
    elif pauses > 3:
        feedback.append("Too many pauses")

    if wpm < 70:
        feedback.append("Speak faster")
    elif wpm > 150:
        feedback.append("Slow down")
    else:
        feedback.append("Good speaking speed")

    return render_template(
        'dashboard.html',
        spoken=spoken,
        accuracy=round(accuracy, 2),
        fillers=fillers,
        pauses=pauses,
        wpm=round(wpm, 2),
        feedback=feedback
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
