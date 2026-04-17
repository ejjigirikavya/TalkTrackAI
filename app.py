from flask import Flask, render_template, request, redirect
from pptx import Presentation
import difflib
import os

app = Flask(__name__)

# ✅ IMPORTANT (works on Render)
UPLOAD_PATH = os.path.join(os.getcwd(), "uploaded.pptx")


# ---------------- PPT TEXT ----------------
def extract_ppt_text(file):
    prs = Presentation(file)
    text = ""

    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "

    return text


# ---------------- CLEAN ----------------
def clean_text(text):
    return " ".join(text.lower().split())


# ---------------- ACCURACY ----------------
def calculate_accuracy(ppt_text, spoken_text):
    if not ppt_text or not spoken_text:
        return 0

    return round(
        difflib.SequenceMatcher(None, ppt_text, spoken_text).ratio() * 100, 2
    )


# ---------------- FILLERS ----------------
def count_fillers(text):
    fillers = ["um", "uh", "like", "you know", "basically", "and"]
    return sum(text.count(word) for word in fillers)


# ---------------- PAUSES ----------------
def count_pauses(text):
    return text.count("...")


# ---------------- SPEED ----------------
def calculate_wpm(text):
    words = len(text.split())
    wpm = words * 3

    return max(60, min(wpm, 150))


# ---------------- FEEDBACK ----------------
def generate_ai_feedback(acc, fillers, wpm, pauses):
    feedback = []

    if acc < 30:
        feedback.append("You need to follow PPT more closely.")
    else:
        feedback.append("Good content alignment.")

    if fillers > 3:
        feedback.append("Reduce filler words.")
    else:
        feedback.append("Good clarity.")

    if wpm > 130:
        feedback.append("Slow down.")
    elif wpm < 70:
        feedback.append("Speak faster.")
    else:
        feedback.append("Good flow.")

    if pauses > 5:
        feedback.append("Too many pauses.")
    else:
        feedback.append("Good pacing.")

    return feedback


# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    return redirect('/dashboard')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect('/')
    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', done=False)


# ✅ UPLOAD FIXED
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('ppt')

    if not file or file.filename == '':
        return render_template("dashboard.html", error="No file selected", done=False)

    file.save(UPLOAD_PATH)

    print("Saved:", UPLOAD_PATH)
    print("Exists:", os.path.isfile(UPLOAD_PATH))

    return render_template("dashboard.html", message="PPT uploaded!", done=False)


# ✅ ANALYZE FIXED
@app.route('/analyze', methods=['POST'])
def analyze():
    spoken_text = request.form.get('text', "").lower()

    if not spoken_text.strip():
        return render_template("dashboard.html", error="No speech detected", done=False)

    if not os.path.isfile(UPLOAD_PATH):
        return render_template("dashboard.html", error="Upload PPT first", done=False)

    ppt_text = extract_ppt_text(UPLOAD_PATH)

    ppt_text = clean_text(ppt_text)
    spoken_text = clean_text(spoken_text)

    accuracy = calculate_accuracy(ppt_text, spoken_text)
    fillers = count_fillers(spoken_text)
    pauses = count_pauses(spoken_text)
    wpm = calculate_wpm(spoken_text)

    feedback = generate_ai_feedback(accuracy, fillers, wpm, pauses)

    return render_template(
        "dashboard.html",
        spoken=spoken_text,
        accuracy=accuracy,
        fillers=fillers,
        pauses=pauses,
        wpm=wpm,
        feedback=feedback,
        done=True
    )


if __name__ == '__main__':
    app.run(debug=True)
