<!DOCTYPE html>
<html>
<head>
    <title>TalkTrack Dashboard</title>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
            color: white;
        }

        header {
            text-align: center;
            padding: 20px;
            font-size: 24px;
            font-weight: bold;
        }

        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
        }

        .card {
            background: rgba(255, 255, 255, 0.08);
            padding: 30px;
            border-radius: 15px;
            width: 400px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }

        input[type="file"] {
            margin-bottom: 10px;
            color: white;
        }

        button {
            border: none;
            padding: 12px 20px;
            margin: 8px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
        }

        .upload-btn {
            background: #4fc3f7;
            color: black;
        }

        .start-btn {
            background: #29b6f6;
            color: black;
        }

        .stop-btn {
            background: #ef5350;
            color: white;
        }

        .analyze-btn {
            background: #4fc3f7;
            color: black;
            width: 100%;
        }

        textarea {
            width: 100%;
            height: 80px;
            border-radius: 8px;
            border: none;
            padding: 10px;
            margin-top: 10px;
            resize: none;
        }

        hr {
            margin: 20px 0;
            border: 0.5px solid #aaa;
        }

        .results {
            text-align: left;
        }

        .results h3 {
            margin-bottom: 10px;
        }

        .feedback {
            margin-top: 10px;
        }

        ul {
            padding-left: 20px;
        }
    </style>
</head>

<body>

<header>🎤 TalkTrack Dashboard</header>

<div class="container">
    <div class="card">

        <!-- Upload -->
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <input type="file" name="ppt" required><br>
            <button class="upload-btn">Upload PPT</button>
        </form>

        <!-- Speech -->
        <textarea id="speechText" placeholder="Your speech will appear here..."></textarea>

        <!-- Buttons -->
        <div>
            <button class="start-btn" onclick="startSpeech()">▶ Start Presentation</button>
            <button class="stop-btn" onclick="stopSpeech()">■ Stop</button>
        </div>

        <!-- Analyze -->
        <form action="/analyze" method="POST" onsubmit="setText()">
            <input type="hidden" name="text" id="hiddenText">
            <button class="analyze-btn">Analyze</button>
        </form>

        <hr>

        <!-- Results -->
        {% if done %}
        <div class="results">
            <h3>📊 Results</h3>

            <p><b>Spoken:</b> {{ spoken }}</p>
            <p><b>Accuracy:</b> {{ accuracy }}%</p>
            <p><b>Fillers:</b> {{ fillers }}</p>
            <p><b>Speed:</b> {{ wpm }} WPM</p>
            <p><b>Pauses:</b> {{ pauses }}</p>

            <div class="feedback">
                <h4>🧠 AI Feedback</h4>
                <ul>
                    {% for f in feedback %}
                    <li>{{ f }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% endif %}

        {% if error %}
        <p style="color:red">{{ error }}</p>
        {% endif %}

    </div>
</div>

<script>
let recognition;

function startSpeech() {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;

    recognition.onresult = function(event) {
        let text = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            text += event.results[i][0].transcript;
        }
        document.getElementById("speechText").value = text;
    };

    recognition.start();
}

function stopSpeech() {
    recognition.stop();
}

function setText() {
    document.getElementById("hiddenText").value =
        document.getElementById("speechText").value;
}
</script>

</body>
</html>
