from flask import Flask, request,send_file,Response,jsonify, render_template
import pythoncom
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from twilio.rest import Client
from flask_socketio import SocketIO, emit
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from googlesearch import search
from flask_cors import CORS
from gtts import gTTS
from plivo import RestClient
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

account_sid = 'AC0d085c9c6fa060904d204c998ca2ebcb'
auth_token = '8050cee8f611077a58e1e48e8fd6c000'

# Initialize the Twilio client
client = Client(account_sid, auth_token)

@app.route('/send-whatsapp', methods=['POST'])
def send_whatsapp():
    data = request.json
    to_number = data.get('to_number')
    message_body = data.get('message_body')

    # Twilio WhatsApp number (must be valid and configured)
    from_number = 'whatsapp:+14155238886'  # Replace with your Twilio WhatsApp number

    try:
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to='whatsapp:' + to_number
        )
        return jsonify({'status': 'Message sent successfully!', 'sid': message.sid})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


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

logging.basicConfig(level=logging.INFO)

# Ensure the uploads directory exists
os.makedirs('uploads', exist_ok=True)

# Initialize the Instagram bot
bot = Bot()

def upload_to_instagram(image_path, caption):
    try:
        # Login to Instagram
        username = 'python7372'
        password = 'PYTHON555'
        logging.info("Logging into Instagram...")
        bot.login(username=username, password=password)

        logging.info(f"Uploading {image_path} with caption: {caption}")
        bot.upload_photo(image_path, caption=caption)

        logging.info("Upload successful!")
        os.remove(image_path)  # Optionally remove the temporary file after upload
    except Exception as e:
        logging.error(f"Error during upload: {str(e)}")

@app.route('/upload', methods=['POST'])
def upload_picture():
    if 'image_path' not in request.files:
        return jsonify({'error': 'Image file is required.'}), 400

    image_file = request.files['image_path']
    caption = request.form.get('caption', '')

    if image_file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    try:
        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join('uploads', image_file.filename)
        image_file.save(temp_file_path)

        # Start a new thread for the Instagram upload
        thread = threading.Thread(target=upload_to_instagram, args=(temp_file_path, caption))
        thread.start()

        return jsonify({'message': 'Photo upload in progress!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500







@app.route('/make_call.html')  # Ensure that the URL starts with a '/'
def make_call_form():
    return render_template('make_call.html')

TWILIO_ACCOUNT_SID = 'AC0d085c9c6fa060904d204c998ca2ebcb'
TWILIO_AUTH_TOKEN = '8050cee8f611077a58e1e48e8fd6c000'
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

def scrape_google(query, num_results=4):
    search_results = []
    for result in search(query, num_results=num_results):
        search_results.append(result)
    return search_results

# Define the Flask route for the API
@app.route('/search', methods=['GET'])
def google_search():
    # Get the search query and number of results from URL parameters
    query = request.args.get('query')
    num_results = request.args.get('num_results', 4)  # Default to 4 results if not provided

    # Check if query is provided
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Scrape Google for search results
    try:
        results = scrape_google(query, int(num_results))
        return jsonify({"status": "success", "results": results}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
   


if __name__ == '__main__':  # Corrected __name__ check
    app.run(debug=True)
