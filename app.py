from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

# Configurations
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATA_FILE = 'data/user_data.json'

# Ensure the data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({"profile": {}, "tweets": []}, f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def home():
    data = load_data()
    profile = data.get("profile", {})
    tweets = data.get("tweets", [])
    return render_template('home.html', profile=profile, tweets=reversed(tweets))  # Show newest first

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    data = load_data()
    profile = data.get("profile", {})
    
    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        
        # Handle profile picture upload
        profile_pic = request.files.get('profile_pic')
        if profile_pic:
            profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pic.png')
            profile_pic.save(profile_pic_path)
            profile['profile_pic'] = profile_pic_path
        
        # Handle banner upload
        banner = request.files.get('banner')
        if banner:
            banner_path = os.path.join(app.config['UPLOAD_FOLDER'], 'banner.png')
            banner.save(banner_path)
            profile['banner'] = banner_path
        
        profile['name'] = name
        profile['bio'] = bio
        
        data['profile'] = profile
        save_data(data)
        return redirect(url_for('profile'))
    
    return render_template('profile.html', profile=profile)

@app.route('/tweet', methods=['POST'])
def tweet():
    data = load_data()
    tweets = data.get("tweets", [])
    profile = data.get("profile", {})
    
    tweet_content = request.form.get('tweet')
    if tweet_content:
        tweets.append({
            "content": tweet_content,
            "username": profile.get('name', 'Anonymous'),
            "profile_pic": profile.get('profile_pic', None),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        data['tweets'] = tweets
        save_data(data)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
