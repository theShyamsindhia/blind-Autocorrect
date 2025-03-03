lobeomoibs from pynput import keyboard
import time
from pynput.keyboard import Controller
import requests
from fuzzywuzzy import fuzz

# Initialize the keyboard controller for typing corrected text
keyboard_controller = Controller()

# Global variables
buffer = []
last_keypress_time = time.time()

# Function to calculate similarity between two words
def is_similar(rough_input, corrected_word, threshold=70):
    similarity = fuzz.ratio(rough_input.lower(), corrected_word.lower())
    return similarity >= threshold

# Function to send input to Ollama for autocorrection
def autocorrect_ollama(rough_input):
    url = "http://localhost:11434/v1/chat/completions"  # Correct API endpoint for Ollama
    
    # Message to pass to the Ollama model
    payload = {
        "model": "mistral:latest",  # Use the model available in Ollama
        "messages": [
            {"role": "system", "content": "You are a strict spelling corrector. Correct the spelling of this word, return only the corrected word. Do not provide explanations, and do not interpret or add any other context."},
            {"role": "user", "content": rough_input}
        ],
        "temperature": 0.1  # Very low temperature for more deterministic corrections
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        # Send request to Ollama
        print(f"Sending to Ollama: {rough_input}")  # Log what is being sent
        response = requests.post(url, json=payload, headers=headers, timeout=10)  # Set a timeout to avoid hanging
        
        # Check if the response status is OK
        if response.status_code == 200:
            result = response.json()
            # Extract the corrected word
            corrected_word = result['choices'][0]['message']['content'].strip()
            print(f"Ollama Response: {corrected_word}")  # Log Ollama's response
            
            # Post-process: Only take the first word and strip non-alphabetic characters
            corrected_word = corrected_word.split()[0].strip()  # Keep only the first word
            corrected_word = ''.join(filter(str.isalpha, corrected_word))  # Remove any non-alphabetic characters
            
            # Return corrected word only if it's similar enough to the rough input
            if is_similar(rough_input, corrected_word):
                return corrected_word
            else:
                return rough_input  # If not similar enough, return the original input
        else:
            print(f"Ollama error: {response.status_code}, {response.text}")
            return rough_input  # Return the original input if there's an error

    except requests.exceptions.RequestException as e:
        # Log detailed connection errors
        print(f"Error connecting to Ollama: {e}")
        return rough_input  # Return rough input if there's a connection error

# Function to process buffer and autocorrect
def process_buffer():
    global buffer
    rough_input = ''.join(buffer).strip()  # Join buffer to create rough input
    
    # If there's no input, don't process
    if not rough_input:
        return
    
    # Call Ollama to correct the word
    corrected_word = autocorrect_ollama(rough_input)
    
    # Clear the wrongly typed word by simulating backspace presses
    for _ in range(len(rough_input)):
        keyboard_controller.press(keyboard.Key.backspace)
        keyboard_controller.release(keyboard.Key.backspace)
    
    # Type the corrected word followed by a space
    keyboard_controller.type(corrected_word)
    keyboard_controller.type(' ')  # Add a space after the word
    
    # Reset the buffer for the next word
    buffer.clear()

# Function to capture key presses
def on_press(key):
    global buffer, last_keypress_time
    try:
        # Only capture alphanumeric characters and store them in the buffer
        if key.char.isalnum():
            buffer.append(key.char)
        elif key == keyboard.Key.space:
            # When the space is pressed, process the word in the buffer
            process_buffer()
    except AttributeError:
        pass

    current_time = time.time()
    if current_time - last_keypress_time > 0.9 :
        # Process the buffer after inactivity
        process_buffer()  
    last_keypress_time = current_time

# Stop the listener on 'Esc' press
def on_release(key):
    if key == keyboard.Key.esc:
        return False

# Main function to run the listener
def main():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Start the service
if __name__ == "__main__":
    main()

