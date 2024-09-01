from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import speech_recognition as sr
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize the recognizer
r = sr.Recognizer()
listening = True  # Global variable to control the listening loop

def simulate_accuracy(text):
    accuracy = random.uniform(85, 100)
    return round(accuracy, 2)

def simulate_pronunciation(text):
    pronunciation = random.uniform(80, 100)
    return round(pronunciation, 2)

def recognize_speech():
    global listening
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        emit('listening', {'status': 'Listening...'}, broadcast=True)
        print("Listening...")

        while listening:
            emit('listening', {'status': 'Listening...'}, broadcast=True)
            audio = r.listen(source)

            if not listening:
                # Break out of the loop if listening is stopped
                break

            emit('listening', {'status': 'Processing...'}, broadcast=True)
            print("Processing...")
            try:
                text = r.recognize_google(audio)
                accuracy = simulate_accuracy(text)
                pronunciation = simulate_pronunciation(text)
                emit('speech_recognized', {'text': text, 'accuracy': accuracy, 'pronunciation': pronunciation}, broadcast=True)
            except sr.UnknownValueError:
                emit('speech_recognized', {'text': "Sorry, I could not understand the audio", 'accuracy': 0, 'pronunciation': 0}, broadcast=True)
            except sr.RequestError as e:
                emit('speech_recognized', {'text': f"Could not request results; {e}", 'accuracy': 0, 'pronunciation': 0}, broadcast=True)

        # Emit 'Not Listening' status when done
        emit('listening', {'status': 'Not Listening'}, broadcast=True)
        print("Stopped Listening")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_listening')
def handle_start_listening():
    global listening
    listening = True  # Set listening to True when starting
    recognize_speech()

@socketio.on('stop_listening')
def handle_stop_listening():
    global listening
    listening = False  # Set listening to False to stop the loop
    emit('listening', {'status': 'Not Listening'}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)