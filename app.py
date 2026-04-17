from flask import Flask, render_template, request, redirect, session
from pptx import Presentation
import difflib

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- EXTRACT PPT ----------
def extract_ppt_text(file):
    prs = Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "
    return text.lower()

# ---------- ACCURACY ----------
def calculate_accuracy(ppt_text, spoken_text):
    return round(difflib.SequenceMatcher(None, ppt_text, spoken_text).ratio() * 100, 2)

# ---------- FILLERS ----------
def count_fillers(text):
    fillers = ["um", "uh", "like", "you know", "basically", "and"]
    return sum(text.count(word) for word in fillers)

# ---------- PAUSES ----------
def count_pauses(text):
    return text.count("...")

# ---------- FEEDBACK ----------
def generate_feedback(acc, fillers, wpm, pauses):
    feedback = []

    if acc < 30:
        feedback.append("Follow PPT more closely.")
    else:
        feedback.append("Good clarity.")

    if fillers > 3:
        feedback.append("Too many filler words.")
    else:
        feedback.append("Good flow.")

    if wpm < 90:
        feedback.append("Speak faster.")
    elif wpm > 160:
        feedback.append("Slow down.")

    if pauses > 3:
        feedback.append("Too many pauses.")

    return feedback


# ---------- ROUTES ----------

# LOGIN PAGE (index.html)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/dashboard')
    return render_template('index.html')


# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect('/')
    return render_template('signup.html')


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# UPLOAD PPT
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('ppt')

    if not file:
        return render_template('dashboard.html', error="No file selected")

    ppt_text = extract_ppt_text(file)

    # store in session (IMPORTANT)
    session['ppt_text'] = ppt_text

    return redirect('/dashboard')


# ANALYZE (STOP BUTTON CALLS THIS)
@app.route('/analyze', methods=['POST'])
def analyze():
    ppt_text = session.get('ppt_text', '')
    spoken_text = request.form.get('text', '').lower()

    if ppt_text.strip() == "":
        return render_template('dashboard.html', error="Upload PPT first")

    if spoken_text.strip() == "":
        return render_template('dashboard.html', error="No speech detected")

    accuracy = calculate_accuracy(ppt_text, spoken_text)
    fillers = count_fillers(spoken_text)
    pauses = count_pauses(spoken_text)

    words = len(spoken_text.split())
    wpm = round(words / 1.5, 2) if words else 0

    feedback = generate_feedback(accuracy, fillers, wpm, pauses)

    return render_template(
        'dashboard.html',
        spoken=spoken_text,
        accuracy=accuracy,
        fillers=fillers,
        wpm=wpm,
        pauses=pauses,
        feedback=feedback
    )


if __name__ == '__main__':
    app.run(debug=True)
