import os
import requests
from flask import Flask, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
APP_ID = os.getenv('APP_ID')
APP_SECRET = os.getenv('APP_SECRET')
REDIRECT_URI = 'https://your-heroku-app.herokuapp.com/callback'

@app.route('/')
def home():
    return '''
        <h1>Facebook Bot</h1>
        <a href="/login">Login with Facebook</a>
    '''

@app.route('/login')
def login():
    fb_login_url = f"https://www.facebook.com/v11.0/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope=public_profile,email"
    return redirect(fb_login_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = f"https://graph.facebook.com/v11.0/oauth/access_token?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&client_secret={APP_SECRET}&code={code}"
    token_response = requests.get(token_url).json()
    session['access_token'] = token_response['access_token']
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))
    
    profile_url = f"https://graph.facebook.com/me?access_token={access_token}"
    profile_response = requests.get(profile_url).json()
    return jsonify(profile_response)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for event in entry['messaging']:
                if event.get('message'):
                    sender_id = event['sender']['id']
                    message_text = event['message']['text']
                    send_message(sender_id, "Thank you for your message!")
    return "ok", 200

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v11.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, headers=headers, json=data)

if __name__ == '__main__':
    app.run(debug=True)
