import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyttsx3
import threading
import webbrowser
import subprocess
import datetime
import platform


class VoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Accessible Voice Assistant")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        # -----------------------------
        # Voice engine
        # -----------------------------
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 155)
        self.engine.setProperty("volume", 1.0)

        voices = self.engine.getProperty("voices")
        if voices:
            self.engine.setProperty("voice", voices[0].id)

        self.recognizer = sr.Recognizer()

        self.listening = False

        # -----------------------------
        # Accessibility settings
        # -----------------------------
        self.bg_color = "#111111"
        self.fg_color = "#FFFFFF"
        self.button_color = "#333333"

        self.root.configure(bg=self.bg_color)

        self.create_interface()

        # Keyboard shortcuts
        self.root.bind("<space>", self.keyboard_listen)
        self.root.bind("<Return>", self.keyboard_listen)
        self.root.bind("<Escape>", self.stop_assistant)

    # =========================================================
    # GUI
    # =========================================================

    def create_interface(self):

        title = tk.Label(
            self.root,
            text="Accessible Voice Assistant",
            font=("Arial", 28, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        title.pack(pady=20)

        instruction = tk.Label(
            self.root,
            text="Press SPACE or click LISTEN to give a voice command",
            font=("Arial", 16),
            bg=self.bg_color,
            fg=self.fg_color
        )
        instruction.pack(pady=5)

        # -----------------------------
        # Status
        # -----------------------------

        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg="#00FF00"
        )
        self.status_label.pack(pady=10)

        # -----------------------------
        # Conversation area
        # -----------------------------

        self.conversation = scrolledtext.ScrolledText(
            self.root,
            width=70,
            height=15,
            font=("Arial", 16),
            bg="#222222",
            fg="white",
            insertbackground="white",
            wrap=tk.WORD
        )

        self.conversation.pack(
            padx=30,
            pady=15,
            fill=tk.BOTH,
            expand=True
        )

        self.conversation.config(state=tk.DISABLED)

        # -----------------------------
        # Listen button
        # -----------------------------

        self.listen_button = tk.Button(
            self.root,
            text="🎤  LISTEN",
            command=self.start_listening,
            font=("Arial", 24, "bold"),
            bg=self.button_color,
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=4
        )

        self.listen_button.pack(pady=10)

        # -----------------------------
        # Stop button
        # -----------------------------

        stop_button = tk.Button(
            self.root,
            text="STOP",
            command=self.stop_assistant,
            font=("Arial", 18, "bold"),
            bg="#550000",
            fg="white",
            width=12,
            height=1
        )

        stop_button.pack(pady=10)

        # -----------------------------
        # Text input
        # -----------------------------

        input_frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )
        input_frame.pack(fill=tk.X, padx=30, pady=15)

        self.text_entry = tk.Entry(
            input_frame,
            font=("Arial", 18),
            bg="white",
            fg="black"
        )

        self.text_entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            ipady=10
        )

        send_button = tk.Button(
            input_frame,
            text="SEND",
            command=self.send_text,
            font=("Arial", 16, "bold"),
            bg=self.button_color,
            fg="white",
            width=8
        )

        send_button.pack(side=tk.RIGHT, padx=(10, 0))

    # =========================================================
    # Conversation
    # =========================================================

    def add_message(self, speaker, message):

        self.conversation.config(state=tk.NORMAL)

        self.conversation.insert(
            tk.END,
            f"{speaker}: {message}\n\n"
        )

        self.conversation.see(tk.END)

        self.conversation.config(state=tk.DISABLED)

    # =========================================================
    # Text-to-Speech
    # =========================================================

    def speak(self, text):

        self.add_message("Assistant", text)

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)

    # =========================================================
    # Speech recognition
    # =========================================================

    def start_listening(self):

        if self.listening:
            return

        self.listening = True

        self.status_label.config(
            text="Listening...",
            fg="#FFFF00"
        )

        self.listen_button.config(
            state=tk.DISABLED
        )

        thread = threading.Thread(
            target=self.listen,
            daemon=True
        )

        thread.start()

    def listen(self):

        try:

            with sr.Microphone() as source:

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=8
                )

            self.root.after(
                0,
                lambda: self.status_label.config(
                    text="Processing...",
                    fg="#00FFFF"
                )
            )

            try:

                command = self.recognizer.recognize_google(
                    audio
                )

                self.root.after(
                    0,
                    lambda: self.process_command(command)
                )

            except sr.UnknownValueError:

                self.root.after(
                    0,
                    lambda: self.speak(
                        "Sorry, I could not understand you."
                    )
                )

            except sr.RequestError:

                self.root.after(
                    0,
                    lambda: self.speak(
                        "Speech recognition is currently unavailable."
                    )
                )

        except sr.WaitTimeoutError:

            self.root.after(
                0,
                lambda: self.speak(
                    "I did not hear a command."
                )
            )

        except Exception as e:

            print("Microphone error:", e)

            self.root.after(
                0,
                lambda: self.speak(
                    "There was a problem with the microphone."
                )
            )

        finally:

            self.listening = False

            self.root.after(
                0,
                lambda: self.status_label.config(
                    text="Ready",
                    fg="#00FF00"
                )
            )

            self.root.after(
                0,
                lambda: self.listen_button.config(
                    state=tk.NORMAL
                )
            )

    # =========================================================
    # Text command
    # =========================================================

    def send_text(self):

        command = self.text_entry.get().strip()

        if command:

            self.text_entry.delete(
                0,
                tk.END
            )

            self.process_command(command)

    # =========================================================
    # Command processor
    # =========================================================

    def process_command(self, command):

        command = command.lower().strip()

        self.add_message(
            "You",
            command
        )

        # -----------------------------
        # Greeting
        # -----------------------------

        if any(word in command for word in [
            "hello",
            "hi",
            "hey"
        ]):

            self.speak(
                "Hello. How can I help you?"
            )

        # -----------------------------
        # Time
        # -----------------------------

        elif "time" in command:

            current_time = datetime.datetime.now().strftime(
                "%I:%M %p"
            )

            self.speak(
                f"The current time is {current_time}"
            )

        # -----------------------------
        # Date
        # -----------------------------

        elif "date" in command or "today" in command:

            today = datetime.datetime.now().strftime(
                "%A, %d %B %Y"
            )

            self.speak(
                f"Today is {today}"
            )

        # -----------------------------
        # Google
        # -----------------------------

        elif "open google" in command:

            self.speak("Opening Google.")

            webbrowser.open(
                "https://www.google.com"
            )

        # -----------------------------
        # YouTube
        # -----------------------------

        elif "open youtube" in command:

            self.speak("Opening YouTube.")

            webbrowser.open(
                "https://www.youtube.com"
            )

        # -----------------------------
        # Search Google
        # -----------------------------

        elif command.startswith("search"):

            query = command.replace(
                "search",
                "",
                1
            ).strip()

            if query:

                self.speak(
                    f"Searching for {query}"
                )

                webbrowser.open(
                    "https://www.google.com/search?q="
                    + query.replace(" ", "+")
                )

            else:

                self.speak(
                    "What would you like me to search for?"
                )

        # -----------------------------
        # Open calculator
        # -----------------------------

        elif "open calculator" in command:

            self.speak(
                "Opening calculator."
            )

            if platform.system() == "Windows":

                subprocess.Popen(
                    "calc.exe"
                )

            elif platform.system() == "Darwin":

                subprocess.Popen(
                    ["open", "-a", "Calculator"]
                )

            else:

                subprocess.Popen(
                    ["gnome-calculator"]
                )

        # -----------------------------
        # Open notepad
        # -----------------------------

        elif "open notepad" in command:

            self.speak(
                "Opening notepad."
            )

            if platform.system() == "Windows":

                subprocess.Popen(
                    "notepad.exe"
                )

            elif platform.system() == "Darwin":

                subprocess.Popen(
                    ["open", "-a", "TextEdit"]
                )

            else:

                subprocess.Popen(
                    ["gedit"]
                )

        # -----------------------------
        # Stop speaking
        # -----------------------------

        elif "stop" in command:

            self.stop_speech()

        # -----------------------------
        # Help
        # -----------------------------

        elif "help" in command or "what can you do" in command:

            self.speak(
                "You can ask me for the time, "
                "today's date, open Google, "
                "open YouTube, search the internet, "
                "open calculator, or open notepad."
            )

        # -----------------------------
        # Exit
        # -----------------------------

        elif any(word in command for word in [
            "exit",
            "quit",
            "close assistant"
        ]):

            self.speak(
                "Goodbye."
            )

            self.root.after(
                1000,
                self.root.destroy
            )

        # -----------------------------
        # Unknown command
        # -----------------------------

        else:

            self.speak(
                "I don't know that command yet. "
                "Say help to hear what I can do."
            )

    # =========================================================
    # Keyboard accessibility
    # =========================================================

    def keyboard_listen(self, event=None):

        self.start_listening()

    # =========================================================
    # Stop speech
    # =========================================================

    def stop_speech(self):

        try:
            self.engine.stop()
        except:
            pass

        self.status_label.config(
            text="Speech stopped",
            fg="#FFAA00"
        )

    # =========================================================
    # Stop assistant
    # =========================================================

    def stop_assistant(self, event=None):

        self.stop_speech()

        self.listening = False

        self.status_label.config(
            text="Ready",
            fg="#00FF00"
        )


# =============================================================
# Run application
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = VoiceAssistant(root)

    root.mainloop()