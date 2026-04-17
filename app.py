from flask import Flask, render_template, request, redirect, url_for
from pptx import Presentation
import difflib

app = Flask(__name__)

ppt_text = ""   # simple global (works reliably)


# ---------- EXTRACT PPT ----------
def extract_ppt_text(file):
    prs = Presentation(file)
    text = ""

    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "

    return text.lower()


# ---------- ROUTES ----------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/upload', methods=['POST'])
def upload():
    global ppt_text

    file = request.files.get('ppt')
    if file:
        ppt_text = extract_ppt_text(file)

    return redirect(url_for('dashboard'))


@app.route('/analyze', methods=['POST'])
def analyze():
    global ppt_text

    spoken = request.form.get('text', '').lower()

    if spoken.strip() == "":
        return render_template('dashboard.html', error="No speech detected")

    # 🔥 IMPORTANT: no blocking error
    if ppt_text:
        accuracy = difflib.SequenceMatcher(None, spoken, ppt_text).ratio() * 100
    else:
        accuracy = 0

    fillers = sum(spoken.count(w) for w in ["um", "uh", "like"])
    pauses = spoken.count("...")
    wpm = len(spoken.split())

    feedback = []
    if accuracy < 40:
        feedback.append("Follow PPT more closely")
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


if __name__ == "__main__":
    app.run(debug=True)
