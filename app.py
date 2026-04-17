from flask import Flask, render_template, request, redirect
from pptx import Presentation
import difflib
import os

app = Flask(__name__)

# ---------------- PPT TEXT ----------------
def extract_ppt_text(file):
    prs = Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "
    return text.lower()


# ---------------- ACCURACY ----------------
def calculate_accuracy(ppt_text, spoken_text):
    if not ppt_text:
        return 0
    return round(difflib.SequenceMatcher(None, ppt_text, spoken_text).ratio() * 100, 2)


# ---------------- FILLERS ----------------
def count_fillers(text):
    fillers = ["um", "uh", "like", "you know", "basically", "and"]
    return sum(text.count(word) for word in fillers)


# ---------------- PAUSES ----------------
def count_pauses(text):
    return text.count("...")


# ---------------- FEEDBACK ----------------
def generate_ai_feedback(acc, fillers, wpm, pauses):
    feedback = []

    if acc < 40:
        feedback.append("Follow PPT more closely.")
    else:
        feedback.append("Good alignment with PPT.")

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


# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', done=False)


# ---------------- UPLOAD ----------------
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('ppt')

    if file:
        file.save("uploaded.pptx")
        return render_template("dashboard.html", message="PPT uploaded!", done=False)

    return render_template("dashboard.html", error="No file selected", done=False)


# ---------------- ANALYZE (STOP BUTTON TRIGGERS THIS) ----------------
@app.route('/analyze', methods=['POST'])
def analyze():
    spoken_text = request.form.get('text', '').lower()

    if not spoken_text.strip():
        return render_template('dashboard.html', error="No speech detected", done=False)

    # ✅ NO BLOCKING (IMPORTANT FIX)
    if os.path.exists("uploaded.pptx"):
        ppt_text = extract_ppt_text("uploaded.pptx")
        accuracy = calculate_accuracy(ppt_text, spoken_text)
    else:
        accuracy = 0  # Still allow results

    fillers = count_fillers(spoken_text)
    pauses = count_pauses(spoken_text)
    wpm = len(spoken_text.split())

    feedback = generate_ai_feedback(accuracy, fillers, wpm, pauses)

    return render_template(
        'dashboard.html',
        done=True,
        spoken=spoken_text,
        accuracy=accuracy,
        fillers=fillers,
        pauses=pauses,
        wpm=wpm,
        feedback=feedback
    )


if __name__ == '__main__':
    app.run(debug=True)
