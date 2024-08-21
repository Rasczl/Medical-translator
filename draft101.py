import cv2
from pyzbar.pyzbar import decode
import speech_recognition as sr
from openai import OpenAI
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def decode_barcode(frame):
    # Decode barcodes
    decoded_objects = decode(frame)

    # Print data points
    for obj in decoded_objects:
        print("Type:", obj.type)
        print("Data:", obj.data.decode('utf-8'))
        patient=obj.data.decode('utf-8')
    language= patient[2]
    return language, patient

def recognize_speech():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print(" ")
        audio = r.listen(source, timeout=5)  # Listen for input with a timeout of 5 seconds
        try:
            # Use Google Speech Recognition
            text = r.recognize_google(audio)  
            print("You said: {}".format(text))
            return text

        except sr.UnknownValueError:
            print("I'm sorry, I didn't catch that")
        except sr.RequestError as e:
            print("Cannot fetch results from Google API".format(e))
    return None  # Return None if no speech is detected within the timeout

def translate_text(language, text):
    if text is None:
        return "No information available"
    
    # Your OpenAI API key
    # Use your own API key down below
    client = OpenAI(api_key="")
    # Create a new session
    session = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": "you are a translator, you will receive a language and text pair in the form of 'language:text' return the text translated into the preferred language. return only the translated text"
        },
        {
            "role": "user",
            "content": f"{language}:{text}"
        }]
    )
    response = session.choices[0].message.content
    print(response)
    return response

def on_button_click():
    global barcode_scanned
    if not barcode_scanned:
        result_label.config(text="No information available")
        return
    text = recognize_speech()
    # Assuming language and patient_info are obtained from the barcode scanning
    language, patient_info = "English", ["Julio Marco", "50", "Spanish", "Sulfate", "Tomatoes"]
    translation = translate_text(language, text)
    result_label.config(text=f"Translated text: {translation}")

def capture_and_decode():
    global barcode_scanned
    barcode_scanned = True
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        # Decode barcode
        language, patient_info = decode_barcode(frame)

        if language is not None:  # If barcode is detected
            break  # Exit loop

        # Display the frame
        cv2.imshow('Barcode Scanner', frame)

        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Create a Tkinter window
window = tk.Tk()
window.title("Medical Translator")
window.configure(bg="#ADD8E6")  # Set background color to light blue

# Create a frame for buttons
button_frame = ttk.Frame(window, padding="20")
button_frame.pack(pady=20)

# Create a button to trigger speech recognition and translation
button_speech_recognition = ttk.Button(button_frame, text="Start Speech Recognition", command=on_button_click, style="Custom.TButton")
button_speech_recognition.pack(side="left", padx=10)

# Create a button to trigger camera and barcode scanning
button_barcode_scanning = ttk.Button(button_frame, text="Start Barcode Scanning", command=capture_and_decode, style="Custom.TButton")
button_barcode_scanning.pack(side="left", padx=10)

# Define custom button style
window.style = ttk.Style()
window.style.configure("Custom.TButton", font=("Arial", 24), background="#007bff", foreground="black", padding=10)

# Create a frame for result display
result_frame = ttk.Frame(window)
result_frame.pack(pady=10)

# Create a label to display the translated text
result_label = ttk.Label(result_frame, text="", font=("Arial", 24), wraplength=400, foreground="black")
result_label.pack()

# Initialize variable to track if barcode has been scanned
barcode_scanned = False

# Start the Tkinter event loop
window.mainloop()
