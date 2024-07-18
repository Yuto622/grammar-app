import speech_recognition as sr
from django.shortcuts import render
from django.http import JsonResponse
from pydub import AudioSegment
from django.contrib.auth.decorators import login_required
import openai
from langchain_openai import ChatOpenAI
import os
import re
import math

from charts.models import Chart


@login_required(login_url='users/sign_in/')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='users/sign_in/')
def recognize_speech(request):
    audio_file = request.FILES['audio_file']
    audio = AudioSegment.from_file(audio_file)
    audio = audio.set_frame_rate(44100).set_sample_width(2).set_channels(1)
    audio.export("output.wav", format="wav")
    duration = math.floor(audio.duration_seconds)
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

    data, error_count = check_grammar(text, duration, request.user)
    return JsonResponse({'match': data, 'text': text, 'error_count': error_count})


def check_grammar(text_check, duration, user):
    text_1 = ("Identify any sentences with grammatical and spelling errors and provide corrections in the following "
              "format: [Original]:, [Corrected]:, [Explanation]:. If no grammatical or spelling errors are found in "
              "the sentence, print: Your sentence is correct.")

    messages = [
        ("ai", text_1),
        ("human", text_check),
    ]
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.environ.get("OPENAI_API_KEY"))
    response = llm.invoke(messages, frequency_penalty=0)
    error = response.content
    errors = re.findall(r'\[Original]:', error)
    error_count = len(errors)

    sentences = re.split(r'[.!?]', text_check)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    sentence_count = len(sentences)
    word = text_check.split()
    word_count = len(word)
    print(error)
    print(duration, error_count, sentence_count, word_count)
    chart = Chart.create_chart(
        user=user,
        duration=duration,
        error_count=error_count,
        sentence_count=sentence_count,
        word_count=word_count
    )

    return error, error_count
