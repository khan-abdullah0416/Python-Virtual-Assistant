from time import ctime, sleep
import pyrebase
import pyttsx3
import datetime
import speech_recognition as sr
import webbrowser

# Firebase Database
firebaseConfig = {
    "apiKey": "AIzaSyAkD-Ehz2IOwx4iA3jL_dZPpzog3vaaY94",
    "authDomain": "home-automation-794c1.firebaseapp.com",
    "databaseURL": "https://home-automation-794c1-default-rtdb.firebaseio.com",
    "projectId": "home-automation-794c1",
    "storageBucket": "home-automation-794c1.appspot.com",
    "messagingSenderId": "204270994860",
    "appId": "1:204270994860:web:2372c400f7c7f0cd272609",
}

firebase = pyrebase.initialize_app(firebaseConfig)
fb_db = firebase.database()

# Initialize the recognizer
r = sr.Recognizer()

# Initialize the Text to Speech _engine
speech_engine = pyttsx3.init()


def website_input(first=True):
    myGetResults = fb_db.child('/command').get()
    myGetResults = myGetResults.val()

    mostrecentKeyID = 0
    mostrecentTimestamp = 0

    if myGetResults == None:
        pass
    else:
        # To get the most recent input
        for keyID in myGetResults:
            if int(int(myGetResults[keyID]['Time']) > mostrecentTimestamp):
                mostrecentTimestamp = int(myGetResults[keyID]['Time'])
                mostrecentKeyID = myGetResults[keyID]

        out = str(myGetResults[keyID]['Input'])

        if ('add' in out) and (first == True):
            fb_db.child('/command').remove()
            speak('What do you want to add to your to do list?')
            sleep(3)
            website_input(first=False)
        elif first == False:
            to_do_dict = {
            'To Do': out,
            }
            fb_db.child('/to-do').push(to_do_dict)
            speak('Added ' + out + ' to the to do list.')
            fb_db.child('/command').remove()
        else:
            respond(voice_data=out)
            fb_db.child('/command').remove()


def upload(voice_data, person):

    if person == True:
        now = int(datetime.datetime.today().strftime("%Y%m%d%H%M%S"))
        voice_log = {
            'Output': 'Person: ' + voice_data,
            'Time': now,
        }
        fb_db.child('/virtual_assistant/voice_log').push(voice_log)
    else:
        now = int(datetime.datetime.today().strftime("%Y%m%d%H%M%S"))
        voice_log = {
            'Output': 'Bot: ' + voice_data,
            'Time': now,
        }
        fb_db.child('/virtual_assistant/voice_log').push(voice_log)


def speak(audio_string):

    voices = speech_engine.getProperty("voices")
    speech_engine.setProperty("voice", voices[1].id)
    speech_engine.setProperty("rate", 160)
    speech_engine.say(audio_string)
    speech_engine.runAndWait()
    upload(audio_string, False)


def record_audio(ask=False):

    with sr.Microphone() as source:

        if ask:
            speak(ask)

        audio = r.listen(source)
        voice_data = ''

        try:
            voice_data = r.recognize_google(audio)
            upload(voice_data, True)
        except sr.UnknownValueError:
            speak('Sorry, I did not get that.')
        except sr.RequestError:
            speak('Sorry, the service is down.')

        return voice_data


def respond(voice_data):

    # Name
    if ('what is your name' in voice_data):
        speak('My name is Alexa.')

    # Time
    elif ('time' in voice_data):
        speak(ctime())

    # Search
    elif ('search' in voice_data):
        search = record_audio('What do you want to search for?')
        url = 'https://google.com/search?q=' + search
        webbrowser.get().open(url)
        speak('Here is what I found for ' + search)

    # Location
    elif ('find location' in voice_data):
        location = record_audio('What is the location?')
        url = 'https://google.nl/maps/place/' + location + '/&amp;'
        webbrowser.get().open(url)
        speak('Here is the location of ' + location)

    # To-Do List

    # Create
    elif ('add' in voice_data):
        to_do = record_audio('What do you want to add to your to do list?')
        to_do_dict = {
            'To Do': to_do,
        }
        fb_db.child('/to-do').push(to_do_dict)
        speak('Added ' + to_do + ' to the to do list.')

    # Delete
    elif ('remove' in voice_data):
        fb_db.child('/to-do').remove()
        speak('Removed all tasks')

    # Turn Off
    elif ('off' in voice_data):
        exit()


speak('Hello, what would you like to do?')

while True:
    voice_data = record_audio()
    respond(voice_data)
    website_input()
