from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime
import random

# AI Integration
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "OPENAI_API_KEY":
        client = OpenAI(api_key=api_key)
        AI_AVAILABLE = True
        print("✅ OpenAI API initialized")
    else:
        print("⚠️ No valid OpenAI API key - using fallback")
        AI_AVAILABLE = False
except Exception as e:
    print(f"❌ AI Error: {e}")
    AI_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "sk-...ewUA")

# Database initialization
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS headlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            category TEXT NOT NULL,
            headline TEXT NOT NULL,
            is_favorite INTEGER DEFAULT 0,
            views INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email) REFERENCES users(email)
        )
    ''')
    
    conn.commit()
    conn.close()

HEADLINE_TEMPLATES = {
    "ai_tech": {
        "templates": ["{subject} {action} {object}", "BREAKING: {subject} {action} {object}!"],
        "subjects": ["OpenAI", "Google DeepMind", "Meta AI", "Elon Musk", "A startup"],
        "actions": ["launches", "releases", "announces"],
        "objects": ["AI model", "quantum chip", "neural network"],
    },
    "world": {
        "templates": ["{country} {action} {object}", "BREAKING: {country} {action} {object}!"],
        "subjects": ["India", "USA", "China"],
        "actions": ["discovers", "announces"],
        "objects": ["peace treaty", "space mission"],
    },
    "politics": {
        "templates": ["{subject} {action} {object}!", "HISTORIC: {subject} {action}!"],
        "subjects": ["PM Modi", "Opposition", "Parliament"],
        "actions": ["announces", "proposes"],
        "objects": ["historic policy", "new law"],
    },
    "sports": {
        "templates": ["{athlete} {action} {object}!", "BREAKING: {athlete} {action} {object}!"],
        "subjects": ["Virat Kohli", "MS Dhoni", "Rohit Sharma"],
        "actions": ["scores", "breaks", "wins"],
        "objects": ["world record", "tournament"],
    },
    "entertainment": {
        "templates": ["{subject} {action} {object}!", "BREAKING: {subject} {action}!"],
        "subjects": ["SRK", "Bollywood", "Netflix"],
        "actions": ["announces", "launches"],
        "objects": ["new movie", "web series"],
    },
    "business": {
        "templates": ["{company} {action} {object}!", "BREAKING: {company} {action}!"],
        "subjects": ["Reliance", "TCS", "Infosys"],
        "actions": ["acquires", "launches"],
        "objects": ["startup", "company"],
    },
    "lifestyle": {
        "templates": ["{subject} {action} {object}!", "NEW TREND: {subject} {action}"],
        "subjects": ["Health experts", "Celebrity chef", "Nutritionist"],
        "actions": ["reveals", "launches"],
        "objects": ["diet trend", "recipe"],
    },
    "weird": {
        "templates": ["WTF: {subject} {action} {object}!", "INSANE: {subject} {action}!"],
        "subjects": ["Aliens", "Time travelers", "AI robots"],
        "actions": ["discovered", "landed"],
        "objects": ["on Earth", "in Mumbai"],
    },
    "space": {
        "templates": ["COSMIC: {subject} {action} {object}!", "SPACE NEWS: {subject} {action}!"],
        "subjects": ["NASA", "ISRO", "SpaceX"],
        "actions": ["discovers", "launches"],
        "objects": ["alien life", "new planet"],
    },
    "social_media": {
        "templates": ["{subject} {action} {object}!", "VIRAL: {subject} {action}"],
        "subjects": ["TikTok", "Instagram", "YouTube"],
        "actions": ["removes", "bans"],
        "objects": ["feature", "account"],
    },
    "startup": {
        "templates": ["{subject} {action} {object}!", "{subject} {action} Series {series}!"],
        "subjects": ["Startup", "Founder", "Tech company"],
        "actions": ["raises", "launches"],
        "objects": ["funding", "product"],
        "series": ["A", "B", "C"]
    }
}

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def generate_ai_headline(category, tone="funny"):
    """Generate headline using AI or fallback"""
    if not AI_AVAILABLE:
        print(f"Using fallback for category: {category}")
        return generate_fallback_headline(category)
    
    try:
        prompt = f"Generate a short satirical fake news headline for {category} in {tone} tone. Max 15 words."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.8
        )
        headline = response.choices[0].message.content.strip()
        print(f"✅ AI generated for {category}: {headline}")
        return headline
    except Exception as e:
        print(f"❌ AI Error: {e} - Using fallback")
        return generate_fallback_headline(category)

def generate_fallback_headline(category):
    """Generate headline without AI"""
    if category not in HEADLINE_TEMPLATES:
        category = "weird"
    
    data = HEADLINE_TEMPLATES[category]
    template = random.choice(data["templates"])
    
    kwargs = {}
    for key in ["subject", "action", "object", "country", "company", "athlete", "series"]:
        if f"{{{key}}}" in template and key in data:
            kwargs[key] = random.choice(data[key])
    
    headline = template.format(**kwargs)
    print(f"📝 Fallback generated for {category}: {headline}")
    return headline

def save_headline(email, category, headline):
    """Save headline to database"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "INSERT INTO headlines (email, category, headline) VALUES (?, ?, ?)",
            (email, category, headline)
        )
        conn.commit()
        conn.close()
        print(f"✅ Headline saved to DB")
    except Exception as e:
        print(f"❌ Error saving headline: {e}")

def get_user_headlines(email, limit=50):
    """Get user's headlines"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "SELECT id, headline, category, created_at, is_favorite FROM headlines WHERE email = ? ORDER BY created_at DESC LIMIT ?",
            (email, limit)
        )
        headlines = c.fetchall()
        conn.close()
        return headlines
    except Exception as e:
        print(f"❌ Error fetching headlines: {e}")
        return []

def get_user_favorites(email):
    """Get user's favorite headlines"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "SELECT id, headline, category, created_at FROM headlines WHERE email = ? AND is_favorite = 1 ORDER BY created_at DESC",
            (email,)
        )
        headlines = c.fetchall()
        conn.close()
        return headlines
    except Exception as e:
        print(f"❌ Error fetching favorites: {e}")
        return []

def get_trending_headlines():
    """Get trending headlines"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "SELECT headline, category, COUNT(*) as count FROM headlines GROUP BY headline ORDER BY count DESC LIMIT 10"
        )
        results = c.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"❌ Error fetching trending: {e}")
        return []

# ============= ROUTES =============

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        if not email or not password:
            error = "Email and password required"
        else:
            try:
                conn = get_db()
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE email = ?", (email,))
                user = c.fetchone()
                conn.close()
                
                if user and check_password_hash(user['password'], password):
                    session["user"] = email
                    print(f"✅ User logged in: {email}")
                    return redirect(url_for("home"))
                else:
                    error = "Invalid email or password"
            except Exception as e:
                error = f"Login error: {e}"
                print(f"❌ Login error: {e}")
    
    return render_template("login.html", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not email or not password:
            error = "Email and password required"
        elif password != confirm_password:
            error = "Passwords don't match"
        elif len(password) < 6:
            error = "Password too short (min 6 chars)"
        else:
            try:
                conn = get_db()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users (email, password) VALUES (?, ?)",
                    (email, generate_password_hash(password))
                )
                conn.commit()
                conn.close()
                print(f"✅ New user signed up: {email}")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Email already exists"
            except Exception as e:
                error = f"Signup error: {e}"
                print(f"❌ Signup error: {e}")
    
    return render_template("signup.html", error=error)

@app.route("/home", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    
    user_email = session["user"]
    category = request.form.get("category", "ai_tech")
    headlines = []
    error = None
    
    if request.method == "POST":
        try:
            count = int(request.form.get("count", 1))
            tone = request.form.get("tone", "funny")
            
            print(f"\n🎯 Generating {count} headlines for {category} in {tone} tone")
            
            for i in range(min(count, 5)):
                headline = generate_ai_headline(category, tone)
                save_headline(user_email, category, headline)
                headlines.append(headline)
            
            print(f"✅ Generated {len(headlines)} headlines")
        except Exception as e:
            error = f"Error generating headlines: {e}"
            print(f"❌ Generation error: {e}")
    
    user_headlines = get_user_headlines(user_email, 20)
    categories = list(HEADLINE_TEMPLATES.keys())
    
    return render_template(
        "index.html",
        headlines=headlines,
        category=category,
        user_headlines=user_headlines,
        categories=categories,
        ai_available=AI_AVAILABLE,
        error=error
    )

@app.route("/favorites")
def favorites():
    if "user" not in session:
        return redirect(url_for("login"))
    
    favorites = get_user_favorites(session["user"])
    return render_template("favorites.html", favorites=favorites)

@app.route("/trending")
def trending():
    if "user" not in session:
        return redirect(url_for("login"))
    
    trending_headlines = get_trending_headlines()
    return render_template("trending.html", trending=trending_headlines)

@app.route("/api/toggle-favorite/<int:headline_id>", methods=["POST"])
def toggle_favorite(headline_id):
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT is_favorite FROM headlines WHERE id = ?", (headline_id,))
        row = c.fetchone()
        
        if row:
            new_status = 1 - row['is_favorite']
            c.execute("UPDATE headlines SET is_favorite = ? WHERE id = ?", (new_status, headline_id))
            conn.commit()
            conn.close()
            return jsonify({"success": True, "is_favorite": new_status})
        
        conn.close()
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        print(f"❌ Toggle favorite error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":

    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

    init_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀 Starting app on port {port}")
    print(f"🤖 AI Available: {AI_AVAILABLE}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
