<h2>Dashboard</h2>

<form action="/upload" method="POST" enctype="multipart/form-data">
    <input type="file" name="ppt">
    <button>Upload PPT</button>
</form>

<br>

<textarea id="speechText" rows="4" cols="50"></textarea><br><br>

<button onclick="startSpeech()">Start</button>
<button onclick="stopSpeech()">Stop</button>

<form id="form" action="/analyze" method="POST">
    <input type="hidden" name="text" id="hiddenText">
</form>

{% if error %}
<p style="color:red">{{error}}</p>
{% endif %}

{% if spoken %}
<h3>Results</h3>
<p>Accuracy: {{accuracy}}</p>
<p>Fillers: {{fillers}}</p>
<p>WPM: {{wpm}}</p>
<p>Pauses: {{pauses}}</p>

<ul>
{% for f in feedback %}
<li>{{f}}</li>
{% endfor %}
</ul>
{% endif %}

<script>
let recognition;

function startSpeech(){
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;

    recognition.onresult = function(e){
        let text = "";
        for(let i=0;i<e.results.length;i++){
            text += e.results[i][0].transcript;
        }
        document.getElementById("speechText").value = text;
    };

    recognition.start();
}

function stopSpeech(){
    recognition.stop();

    setTimeout(()=>{
        document.getElementById("hiddenText").value =
            document.getElementById("speechText").value;

        document.getElementById("form").submit();
    }, 500);
}
</script>
