import cv2
import mediapipe as mp
import pyautogui
import speech_recognition as sr
import pyttsx3
import time

# Initialize hand tracking and voice assistant
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize voice assistant
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Screen size
screen_width, screen_height = pyautogui.size()

# Start capturing video
cap = cv2.VideoCapture(0)

gesture_active = True


def speak(text):
    engine.say(text)
    engine.runAndWait()


def listen_command():
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            return command.lower()
        except sr.UnknownValueError:
            return ""


speak("Proton is ready. Say 'start recognition' to begin or 'exit' to close.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if gesture_active and results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark

            index_finger_tip = landmarks[8]
            thumb_tip = landmarks[4]
            middle_finger_tip = landmarks[12]

            x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            screen_x, screen_y = int(index_finger_tip.x * screen_width), int(index_finger_tip.y * screen_height)

            cv2.circle(frame, (x, y), 10, (255, 0, 0), -1)
            pyautogui.moveTo(screen_x, screen_y)

            # Gesture logic
            if abs(x - thumb_tip.x * w) < 30 and abs(y - thumb_tip.y * h) < 30:
                pyautogui.click()
                cv2.putText(frame, 'Left Click', (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if abs(x - middle_finger_tip.x * w) < 30 and abs(y - middle_finger_tip.y * h) < 30:
                pyautogui.rightClick()
                cv2.putText(frame, 'Right Click', (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if abs(x - thumb_tip.x * w) < 30 and abs(y - thumb_tip.y * h) < 30 and abs(
                    x - middle_finger_tip.x * w) < 30:
                pyautogui.doubleClick()
                cv2.putText(frame, 'Double Click', (x, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Show the frame
    cv2.imshow("AI Virtual Mouse", frame)

    # Listen for voice commands
    if cv2.waitKey(1) & 0xFF == ord('v'):
        command = listen_command()
        if 'start recognition' in command:
            gesture_active = True
            speak("Gesture recognition activated.")
        elif 'stop recognition' in command:
            gesture_active = False
            speak("Gesture recognition deactivated.")
        elif 'exit' in command:
            speak("Goodbye!")
            break
        elif 'google search' in command:
            speak("What do you want to search?")
            query = listen_command()
            pyautogui.hotkey('ctrl', 't')
            pyautogui.write(f'https://www.google.com/search?q={query}')
            pyautogui.press('enter')

    # Break on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

speak("Proton is shutting down.")