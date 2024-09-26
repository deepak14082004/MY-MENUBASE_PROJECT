from flask import Flask, request,send_file,Response,jsonify, render_template
import pythoncom
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from twilio.rest import Client
from email.mime.text import MIMEText
from email import encoders
from flask_socketio import SocketIO, emit
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import smtplib
from email.mime.text import MIMEText
from serpapi import GoogleSearch
from flask_cors import CORS
import requests
from gtts import gTTS
from plivo import RestClient
import subprocess
from instagrapi import Client
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import logging
import io
import threading
import os
from instabot import Bot
import cv2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import logging
import wave
import io
import cv2
import subprocess
from twilio.rest import Client
import speech_recognition as sr

app = Flask(__name__)  # Corrected __name__

# होम पेज
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/intro.html')
def intro_form():
    return render_template('intro.html')

# 'Send Email' फॉर्म पेज
@app.route('/send_email.html')
def send_email_form():
    return render_template('send_email.html')


# फॉर्म सबमिशन हैंडलर
@app.route('/send-email', methods=['POST'])
def send_email():
    to_email = request.form['to_email']
    subject = request.form['subject']
    message_body = request.form['message']

    
    try:
        
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = 'deepakkharodia50@gmail.com'  
        sender_password = 'vfwykgxhmllovrfe'  

        msg = MIMEText(message_body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return 'Email sent successfully!'
    except Exception as e:
        return f'Failed to send email: {str(e)}'


@app.route('/send_message.html')
def send_message_form():
    return render_template('send_message.html')

ACCOUNT_SID = 'AC0d085c9c6fa060904d204c998ca2ebcb'
AUTH_TOKEN = '8050cee8f611077a58e1e48e8fd6c000'
TWILIO_PHONE_NUMBER = '+18777804236'  # Your Twilio phone number

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# POST route to send SMS
@app.route('/send-sms', methods=['POST'])
def send_sms():
    try:
        # Get JSON data from the request
        data = request.get_json()
        to_phone_number = data.get('to_phone_number')
        message_body = data.get('message_body')

        if not to_phone_number or not message_body:
            return jsonify({"error": "Both 'to_phone_number' and 'message_body' are required"}), 400

        # Send the SMS message
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )

        return jsonify({"message": "SMS sent successfully", "sid": message.sid}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def control_volume(target_volume=None, mute=None):
    pythoncom.CoInitialize()

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    if mute is not None:
        volume.SetMute(mute, None)
        return {"message": "Volume muted" if mute else "Volume unmuted"}

    if target_volume is not None:
        volume.SetMasterVolumeLevel(target_volume, None)
        return {"message": f"Volume set to {target_volume}"}

    current_volume = volume.GetMasterVolumeLevel()
    return {"current_volume": current_volume}

@app.route('/volume_control.html')
def volume_control_form():
    return render_template('volume_control.html')

def control_volume():
    # Initialize COM (fixes the CoInitialize issue)
    pythoncom.CoInitialize()

    # Get the default audio device interface
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Get the current volume level (range: -65.25 to 0.0)
    current_volume = volume.GetMasterVolumeLevel()
    print(f"Current volume level: {current_volume}")

    # Set volume to a specific level (-65.25 min, 0.0 max)
    target_volume = -10.0  # Adjust as needed (-65.25 to 0.0)
    volume.SetMasterVolumeLevel(target_volume, None)

    # You can also mute or unmute the audio
    volume.SetMute(0, None)  # 0 to unmute, 1 to mute

# Call the function to control volume
control_volume()

def control_volume(target_volume=None, mute=None):
    pythoncom.CoInitialize()

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    if mute is not None:
        volume.SetMute(mute, None)
        return {"message": "Volume muted" if mute else "Volume unmuted"}

    if target_volume is not None:
        volume.SetMasterVolumeLevel(target_volume, None)
        return {"message": f"Volume set to {target_volume}"}

    current_volume = volume.GetMasterVolumeLevel()
    return {"current_volume": current_volume}

@app.route('/volume', methods=['GET', 'POST'])
def volume():
    if request.method == 'GET':
        return jsonify(control_volume())

    if request.method == 'POST':
        data = request.get_json()
        target_volume = float(data.get('target_volume'))
        return jsonify(control_volume(target_volume=target_volume))

@app.route('/mute', methods=['POST'])
def mute():
    data = request.get_json()
    mute = int(data.get('mute'))
    return jsonify(control_volume(mute=mute))

@app.route('/text_to_audio.html')
def text_to_audio_form():
    return render_template('text_to_audio.html')

@app.route('/text-to-audio', methods=['POST'])
def text_to_audio():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    try:
        # Convert text to speech
        tts = gTTS(text=text, lang='en')
        audio_file = 'output.mp3'
        tts.save(audio_file)

        # Return the audio file
        return send_file(audio_file, mimetype='audio/mpeg', as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send_whatsapp_message.html')
def send_whatsapp_message_form():
    return render_template('send_whatsapp_message.html')





@app.route('/launch_vlc.html')
def launch_vlc_form():
    return render_template('launch_vlc.html')

file_path = "C:\\Users\\deepa\\OneDrive\\Desktop\\MENUBASE\\Tu Jo Mileya _ Official Video _ Juss x MixSingh _ New Punjabi Song 2024 _ Latest Punjabi Songs 2024.mp4"

print(os.path.isfile(file_path))  # Should print True if the file exists

@app.route('/launch-vlc', methods=['POST'])
def launch_vlc():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        media_file = data.get('media_file', '')

        if not media_file:
            return jsonify({"error": "No media file provided"}), 400

        # Print the received path for debugging
        print(f"Received media file path: {media_file}")

        # Normalize the path (remove extra spaces and convert to absolute path)
        media_file = os.path.abspath(media_file).strip()

        # Check if the media file path is valid
        if not os.path.isfile(media_file):
            return jsonify({"error": f"Media file does not exist: {media_file}"}), 400

        # Provide the full path to the VLC executable if not in PATH
        vlc_path = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\VideoLAN\\VLC media player.lnk"  # Update this path if VLC is in a different location
        vlc_command = [vlc_path, media_file]

        # Launch VLC with the media file
        subprocess.Popen(vlc_command)  # Launch VLC in the background

        return jsonify({"message": "VLC launched successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/upload_ig_pic.html')  # Ensure that the URL starts with a '/'
def upload_ig_pic_form():
    return render_template('upload_ig_pic.html')  # Assuming you have this HTML template

# Constants for Instagram Graph API
INSTAGRAM_GRAPH_API_URL = "https://graph.facebook.com/v15.0"
INSTAGRAM_USER_ID = 'your_instagram_user_id'  # Instagram user ID (business/creator account)
ACCESS_TOKEN = 'your_facebook_access_token'  # Your access token from Facebook Graph API

# Route to handle Instagram photo upload
@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    data = request.get_json()

    image_url = data.get('image_url')  # Image URL that you want to upload
    caption = data.get('caption')  # Caption for the post

    # Step 1: Upload the image to Instagram as a container
    container_url = f"{INSTAGRAM_GRAPH_API_URL}/{INSTAGRAM_USER_ID}/media"
    container_payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': ACCESS_TOKEN
    }

    container_response = requests.post(container_url, data=container_payload)
    container_result = container_response.json()

    if 'id' in container_result:
        # Step 2: Publish the container to Instagram feed
        publish_url = f"{INSTAGRAM_GRAPH_API_URL}/{INSTAGRAM_USER_ID}/media_publish"
        publish_payload = {
            'creation_id': container_result['id'],
            'access_token': ACCESS_TOKEN
        }

        publish_response = requests.post(publish_url, data=publish_payload)
        publish_result = publish_response.json()

        if 'id' in publish_result:
            return jsonify({
                'status': 'success',
                'message': 'Photo uploaded successfully!',
                'post_id': publish_result['id']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to publish the photo.',
                'error': publish_result
            }), 400
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to create the container.',
            'error': container_result
        }), 400



@app.route('/make_call.html')  # Ensure that the URL starts with a '/'
def make_call_form():
    return render_template('make_call.html')

TWILIO_ACCOUNT_SID = 'AC0d085c9c6fa060904d204c998ca2ebcb'
TWILIO_AUTH_TOKEN = '4a0122fc759d73e9d192b55ce95e5cf0'
TWILIO_PHONE_NUMBER = '+17472200058'

# Initialize the Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/make_call', methods=['POST'])
def make_call():
    # Get the recipient's phone number from the request
    data = request.get_json()
    to_phone_number = data.get('to')

    if not to_phone_number:
        return jsonify({'error': 'Phone number is required'}), 400

    try:
        call = client.calls.create(
            to=to_phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url='http://demo.twilio.com/docs/voice.xml'  # URL of TwiML instructions
        )
        return jsonify({'message': 'Call initiated', 'call_sid': call.sid}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/audio_to_text.html')
def audio_to_text_form():
    return render_template('audio_to_text.html')

@app.route('/process_speech', methods=['POST'])
def process_speech():
    data = request.get_json()
    text = data.get('text', '')
    
    # Process the text (e.g., save it to a database, analyze it, etc.)
    print(f"Received text: {text}")

    return jsonify({"status": "success", "message": "Text received."})


@app.route('/schedule_email.html')
def schedule_email_form():
    return render_template('schedule_email.html')

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change if using another email service
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'deepakkharodia50@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'vfwykgxhmllovrfe'    # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'deepakkharodia50@gmail.com'  # Replace with your email

mail = Mail(app)
scheduler = BackgroundScheduler()

def send_email(subject, recipient, body):
    with app.app_context():
        msg = Message(subject=subject, recipients=[recipient])
        msg.body = body
        mail.send(msg)
        print(f"Email sent to {recipient} with subject '{subject}'")

@app.route('/schedule_email', methods=['POST'])
def schedule_email():
    data = request.get_json()
    subject = data.get('subject')
    recipient = data.get('recipient')
    body = data.get('body')
    send_time = data.get('send_time')  # Expected format: 'YYYY-MM-DD HH:MM:SS'

    # Convert send_time to a datetime object
    scheduled_time = datetime.strptime(send_time, '%Y-%m-%d %H:%M:%S')

    # Calculate delay in seconds
    delay = (scheduled_time - datetime.now()).total_seconds()

    if delay < 0:
        return jsonify({"status": "error", "message": "Scheduled time must be in the future."}), 400

    # Schedule the email
    scheduler.add_job(send_email, 'date', run_date=scheduled_time, args=[subject, recipient, body])
    scheduler.start()

    return jsonify({"status": "success", "message": "Email scheduled successfully."}), 200


@app.route('/click_photo.html')
def click_photo_form():
    return render_template('click_photo.html')

camera = cv2.VideoCapture(0)

# Function to capture frames from the camera
def generate_frames():
    while True:
        success, frame = camera.read()  # Read frame from the camera
        if not success:
            break
        else:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame in the response with correct MIME type
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to stream the video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to capture a photo and save it
@app.route('/capture_photo')
def capture_photo():
    success, frame = camera.read()  # Capture one frame
    if success:
        # Save the captured frame as an image file
        cv2.imwrite('captured_photo.jpg', frame)
        return "Photo captured successfully!"
    else:
        return "Failed to capture photo."


@app.route('/bulk_email.html')
def bulk_email_form():
    return render_template('bulk_email.html')

load_dotenv()

# Email credentials
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'deepakkharodia50@gmail.com')  # Replace with your email
PASSWORD = os.getenv('PASSWORD', 'vfwykgxhmllovrfe')  # Replace with your password

# Send bulk email function
def send_bulk_email(recipients, subject, body):
    try:
        # Set up the SMTP server (using Gmail in this example)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, PASSWORD)

        # Loop through each recipient and send an email
        for recipient in recipients:
            # Create MIME object for each email
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient
            msg['Subject'] = subject

            # Attach the email body
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())

        server.quit()  # Close the SMTP server
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

# API route to send bulk emails
@app.route('/send_bulk_email', methods=['POST'])
def send_bulk_email_api():
    data = request.get_json()

    # Extract data from the JSON payload
    recipients = data.get('recipients')
    subject = data.get('subject')
    body = data.get('body')

    # Validate the input
    if not recipients or not subject or not body:
        return jsonify({'status': 'error', 'message': 'Missing recipients, subject, or body'}), 400

    # Call the function to send emails
    if send_bulk_email(recipients, subject, body):
        return jsonify({'status': 'success', 'message': 'Emails sent successfully!'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send emails'}), 500

@app.route('/google.html')
def google_form():
    return render_template('google.html')

# Replace with your SerpAPI key
SERPAPI_API_KEY = 'a2adf6609b9e0abefa4ce07c932f42801be41974b1d0c39c6c44597c3080a1dd'

@app.route('/search', methods=['GET'])
def google_search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    try:
        # Search on Google using SerpAPI
        search = GoogleSearch({
            "q": query,
            "num": 5,
            "api_key": SERPAPI_API_KEY
        })

        results = search.get_dict()

        top_results = []
        for result in results.get("organic_results", []):
            top_results.append({
                'title': result.get('title'),
                'link': result.get('link'),
                'snippet': result.get('snippet')
            })

        return jsonify({'query': query, 'top_results': top_results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/location.html')
def location_form():
    return render_template('location.html')
   
# Route to get geo coordinates and location
@app.route('/get-location', methods=['GET'])
def get_location():
    try:
        # Fetch IP-based location details from an external service
        response = requests.get('https://ipinfo.io/json')
        data = response.json()

        # Extract required details
        location_data = {
            'ip': data.get('ip'),
            'city': data.get('city'),
            'region': data.get('region'),
            'country': data.get('country'),
            'latitude': data.get('loc').split(',')[0],
            'longitude': data.get('loc').split(',')[1],
            'timezone': data.get('timezone'),
            'status': 'success'
        }

        return jsonify(location_data)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/linux_shortcuts.html')
def linux_shortcuts_form():
    return render_template('linux_shortcuts.html')



# Predefined dictionary of Linux shortcuts
linux_shortcuts = {
    "copy": "Ctrl + C",
    "paste": "Ctrl + V",
    "cut": "Ctrl + X",
    "find": "Ctrl + F",
    "undo": "Ctrl + Z",
    "redo": "Ctrl + Shift + Z",
    "save": "Ctrl + S",
    "close": "Ctrl + W",
    "terminal": "Ctrl + Alt + T",
    "switch windows": "Alt + Tab",
    "lock screen": "Ctrl + Alt + L",
    "screenshot": "PrtScn or Shift + PrtScn"
}

@app.route('/find-shortcut', methods=['GET'])
def find_shortcut():
    # Get query from request
    command = request.args.get('command', '').lower()
    
    # Search for the command in the dictionary
    shortcut = linux_shortcuts.get(command)
    
    if shortcut:
        return jsonify({
            'status': 'success',
            'command': command,
            'shortcut': shortcut
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'No shortcut found for "{command}". Try searching for another command.'
        }), 404

@app.route('/run_train.html')
def run_train_form():
    return render_template('run_train.html')

@app.route('/run-training', methods=['POST'])
def run_training():
    try:
        # Run the train.py script as if running it in the command prompt
        result = subprocess.run(['python', 'train.py'], capture_output=True, text=True, shell=True)

        # Return the output from the training script
        return jsonify({'status': 'success', 'output': result.stdout.strip()})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/send_email_pic.html')
def send_email_pic_form():
    return render_template('send_email_pic.html')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Function to capture photo
def capture_photo():
    cam = cv2.VideoCapture(0)  # Use the first available webcam
    result, image = cam.read()  # Capture the image
    if result:
        photo_path = 'captured_photo.jpg'  # Path to save the image
        cv2.imwrite(photo_path, image)  # Save the image to file
        cam.release()
        return photo_path
    else:
        logging.error("Failed to capture photo from webcam.")
        cam.release()
        return None

# Function to send email with captured photo as attachment
def send_email_with_photo(photo_path, receiver_email):
    sender_email = 'deepakkharodia50@gmail.com'  # Replace with your email
    sender_password = 'vfwykgxhmllovrfe'      # Replace with your email password
    subject = 'Captured Photo'

    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add body text to email
    body = 'Here is the captured photo.'
    msg.attach(MIMEText(body, 'plain'))

    # Attach the captured photo
    with open(photo_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(photo_path)}')
        msg.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        logging.info("Email sent successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

# Flask route to capture photo and send email
@app.route('/send-photo-email', methods=['POST'])
def send_photo_email():
    try:
        data = request.get_json()  # Extract JSON payload
        receiver_email = data.get('receiver_email')

        if not receiver_email:
            logging.error("Receiver email not provided.")
            return jsonify({'error': 'Receiver email not provided'}), 400

        photo_path = capture_photo()
        if not photo_path:
            return jsonify({'error': 'Failed to capture photo'}), 500

        success = send_email_with_photo(photo_path, receiver_email)
        if success:
            return jsonify({'message': 'Photo captured and email sent successfully!'}), 200
        else:
            return jsonify({'error': 'Failed to send email'}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/web_server.html')
def web_server_form():
    return render_template('web_server.html')


# Home route
@app.route('/') 
def home():
    return render_template('index.html')  # Render the HTML page

# API endpoint to get a greeting message
@app.route('/api/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'World')  # Get the 'name' query parameter
    return jsonify({'message': f'Hello, {name}!'})


@app.route('/ping_chat.html')
def ping_chat_form():
    return render_template('ping_chat.html')



def ping(ip_address):
    try:
        # Execute the ping command (4 pings)
        output = subprocess.check_output(['ping', '-c', '4', ip_address], universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Error pinging {ip_address}: {e}"

@app.route('/ping', methods=['POST'])
def ping_ip():
    data = request.get_json()
    ip_address = data.get('ip')

    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400

    ping_result = ping(ip_address)
    return jsonify({'ip': ip_address, 'result': ping_result}), 200



if __name__ == '__main__':  # Corrected __name__ check
    app.run(debug=True)
