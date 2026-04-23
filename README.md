# Fake News Headline Generator

Live App: https://fake-news-generator-9soi.onrender.com/

A Flask-based web application that generates satirical/fake news headlines.
It supports AI-generated content using OpenAI and also works with built-in templates if the API is not available.

---

## Features

* User signup and login
* Generate headlines by category
* Choose tone and number of headlines
* Save generated headlines
* Mark and manage favorites
* View trending headlines
* Works with or without OpenAI API

---

## Tech Stack

* Python (Flask)
* SQLite
* HTML, CSS, JavaScript
* OpenAI API (optional)

---

## Project Structure

```
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

## Run Locally

1. Clone the repository

```
git clone <your-repo-link>
cd project
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Create `.env` file

```
OPENAI_API_KEY=your_api_key
SECRET_KEY=your_secret
```

4. Run the application

```
python fake_headline_generator.py
```

5. Open in browser

```
http://localhost:5000
```

---

## Deployment (Render)

* Build Command:

```
pip install -r requirements.txt
```

* Start Command:

```
gunicorn fake_headline_generator:app
```

* Environment Variables:

```
OPENAI_API_KEY=your_key
SECRET_KEY=your_secret
```

---

## Notes

* If the OpenAI API key is not provided, the app uses fallback templates
* `users.db` is created automatically
* SQLite data may reset after redeploy (not persistent storage)

---

## Author

Manisha Banerjee
