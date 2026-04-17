from flask import Flask, render_template, request, redirect
from pptx import Presentation
import difflib
import os

app = Flask(__name__)

# GLOBAL STORAGE (IMPORTANT FIX)
ppt_text_global = ""


# ----------- EXTRACT PPT TEXT -----------
def extract_ppt_text(file):
    prs = Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + " "
    return text.lower()


# ----------- ACCURACY -----------
def calculate_accuracy(ppt_text, spoken_text):
    return round(difflib.SequenceMatcher(None, ppt_text, spoken_text).ratio() * 100, 2)


# ----------- FILLERS -----------
def count_fillers(text):
    fillers = ["um", "uh", "like", "you know", "basically", "and"]
    count = 0
    for word in fillers:
        count += text.lower().count(word)
    return count


# ----------- PAUSES -----------
def count_pauses(text):
    return text.count("...")


# ----------- AI FEEDBACK -----------
def generate_ai_feedback(acc, fillers, wpm, pauses):
    feedback = []

    if acc < 40:
        feedback.append("You need to follow PPT more closely.")
    else:
        feedback.append("Good clarity.")

    if fillers > 3:
        feedback.append("Reduce filler words.")
    else:
        feedback.append("Good fluency.")

    if wpm < 70:
        feedback.append("Speak faster.")
    elif wpm > 150:
        feedback.append("Slow down.")
    else:
        feedback
