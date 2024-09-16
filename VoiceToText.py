# Copyright © 2024 Chance Currie
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# as this was made for educational purposes and simply out of
# curiosity as OpenAI and Azure are both fascinating. Please see the
# GNU General Public License for more details, or view
# <https://www.gnu.org/licenses/> for more information.


# A Python program that connects to OpenAI's and Azure's API. 
# This program was run on a Windows machine in a Python 3.12 environment and utilizes ChatGPT 4o Mini and Azure Speech To Text. 

# Reference this link as needed in order to understand further how to do this: https://medium.com/@woyera/your-first-steps-in-ai-using-openais-gpt-4o-mini-with-python-e03e8d47aef7
# Second resource: https://www.linkedin.com/pulse/how-use-chatgpt-api-python-tutorialspoint-byl1c/
# This link was referenced in order to make a continuous loop of prompts and answers: https://stackoverflow.com/questions/77505030/openai-api-error-you-tried-to-access-openai-chatcompletion-but-this-is-no-lon
# Original idea for this inspired by DougDoug, a content creator on YouTube. This is basically a dumbed down version of it. Their GitHub can be found here: https://github.com/DougDougGithub/Babagaboosh/tree/main

# Importing the OpenAI API
from openai import OpenAI
# Importing the os library
import os 
import time
# Importing the Azure API
import azure.cognitiveservices.speech as speechsdk

# Declaring the OpenAI key through calling the environment variable that we created back in Step 3 to keep the key a secret.
api_key = os.getenv('OPENAI_API_KEY')

# Validating OpenAI API key
if not api_key:
    exit("OpenAI API key is missing. Please set it in your environment variables.")

# Initializing the OpenAI client
client = OpenAI(api_key=api_key)

# A function that will generate a response based on what the user inputs
def chat_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content" : prompt}]
    )

    return response.choices[0].message.content.strip()

# The Azure Speech-To-Text manager
class SpeechToTextManager:
    azure_speechconfig = None
    azure_audioconfig = None
    azure_speechrecognizer = None

    def __init__(self):
        # Setting up the Azure Speech Configs
        try:
            self.azure_speechconfig = speechsdk.SpeechConfig(subscription=os.getenv('AZURE_TTS_KEY'), region=os.getenv('AZURE_TTS_REGION'))
        except TypeError:
            exit("Azure keys are missing! Please set AZURE_TTS_KEY and AZURE_TTS_REGION as environment variables!")

        if not self.azure_speechconfig:
            exit("Azure Speech SDK configuration failed.")

        self.azure_speechconfig.speech_recognition_language = "en-US"

    # Function to capture speech and convert it to text
    def speechtotext_from_mic(self):
        self.azure_audioconfig = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.azure_speechrecognizer = speechsdk.SpeechRecognizer(speech_config=self.azure_speechconfig, audio_config=self.azure_audioconfig)

        # Prompt to speak into your default microphone to get input capture
        print("Speak into your microphone...")
        speech_recognition_result = self.azure_speechrecognizer.recognize_once_async().get()

        # If the speech is recognized, it will translate it into text
        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
            return speech_recognition_result.text
        # Else If the speech is not recognized, it throws an error message
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        # Else if the speech is cancelled for any reason, it will throw a cancellation message along with an error message if needed
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            print("Speech Recognition canceled: {}".format(speech_recognition_result.cancellation_details.reason))
            if speech_recognition_result.cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(speech_recognition_result.cancellation_details.error_details))

        return None

# A loop that will continue to run until user enters in a keyword that ends the program
# Until the program is stopped, the user can speak as many prompts as they want to
if __name__ == "__main__":

    speech_manager = SpeechToTextManager()

    while True:
        # While the program is running, it will continue to capture speech input and convert it to text
        speech_text = speech_manager.speechtotext_from_mic()

        if speech_text:
            print(f"\nUser: {speech_text}")

            # Send the speech that was captured over to ChatGPT as text
            chat_response = chat_gpt(speech_text)
            print(f"Bot: {chat_response}")
        else:
            print("No valid speech input detected. Please try again.")

        user_exit = input("\nType 'quit' to exit or press Enter to continue: ").strip().lower()
        if user_exit == 'quit':
            break