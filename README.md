# TriviaGlow — Interactive Quiz Web Application

TriviaGlow is a modern, responsive, and interactive web-based quiz application built using Python (Flask) and MongoDB. It allows users to register, log in, take diverse quizzes, track their performance stats, and create their own custom quizzes.

## Key Features

- **User Authentication**: Secure signup and login powered by `bcrypt` password hashing.
- **Interactive Quiz Interface**: Timed quizzes with immediate scoring, feedback, and post-quiz answer reviews with detailed explanations.
- **Custom Quiz Creator**: Users can build new quizzes containing custom titles, descriptions, categories, time limits, and multiple-choice questions.
- **Leaderboard**: Displays rankings based on highest score/percentage and time taken. Filterable by category.
- **Profile & Statistics Dashboard**: Track quizzes taken, average score, total points, and progress across different category masteries.
- **Smart Dual Database Support**: Zero-configuration setup that connects to MongoDB, but automatically falls back to a local JSON file (`db_fallback.json`) if MongoDB is not running.

---

## Architecture & Database Fallback

TriviaGlow features an intelligent database abstraction layer inside [database.py](file:///home/hems/Downloads/quiz-app/database.py). 
- If a running MongoDB server is detected (on `mongodb://localhost:27017/`), the application uses the official MongoDB driver `pymongo`.
- If MongoDB is unreachable, it automatically swaps to a mock database using a local JSON file (`db_fallback.json`). This ensures you can run and test the application with zero external dependencies out-of-the-box.

---

## Project Structure

```text
├── app.py                  # Core Flask server and routing logic
├── database.py             # Database connectivity & fallback handler
├── db_fallback.json        # Local database file (fallback)
├── test_app.py             # Test suite for verifying route handlers and forms
├── static/                 # Static assets
│   └── css/
│       └── style.css       # Custom stylesheet (Glassmorphic theme)
├── templates/              # HTML layout templates using Jinja2
│   ├── base.html           # Main template containing layout and database status bar
│   ├── dashboard.html      # Home dashboard & category listing
│   ├── leaderboard.html    # Ranked leaderboard
│   ├── login.html          # Login portal
│   ├── profile.html        # User statistics and history
│   ├── quiz_create.html    # Form to create new quizzes
│   ├── quiz_details.html   # Pre-quiz details page
│   ├── quiz_result.html    # Detailed result of a completed attempt
│   ├── quiz_take.html      # Interactive quiz taker (JS-driven)
│   └── register.html       # Signup page
└── venv/                   # Local Python virtual environment
```

---

## Installation & Setup

Follow these steps to run the application locally:

### 1. Clone the repository and navigate to the project directory
```bash
cd /home/hems/Downloads/quiz-app
```

### 2. Set up a virtual environment (optional but recommended)
If a virtual environment is not active:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

### 3. Install required packages
Ensure you have the required dependencies:
```bash
pip install flask pymongo bcrypt
```

### 4. Start the Application
Run the Flask server:
```bash
python app.py
```
By default, the server starts in debug mode and will be accessible at:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Running Tests
To verify routes and database functionality:
```bash
python -m unittest test_app.py
```
