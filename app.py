from flask import Flask, render_template, request, redirect
from pptx import Presentation
import difflib

app = Flask(__name__)

ppt_text_global = ""

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
    count = 0
    for word in fillers:
        count += text.lower().count(word)
    return count

# ---------- PAUSES ----------
def count_pauses(text):
    return text.count("...")

# ---------- AI FEEDBACK ----------
def generate_feedback(acc, fillers, wpm, pauses):
    feedback = []

    if acc < 30:
        feedback.append("You need to follow PPT more closely.")
    else:
        feedback.append("Good clarity.")

    if fillers > 3:
        feedback.append("Too many filler words.")
    else:
        feedback.append("Good flow.")

    if wpm < 90:
        feedback.append("Speak faster.")
    elif wpm > 160:
        feedback.append("Slow down a bit.")

    if pauses > 3:
        feedback.append("Too many pauses.")

    return feedback


# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template('dashboard.html')


@app.route('/upload', methods=['POST'])
def upload():
    global ppt_text_global
    file = request.files['ppt']
    ppt_text_global = extract_ppt_text(file)
    return redirect('/')


@app.route('/analyze', methods=['POST'])
def analyze():
    global ppt_text_global

    spoken_text = request.form.get('text', '').lower()

    if ppt_text_global.strip() == "":
        return render_template('dashboard.html', error="Upload PPT first")

    if spoken_text.strip() == "":
        return render_template('dashboard.html', error="No speech detected")

    accuracy = calculate_accuracy(ppt_text_global, spoken_text)
    fillers = count_fillers(spoken_text)
    pauses = count_pauses(spoken_text)

    words = len(spoken_text.split())
    wpm = round(words / 1.5, 2) if words > 0 else 0  # approx speech duration

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
