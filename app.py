from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pptx import Presentation
import difflib
import os

app = Flask(__name__)

ppt_text = ""


# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------- PPT TEXT ----------
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
    matcher = difflib.SequenceMatcher(None, ppt_text, spoken_text.lower())
    return round(matcher.ratio() * 100, 2)


# ---------- FILLERS ----------
filler_words = ["um", "uh", "like", "you know", "basically"]

def count_fillers(text):
    words = text.lower().split()
    return sum(1 for word in words if word in filler_words)


# ---------- PAUSES ----------
def count_pauses(text):
    return text.count(",") + text.count("...") + text.count("  ")


# ---------- ANALYSIS ----------
def analyze_speech(text):
    words = text.split()
    word_count = len(words)

    duration = max(word_count * 0.5, 1)  # estimate speaking time

    wpm = (word_count / duration) * 60
    fillers = count_fillers(text)
    pauses = count_pauses(text)

    return fillers, round(wpm, 2), pauses


# ---------- AI FEEDBACK ----------
def generate_ai_feedback(acc, fillers, wpm, pauses):
    feedback = []

    if acc < 40:
        feedback.append("Follow PPT more closely.")
    elif acc < 75:
        feedback.append("Good attempt, improve alignment.")
    else:
        feedback.append("Excellent presentation!")

    if fillers == 0:
        feedback.append("Great! No filler words used.")
    elif fillers > 3:
        feedback.append("Reduce filler words.")

    if wpm < 70:
        feedback.append("Speak faster.")
    elif wpm > 150:
        feedback.append("Slow down.")
    else:
        feedback.append("Good speaking speed.")

    if pauses == 0:
        feedback.append("Smooth delivery.")
    elif pauses > 3:
        feedback.append("Too many pauses.")

    return feedback


# ---------- ROUTES ----------

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    if cur.fetchone():
        conn.close()
        return render_template('signup.html', error="User already exists")

    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()

    conn.close()

    if user:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Invalid Credentials")


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# ---------- UPLOAD PPT ----------
@app.route('/upload', methods=['POST'])
def upload():
    global ppt_text

    file = request.files.get('ppt')

    if file:
        filepath = os.path.join("uploaded.pptx")
        file.save(filepath)
        ppt_text = extract_ppt_text(filepath)

    return redirect('/dashboard')


# ---------- ANALYZE ----------
@app.route('/analyze', methods=['POST'])
def analyze():
    global ppt_text

    spoken = request.form.get("text", "").strip().lower()

    if spoken == "":
        return render_template('dashboard.html', error="No speech detected!")

    if ppt_text.strip() == "":
        return render_template('dashboard.html', error="Upload PPT first!")

    # calculations
    accuracy = calculate_accuracy(ppt_text, spoken)
    fillers, wpm, pauses = analyze_speech(spoken)
    feedback = generate_ai_feedback(accuracy, fillers, wpm, pauses)

    return render_template(
        'dashboard.html',
        spoken=spoken,
        accuracy=accuracy,
        fillers=fillers,
        pauses=pauses,
        wpm=wpm,
        feedback=feedback
    )


# ---------- RUN ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
