from flask import Flask, render_template, request, redirect, url_for
from pptx import Presentation
import difflib

app = Flask(__name__)

# 🔥 store ppt text safely
ppt_text_store = {"text": ""}


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
@app.route('/')
def login():
    return render_template('index.html')


# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# ---------- UPLOAD ----------
@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files.get('ppt')

        if not file:
            return render_template('dashboard.html', error="No file selected")

        # ✅ extract and store text (NO FILE SAVE)
        ppt_text_store["text"] = extract_ppt_text(file)

        return redirect(url_for('dashboard'))

    except Exception as e:
        return render_template('dashboard.html', error=f"Upload error: {str(e)}")


# ---------- ANALYZE ----------
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        spoken = request.form.get('text', '').strip().lower()

        if spoken == "":
            return render_template('dashboard.html', error="No speech detected")

        ppt_text = ppt_text_store["text"]

        if ppt_text.strip() == "":
            return render_template('dashboard.html', error="Upload PPT first")

        # ---------- ACCURACY ----------
        accuracy = difflib.SequenceMatcher(None, spoken, ppt_text).ratio() * 100

        # ---------- FILLERS ----------
        filler_words = ["um", "uh", "like", "you know", "basically"]
        words = spoken.split()
        fillers = sum(1 for word in words if word in filler_words)

        # ---------- PAUSES ----------
        pauses = spoken.count(",") + spoken.count("...") + spoken.count("  ")

        # ---------- SPEED ----------
        word_count = len(words)
        duration = max(word_count * 0.5, 1)
        wpm = (word_count / duration) * 60

        # ---------- FEEDBACK ----------
        feedback = []

        if accuracy < 40:
            feedback.append("Follow PPT more closely")
        elif accuracy < 75:
            feedback.append("Good attempt, improve alignment")
        else:
            feedback.append("Excellent alignment")

        if fillers == 0:
            feedback.append("No filler words – great job")
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

    except Exception as e:
        # 🔥 prevents 500 crash
        return render_template('dashboard.html', error=f"Analyze error: {str(e)}")


# ---------- SAFETY ----------
@app.route('/analyze', methods=['GET'])
def analyze_get():
    return redirect(url_for('dashboard'))


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
