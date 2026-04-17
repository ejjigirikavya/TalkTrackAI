from flask import Flask, render_template, request, redirect
from pptx import Presentation
import difflib
import os

app = Flask(__name__)

# -------------------- PPT TEXT --------------------
def extract_ppt_text(file):
    prs = Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "
    return text.lower()

# -------------------- ACCURACY --------------------
def calculate_accuracy(ppt_text, spoken_text):
    if not ppt_text or not spoken_text:
        return 0

    # 1. Sequence similarity (overall)
    seq_score = difflib.SequenceMatcher(None, ppt_text, spoken_text).ratio()

    # 2. Word overlap
    ppt_words = set(ppt_text.split())
    spoken_words = set(spoken_text.split())

    if len(ppt_words) == 0:
        word_score = 0
    else:
        common_words = ppt_words.intersection(spoken_words)
        word_score = len(common_words) / len(ppt_words)

    # 3. Combine both (weighted)
    final_score = (0.6 * seq_score) + (0.4 * word_score)

    return round(final_score * 100, 2)
# -------------------- FILLERS --------------------
def count_fillers(text):
    fillers = ["um", "uh", "like", "you know", "basically", "and"]
    count = 0
    for word in fillers:
        count += text.lower().count(word)
    return count

# -------------------- PAUSES --------------------
def count_pauses(text):
    return text.count("...")

# -------------------- SPEED (FIXED HUMAN RANGE) --------------------
def calculate_wpm(text):
    words = len(text.split())
    wpm = words * 3

    if wpm < 60:
        return 60
    elif wpm > 150:
        return 150
    else:
        return wpm

# -------------------- AI FEEDBACK --------------------
def generate_ai_feedback(acc, fillers, wpm, pauses):
    feedback = []

    if acc < 50:
        feedback.append("You need to follow PPT more closely.")
    else:
        feedback.append("Good clarity.")

    if fillers > 3:
        feedback.append("Avoid filler words.")

    if wpm > 120:
        feedback.append("Slow down.")
    elif wpm < 70:
        feedback.append("Speak faster.")

    if pauses > 5:
        feedback.append("Too many pauses.")
    else:
        feedback.append("Good flow.")

    return feedback

# -------------------- ROUTES --------------------
@app.route('/')
def home():
    return render_template('index.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/dashboard')
    return render_template('index.html')

# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect('/login')
    return render_template('signup.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', done=False)

# UPLOAD PPT
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('ppt')
    if file:
        file.save("uploaded.pptx")
    return redirect('/dashboard')

# ANALYZE (SAFE VERSION)
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        spoken_text = request.form.get('text', '').lower()

        if not spoken_text.strip():
            return render_template('dashboard.html',
                                   error="No speech detected",
                                   done=False)

        ppt_text = ""
        if os.path.exists("uploaded.pptx"):
            ppt_text = extract_ppt_text("uploaded.pptx")

        acc = calculate_accuracy(ppt_text, spoken_text)
        fillers = count_fillers(spoken_text)
        pauses = count_pauses(spoken_text)
        wpm = calculate_wpm(spoken_text)
        feedback = generate_ai_feedback(acc, fillers, wpm, pauses)

        return render_template('dashboard.html',
                               done=True,
                               spoken=spoken_text,
                               accuracy=acc,
                               fillers=fillers,
                               pauses=pauses,
                               wpm=wpm,
                               feedback=feedback)

    except Exception as e:
        return f"Error: {str(e)}"

# RUN
if __name__ == '__main__':
    app.run(debug=True)
