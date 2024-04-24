import speech_recognition as sr
from django.shortcuts import render
from language_tool_python import LanguageTool
from django.http import JsonResponse
from pydub import AudioSegment


def index(request):
    return render(request, 'index.html')


def recognize_speech(request):
    audio_file = request.FILES['audio_file']
    audio = AudioSegment.from_file(audio_file)
    audio = audio.set_frame_rate(44100).set_sample_width(2).set_channels(1)
    audio.export("output.wav", format="wav")
    sound = sr.AudioFile('output.wav')
    recognizer = sr.Recognizer()
    text = ""
    try:
        with sound as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language="en-US")

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    if text:
        text = text.capitalize()
    print(f"Text------------:{text}")
    data = check_grammar(text)
    return JsonResponse({'match': data, 'text': text})


def check_grammar(text):
    tool = LanguageTool('en-US')

    matches = tool.check(text)
    tool.close()
    data = []
    if matches:
        for match in matches:
            match_data = {'replacements': match.replacements, 'message': match.message}
            data.append(match_data)

    return data
