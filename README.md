# Fake News Headline Generator

Flask web app to generate fake/satirical news headlines.
Supports AI generation (OpenAI) and fallback templates.

---

## Features

* User signup and login
* Generate headlines by category
* Select tone and number of headlines
* Save headlines to database
* Mark/unmark favorites
* View trending headlines
* Works without API (fallback mode)

---

## Tech Stack

* Python (Flask)
* SQLite
* HTML, CSS, JavaScript
* OpenAI API (optional)

---

## Project Structure

```id="8n4w0m"
.
├── fake_headline_generator.py
├── requirements.txt
├── .env
├── users.db
│
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── index.html
│   ├── favourites.html
│   └── trending.html
│
├── static/
│   ├── dashboard.css
│   └── style.css
```

---

## Setup (Local)

1. Clone repo

```id="8sz0fv"
git clone <your-repo-link>
cd project
```

2. Install dependencies

```id="l3euj7"
pip install -r requirements.txt
```

3. Create `.env`

```id="nq8dcm"
OPENAI_API_KEY=your_api_key
SECRET_KEY=your_secret
```

4. Run

```id="8c3ym9"
python fake_headline_generator.py
```

5. Open

```id="z1ttsf"
http://localhost:5000
```

---

## Deployment (Render)

* Build command:

```id="c9u6vn"
pip install -r requirements.txt
```

* Start command:

```id="6sv8yz"
gunicorn fake_headline_generator:app
```

* Environment Variables:

```id="h2u8dx"
OPENAI_API_KEY=your_key
SECRET_KEY=your_secret
```

---

## Notes

* If OpenAI API key is not set, fallback headlines are used
* `users.db` is created automatically
* SQLite data may reset after redeploy

---

## Author

Manisha Banerjee
