from flask import Flask, render_template, request, redirect, url_for
from pptx import Presentation
import difflib

app = Flask(__name__)

# Global storage
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


# ---------- UPLOAD PPT ----------
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

    # Calculate accuracy
    if ppt_text:
        accuracy = difflib.SequenceMatcher(None, spoken, ppt_text).ratio() * 100
    else:
        accuracy = 0

    # Metrics
    fillers = sum(spoken.count(w) for w in ["um", "uh", "like"])
    pauses = spoken.count("...")
    wpm = len(spoken.split())

    # Feedback
    feedback = []

    if accuracy < 40:
        feedback.append("Follow PPT more closely")
    else:
        feedback.append("Good clarity")

    if fillers > 3:
        feedback.append("Reduce filler words")

    if wpm < 70:
        feedback.append("Speak faster")

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


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
