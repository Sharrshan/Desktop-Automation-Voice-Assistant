import speech_recognition as sr
import os
import platform
import time
from datetime import date
from datetime import datetime
from gtts import gTTS
from playsound import playsound
import psutil
import pyautogui
import fitz  # PyMuPDF
import pytesseract
import re
import subprocess
import requests

# --- Configuration (Update if necessary) ---
# For Windows users, if Tesseract is not in your PATH, update this line:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- Core Functions ---
def speak(text):
    """Converts text to speech and plays it."""
    print(f"Assistant: {text}")
    try:
        tts = gTTS(text=text, lang='en')
        filename = "voice.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Speech Error: {e}")

def listen_for_command():
    """Listens for a command and returns it as text."""
    r = sr.Recognizer()
    # Replace X with the correct index number for your microphone
    with sr.Microphone(device_index=2) as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except (sr.UnknownValueError, sr.RequestError):
        return None

# --- Skill Functions ---

def handle_time():
    """Tells the current time."""
    now = datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {now}")

def handle_open_app(command):
    """Opens a specified application."""
    app_name = command.replace("open", "").strip()
    try:
        if platform.system() == "Windows":
            os.system(f"start {app_name}")
        elif platform.system() == "Darwin": # macOS
            os.system(f"open -a \"{app_name}\"")
        else: # Linux
            os.system(app_name)
        speak(f"Opening {app_name}")
    except Exception:
        speak(f"Sorry, I couldn't open {app_name}.")

def handle_shutdown():
    """Shuts down the computer after confirmation."""
    speak("Are you sure you want to shut down? Please say yes to confirm.")
    confirmation = listen_for_command()
    if confirmation and "yes" in confirmation:
        speak("Shutting down. Goodbye.")
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
        else:
            os.system("sudo shutdown now")
    else:
        speak("Shutdown cancelled.")

def handle_volume(command):
    """Controls system volume and handles missing numbers."""
    os_name = platform.system()

    if "mute" in command:
        # Mute logic remains the same
        if os_name == "Windows":
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            from ctypes import cast, POINTER
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1, None)
        elif os_name == "Darwin":
            os.system("osascript -e 'set volume with output muted'")
        speak("Volume muted.")
        return

    # Find a number in the command
    match = re.search(r'\d+', command)

    # Check if a number was actually found
    if match:
        level = int(match.group())
        if 0 <= level <= 100:
            if os_name == "Windows":
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from comtypes import CLSCTX_ALL
                from ctypes import cast, POINTER
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level / 100, None)
            elif os_name == "Darwin":
                os.system(f"osascript -e 'set volume output volume {level}'")
            speak(f"Volume set to {level} percent.")
        else:
            speak("Please specify a volume level between 0 and 100.")
    else:
        # If no number was found in the command
        speak("Please specify a volume level. For example, 'set volume to 50'.")

def handle_media(command):
    """Controls media player with play/pause/next/previous."""
    if "play" in command or "pause" in command:
        pyautogui.press('playpause')
    elif "next" in command:
        pyautogui.press('nexttrack')
    elif "previous" in command:
        pyautogui.press('prevtrack')

def handle_timer(command):
    """Sets a timer for a specified duration."""
    try:
        duration_str = re.search(r'\d+', command).group()
        duration = int(duration_str)
        unit = "seconds"
        if "minute" in command:
            duration *= 60
            unit = "minutes"
        
        speak(f"Timer set for {duration_str} {unit}.")
        time.sleep(duration)
        speak("Time's up!")
        playsound("voice.mp3") # Reuse the voice file as a simple alarm
    except Exception:
        speak("Sorry, I couldn't set a timer. Please specify a number.")

def handle_status():
    """Reports system status like battery and CPU."""
    cpu_usage = psutil.cpu_percent()
    speak(f"The CPU usage is at {cpu_usage} percent.")
    battery = psutil.sensors_battery()
    if battery:
        speak(f"Battery is at {battery.percent} percent.")

def handle_screen_reader():
    """Reads the text from the current screen using OCR."""
    speak("Reading the screen now.")
    try:
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot)
        if text.strip():
            speak("Here is what I found on the screen.")
            print(text) # Also print for review
            # Speaking long text can be slow, so we can speak a summary
            speak(text.split('\n')[0])
        else:
            speak("I couldn't find any text on the screen.")
    except Exception as e:
        speak(f"Sorry, I couldn't read the screen. Error: {e}")

def handle_calculator(command):
    """Performs basic arithmetic calculations, converting words to operators."""
    try:
        # Remove the trigger word and clean up the string
        term = command.replace("calculate", "").strip()

        # Replace spoken words with operators
        term = term.replace("x", "*").replace("times", "*")
        term = term.replace("plus", "+")
        term = term.replace("minus", "-")
        term = term.replace("divided by", "/")

        # Sanitize input to prevent security risks with eval()
        allowed_chars = "0123456789+-*/.() "
        if all(char in allowed_chars for char in term):
            result = eval(term)
            speak(f"The result is {result}")
        else:
            speak("Sorry, that looks like an invalid calculation.")
    except Exception:
        speak("I couldn't calculate that. Please state it clearly, for example: 'calculate 5 times 3'.")

def handle_file_search(command):
    """Finds files with a specific extension in a directory."""
    try:
        parts = command.split("in")
        extension = parts[0].replace("find", "").replace("files", "").strip()
        directory = parts[1].strip()
        # Common directory shortcuts
        if "downloads" in directory:
            directory = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        speak(f"Searching for {extension} files in {directory}.")
        found_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(f".{extension}"):
                    found_files.append(file)
        
        if found_files:
            speak(f"I found {len(found_files)} files. Here are the first few:")
            for f in found_files[:5]:
                speak(f)
        else:
            speak("I couldn't find any matching files.")
    except Exception:
        speak("Sorry, please specify the file type and directory clearly.")

def handle_pdf_search(command):
    """Searches for text within a specified PDF file."""
    try:
        parts = command.split("for")
        pdf_path = parts[0].replace("search pdf", "").strip()
        search_term = parts[1].strip()

        if not os.path.exists(pdf_path):
            speak("Sorry, I can't find that PDF file.")
            return

        speak(f"Searching for '{search_term}' in {os.path.basename(pdf_path)}.")
        doc = fitz.open(pdf_path)
        found_pages = []
        for page_num, page in enumerate(doc):
            if page.search_for(search_term):
                found_pages.append(str(page_num + 1))
        
        if found_pages:
            speak(f"I found the term on pages: {', '.join(found_pages)}")
        else:
            speak("The specified text was not found in this PDF.")
    except Exception:
        speak("Sorry, please specify the PDF path and search term.")

def get_weather(city="Bangalore"):
    """Fetches and returns the weather for a given city."""
    # --- Paste your OpenWeatherMap API key here ---
    API_KEY = "9ed85a34b15e9fc1461c1484e705ae0b"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    request_url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(request_url)
    
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = round(data['main']['temp'])
        return f"The current weather in {city} is {temperature} degrees Celsius with {weather}."
    else:
        return "Sorry, I couldn't fetch the weather right now."
        
from datetime import date

def handle_daily_briefing():
    """Provides a daily briefing with date, weather, and news."""
    # 1. Greet and give the date
    today = date.today().strftime("%B %d, %Y")
    speak(f"Good morning! Today is {today}.")
    
    # 2. Get the weather
    weather_report = get_weather() # Uses the default city "Ballari"
    speak(weather_report)

# --- Main Application Loop ---
def main():
    """Main function to run the voice assistant."""
    commands = {
        "what time is it": handle_time,
        "open": handle_open_app,
        "shutdown computer": handle_shutdown,
        "set volume to": handle_volume,
        "mute volume": handle_volume,
        "play": handle_media, "pause": handle_media, "next": handle_media, "previous": handle_media,
        "set a timer for": handle_timer,
        "system status": handle_status,
        "read the screen": handle_screen_reader,
        "calculate": handle_calculator,
        "find": handle_file_search,
        "search pdf": handle_pdf_search,
        "daily briefing": handle_daily_briefing,
        "good morning": handle_daily_briefing,
        "what's the update": handle_daily_briefing,
    }

    wake_word = "computer"
    speak("Assistant activated. Say the wake word to begin.")

    while True:
        print("\nWaiting for a command...")
        command = listen_for_command()

        if not command:
            continue

        # 1. First, check for a deactivation command
        if "goodbye" in command or "go to sleep" in command:
            speak("Goodbye!")
            break

        # 2. Next, check for any other recognized command
        found_command = False
        for trigger in commands.keys():
            if trigger in command:
                print(f"DEBUG: Match found for trigger '{trigger}'.")
                if trigger in ["open", "set volume to", "set a timer for", "calculate", "find", "search pdf"]:
                    commands[trigger](command)
                else:
                    commands[trigger]()
                found_command = True
                break
        
        if not found_command:
            # This part is now skipped if a command isn't recognized,
            # allowing the loop to just continue listening silently.
            print(f"DEBUG: Command '{command}' not recognized.")
if __name__ == "__main__":
    main()