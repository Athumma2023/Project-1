from flask import Flask , render_template , request , send_file
from google.cloud import texttospeech , speech
import io
import os

app = Flask(__name__)

# Ensure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "brave-monitor-436720-p1-0bb03ab6d5ac.json"

# Initialize the Text-to-Speech client
tts_client = texttospeech.TextToSpeechClient()

# Initialize the Speech-to-Text client
speech_client = speech.SpeechClient()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/text-to-speech' , methods=['POST'])
def text_to_speech():
    input_text = request.form['text']

    if not input_text:
        return "No text provided" , 400

    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US" ,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(
        input=synthesis_input , voice=voice , audio_config=audio_config
    )

    return send_file(
        io.BytesIO(response.audio_content) ,
        mimetype="audio/mp3" ,
        as_attachment=True ,
        download_name="output.mp3"
    )


@app.route('/speech-to-text' , methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return "No file part" , 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file" , 400

    audio_content = file.read()
    audio = speech.RecognitionAudio(content=audio_content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS ,
        sample_rate_hertz=48000 ,  # Set to 48000 to match the WEBM OPUS header
        language_code="en-US"
    )

    response = speech_client.recognize(config=config , audio=audio)

    if response.results:
        transcript = response.results[0].alternatives[0].transcript
        return transcript
    else:
        return "No speech detected" , 400


if __name__ == '__main__':
    app.run(debug=True)