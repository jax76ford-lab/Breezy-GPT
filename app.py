from flask import Flask, request, session
import requests, os, markdown

app = Flask(__name__)
app.secret_key = "breezy-super-secret-123"

# It will use GROQ_API_KEY from Render later, or your key here for now
API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_KEY_HERE")
@app.route("/")
def home():
    history = session.get("history", [])
    chats = ""
    for h in history:
        if h["role"] == "user":
            chats += f'<div style="text-align:right; margin:10px;"><span style="background:#a855f7; color:white; padding:10px 15px; border-radius:20px 20px 5px 20px; display:inline-block; max-width:85%; text-align:left;">{h["content"]}</span></div>'
        else:
            chats += f'<div style="text-align:left; margin:10px;"><span style="background:white; padding:12px 15px; border-radius:20px 20px 20px 5px; display:inline-block; max-width:90%; box-shadow:0 2px 5px rgba(0,0,0,0.1);">💜 {h["content"]}</span></div>'

    return f"""
    <head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="background:#f3e8ff; font-family:sans-serif; margin:0; display:flex; flex-direction:column; height:100vh;">
    <div style="background:purple; color:white; padding:15px; text-align:center; font-weight:bold; font-size:20px; position:sticky; top:0;">💜 Breezy GPT <a href="/clear" style="color:white; font-size:12px; float:right; text-decoration:none;">New Chat 🗑️</a></div>
    <div style="flex:1; overflow-y:auto; padding:10px; padding-bottom:90px;">{chats if chats else '<p style="text-align:center; color:gray; margin-top:50px;">Ask me anything...<br>✨ I remember everything you say! ✨</p>'}</div>
    <form action="/chat" method="post" style="position:fixed; bottom:0; left:0; right:0; background:white; padding:10px; display:flex; gap:10px; box-shadow:0 -2px 10px rgba(0,0,0,0.1);">
    <input name="msg" placeholder="Message Breezy GPT..." autofocus style="flex:1; padding:14px; border-radius:25px; border:1px solid #ddd; outline:none;">
    <button style="background:purple; color:white; border:none; padding:0 20px; border-radius:25px; font-size:20px;">➤</button>
    </form>
    </body>
    """

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.form.get("msg", "")
    history = session.get("history", [])
    history.append({"role": "user", "content": msg})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": "openai/gpt-oss-20b", "messages": [{"role": "system", "content": "You are Breezy GPT, a fun friendly assistant for Breezy. Answer short, fun, helpful."}] + history[-10:]}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        j=r.json()
        reply = j["choices"][0]["message"]["content"] if "choices" in j else f"GROQ SAYS: {j}"
    except Exception as e:
        reply = f"Oops error: {e}"
    
    # Make **bold** work
    reply_html = markdown.markdown(reply)
    history.append({"role": "assistant", "content": reply_html})
    session["history"] = history
    return '<script>window.location.href="/"</script>'

@app.route("/clear")
def clear():
    session.clear()
    return '<script>window.location.href="/"</script>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
