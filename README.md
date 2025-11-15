Voice-Command-Project: A Personal Desktop Voice Assistant 

Author: Alaa Alameri

Project Overview

The Voice-Command-Project is a desktop application that receives and executes voice commands, aiming to function similarly to personal assistants like Apple's Siri. Built primarily with Python, this assistant provides hands-free control by listening for a user's verbal input, processing it, and performing specific actions, such as launching local applications or navigating to websites.

Key Features

    Voice Recognition: Captures and converts spoken language into text commands using the microphone.

    Intelligent Command Execution: Analyzes the recognized text to determine the required action.

    Local Application Launch: Ability to launch installed desktop applications like WhatsApp and Notepad (المفكرة).

    Web Navigation: If a specified application is not found locally, the assistant defaults to opening its official website (e.g., Facebook or WhatsApp Web) in the default web browser.

    Basic System Interaction: Utilizes libraries like pyautogui for simple graphical user interface automation and system interaction.

    Multithreading: Uses threading and queue for managing concurrent tasks, ensuring a responsive user experience.

    GUI Support (Tkinter): The inclusion of tkinter suggests the project includes a basic graphical interface for interaction.

Technology Stack

The project leverages the power of Python and several specialized libraries for speech processing and system control:
Component	Technology/Library	Purpose
Main Language	Python	The core programming language.
Speech-to-Text	speech_recognition (sr)	Converts spoken words captured from the microphone into text.
Text-to-Speech	pyttsx3	Handles the assistant's voice output (speaking responses to the user).
System Control	os, subprocess, winreg	Used for interacting with the operating system, running programs, and accessing the Windows registry (to find local applications).
Web Interaction	webbrowser	Opens specified URLs and websites in the user's default browser.
GUI	tkinter	Used for creating the assistant's basic graphical user interface (GUI).
Automation	pyautogui	Programmatically controls the mouse and keyboard, useful for automation.
Concurrency	threading, queue, time, Lock	Manages concurrent operations, ensuring the application remains responsive while listening or processing commands.
Data Handling	json	Used for managing configuration or data related to commands.
Date/Time	datetime	Used for commands related to time or date.

Installation & Setup

Follow these steps to set up and run the voice assistant on your local machine.

Prerequisites

    Python: Ensure you have a stable version of Python installed (Python 3.x is recommended).

    Microphone: A functional microphone is required for voice recognition.

Steps

    Clone the Repository:
    Bash

git clone <repository_url>
cd voice-command-project

(Replace <repository_url> with the actual URL of your repository.)

Install Dependencies: The project relies on the following Python packages. You can install them all using pip.

    Note: Depending on your environment, you may need to install system dependencies for libraries like pyaudio (often required by SpeechRecognition).

Bash

# It is highly recommended to use a virtual environment
# python -m venv venv
# source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate   # Windows

pip install SpeechRecognition pyttsx3 pyautogui webbrowser tkinter
# You might also need: pip install pyaudio

    (If you have a requirements.txt file, use pip install -r requirements.txt instead).

Run the Application: Navigate to the project directory and run the main Python file.
Bash

    python <main_file_name>.py

    (Replace <main_file_name>.py with the actual entry point file, e.g., main.py or assistant.py).

Usage

    Launch: Run the application as described in the setup steps.

    Listen: The application will start listening for your voice commands.

    Execute: State a command to the assistant. Examples of commands it can handle:

        "Open WhatsApp" (will launch the local app or its web version).

        "Open Facebook" (will open the official website in the browser).

        "Open Notepad" (will launch the local application).
