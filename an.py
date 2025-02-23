from flask import Flask, request, render_template_string
import requests
import time
import random

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment & Group Messenger</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment & Group Messenger</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <h3>Auto Comment Section</h3>
        <input type="file" name="comment_token_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="comment_time" placeholder="Comment Interval in Seconds" required><br>
        
        <h3>Auto Group Messenger Section</h3>
        <input type="file" name="message_token_file" accept=".txt" required><br>
        <input type="file" name="message_file" accept=".txt" required><br>
        <input type="text" name="hatter_name" placeholder="Enter Message Header" required><br>
        <input type="text" name="group_number" placeholder="Enter Convo Group Number" required><br>
        <input type="file" name="time_file" accept=".txt" required><br>

        <button type="submit">Start Auto Posting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    comment_token_file = request.files['comment_token_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    comment_time = int(request.form['comment_time'])

    message_token_file = request.files['message_token_file']
    message_file = request.files['message_file']
    hatter_name = request.form['hatter_name']
    group_number = request.form['group_number']
    time_file = request.files['time_file']

    comment_tokens = comment_token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    message_tokens = message_token_file.read().decode('utf-8').splitlines()
    messages = message_file.read().decode('utf-8').splitlines()
    time_intervals = [int(line.strip()) for line in time_file.read().decode('utf-8').splitlines()]

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    comment_url = f"https://graph.facebook.com/{post_id}/comments"
    message_url = f"https://graph.facebook.com/{group_number}/feed"

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)"
    ]

    def modify_text(text):
        emojis = ["🔥", "✅", "💯", "👏", "😊", "👍", "🙌", "🎉", "😉", "💪"]
        variations = ["!!", "!!!", "✔️", "...", "🤩", "💥"]
        return f"{random.choice(variations)} {text} {random.choice(emojis)}"

    def post_with_token(token, url, text):
        headers = {"User-Agent": random.choice(user_agents)}
        payload = {'message': modify_text(text), 'access_token': token}
        response = requests.post(url, data=payload, headers=headers)
        return response

    comment_index = 0
    message_index = 0
    active_comment_tokens = list(comment_tokens)
    active_message_tokens = list(message_tokens)

    while True:
        if not active_comment_tokens:
            active_comment_tokens = list(comment_tokens)
            print("🔄 सभी Comment Tokens Reset कर दिए गए!")

        if not active_message_tokens:
            active_message_tokens = list(message_tokens)
            print("🔄 सभी Message Tokens Reset कर दिए गए!")

        comment_token = active_comment_tokens[comment_index % len(active_comment_tokens)]
        comment_text = comments[comment_index % len(comments)]
        message_token = active_message_tokens[message_index % len(active_message_tokens)]
        message_text = f"{hatter_name}: {messages[message_index % len(messages)]}"

        comment_response = post_with_token(comment_token, comment_url, comment_text)
        message_response = post_with_token(message_token, message_url, message_text)

        if comment_response.status_code == 200:
            print(f"✅ Comment Success with Token {comment_index+1}")
        else:
            print(f"❌ Comment Token {comment_index+1} Blocked, Removing...")
            active_comment_tokens.remove(comment_token)

        if message_response.status_code == 200:
            print(f"✅ Group Message Success with Token {message_index+1}")
        else:
            print(f"❌ Message Token {message_index+1} Blocked, Removing...")
            active_message_tokens.remove(message_token)

        comment_index += 1  
        message_index += 1  

        safe_delay = random.choice(time_intervals)
        print(f"⏳ Waiting {safe_delay} seconds before next action...")
        time.sleep(safe_delay)

    return render_template_string(HTML_FORM, message=f"✅ Auto Posting Started!")

if __name__ == '__main__':
    port = 10000  
    app.run(host='0.0.0.0', port=port)
