# Python Voice-Controlled Desktop Assistant

A versatile desktop personal assistant built with Python that streamlines daily workflows by performing a variety of tasks through voice commands. This project leverages speech recognition and system automation to provide hands-free control over your computer.



## Key Features

* **Daily Briefing:** Get a morning update with the current date and a real-time weather forecast for your city using the OpenWeatherMap API.
* **System Control:**
    * **Shutdown:** Safely shuts down the computer with a voice confirmation.
    * **Volume:** Adjusts or mutes the system's master volume.
    * **Applications:** Opens any installed application on the device.
* **Media Player Control:** Manages media playback with commands for play, pause, next track, and previous track.
* **Productivity Tools:**
    * **Timer & Alarm:** Sets a timer for a specified duration.
    * **Calculator:** Performs basic arithmetic calculations from spoken commands.
    * **Screen Reader:** Uses OCR to read the text currently visible on the screen.
* **File System Management:**
    * **File Search:** Locates files with a specific extension within a given directory.
    * **PDF Search:** Scans a PDF document to find and report all pages containing a specific word.

## Technologies Used

* **Language:** Python 3
* **Core Libraries:**
    * **`speech_recognition`**: For converting voice commands into text.
    * **`gTTS` / `playsound`**: For text-to-speech (TTS) synthesis.
    * **`psutil`**: For checking system status like CPU and battery.
    * **`pyautogui`**: For controlling media keys and taking screenshots for OCR.
    * **`PyMuPDF`**: For interacting with and searching within PDF files.
    * **`pytesseract`**: For Optical Character Recognition (OCR) to read the screen.
    * **`requests`**: For making HTTP requests to external APIs (OpenWeatherMap).
    * **`pycaw`**: For audio control on Windows.

## Setup and Installation

Follow these steps to get the assistant running on your local machine.

### 1. Prerequisites
* Python 3.8 or newer.
* The Tesseract-OCR engine must be installed on your system. You can find installers on the [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract).

### 2. Clone the Repository
Clone this repository to your local machine:
```bash
git clone [https://github.com/YourUsername/Your-Repository-Name.git](https://github.com/YourUsername/Your-Repository-Name.git)
cd Your-Repository-Name

pip install -r requirements.txt

# --- Paste your OpenWeatherMap API key here ---
API_KEY = "YOUR_WEATHER_API_KEY"

python assistant.py
```

"What time is it?"

"Give me my daily briefing."

"Open Chrome."

"Set a timer for 5 minutes."

"Calculate 15 times 4."

To stop the assistant, say "goodbye" or "go to sleep," or press Ctrl+C in the terminal.
