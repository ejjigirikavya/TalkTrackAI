from flask import Flask, render_template, request, redirect, url_for
from pptx import Presentation
import difflib
import re

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

    spoken = request.form.get('text', '').lower()

    if spoken.strip() == "":
        return render_template('dashboard.html', error="No speech detected")

   # ---------- CLEAN WORDS ----------
spoken_words = re.findall(r'\b\w+\b', spoken)
ppt_words = re.findall(r'\b\w+\b', ppt_text)

# ---------- ACCURACY (WORD MATCH BASED) ----------
common_words = set(spoken_words) & set(ppt_words)

if spoken_words:
    accuracy = (len(common_words) / len(spoken_words)) * 100
else:
    accuracy = 0


# ---------- FILLER WORDS ----------
filler_list = ["um", "uh", "like", "basically", "actually", "so"]

fillers = sum(1 for word in spoken_words if word in filler_list)


# ---------- PAUSES (ESTIMATION) ----------
pauses = len(spoken_words) // 7
    # Speed
    wpm = len(spoken.split())

    # Feedback
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



