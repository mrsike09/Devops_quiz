import os
import datetime
import uuid
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import get_db, get_db_status

app = Flask(__name__)
# Generate a static secret key for stable sessions
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-quiz-key-1337-abc")

db = get_db()

# Seed default quizzes if collection is empty
DEFAULT_QUIZZES = [
    {
        "_id": "seed-quiz-tech",
        "title": "Tech & Programming Trivia",
        "description": "Test your knowledge on computer science, coding, and tech history!",
        "category": "Technology",
        "difficulty": "Medium",
        "time_limit": 5,
        "creator_name": "System",
        "questions": [
            {
                "text": "Who is considered the father of computers?",
                "options": ["Alan Turing", "Charles Babbage", "Bill Gates", "Ada Lovelace"],
                "correct_option": 1,
                "explanation": "Charles Babbage designed the Analytical Engine, which is considered the first general mechanical computer concept."
            },
            {
                "text": "What does CSS stand for in web design?",
                "options": ["Computer Style Sheets", "Cascading Style Sheets", "Creative Style System", "Complex Style Sheets"],
                "correct_option": 1,
                "explanation": "CSS stands for Cascading Style Sheets, used to describe the presentation of a document written in HTML."
            },
            {
                "text": "Which programming language was originally named 'Oak'?",
                "options": ["Java", "C++", "Python", "Ruby"],
                "correct_option": 0,
                "explanation": "Java was originally initiated by James Gosling and named 'Oak' after an oak tree that stood outside his office."
            },
            {
                "text": "What is the primary protocol used to secure communication over the web?",
                "options": ["HTTP", "FTP", "HTTPS", "SMTP"],
                "correct_option": 2,
                "explanation": "HTTPS (Hypertext Transfer Protocol Secure) encrypts communication using TLS/SSL to protect data integrity and privacy."
            },
            {
                "text": "Which of the following is not a relational database system?",
                "options": ["PostgreSQL", "MySQL", "MongoDB", "Oracle"],
                "correct_option": 2,
                "explanation": "MongoDB is a document-oriented, non-relational (NoSQL) database, whereas MySQL, PostgreSQL, and Oracle are relational (SQL) databases."
            }
        ]
    },
    {
        "_id": "seed-quiz-geo",
        "title": "World Geography Challenge",
        "description": "Embark on a journey to identify countries, capitals, and natural wonders!",
        "category": "Geography",
        "difficulty": "Easy",
        "time_limit": 4,
        "creator_name": "System",
        "questions": [
            {
                "text": "What is the capital of Australia?",
                "options": ["Sydney", "Melbourne", "Canberra", "Brisbane"],
                "correct_option": 2,
                "explanation": "Canberra is the capital city of Australia, selected as a compromise between rival cities Sydney and Melbourne."
            },
            {
                "text": "Which is the largest ocean on Earth?",
                "options": ["Atlantic Ocean", "Indian Ocean", "Southern Ocean", "Pacific Ocean"],
                "correct_option": 3,
                "explanation": "The Pacific Ocean is the largest and deepest of Earth's oceanic divisions, covering about 30% of the Earth's surface."
            },
            {
                "text": "Which country is home to the landmark 'Machu Picchu'?",
                "options": ["Peru", "Brazil", "Colombia", "Mexico"],
                "correct_option": 0,
                "explanation": "Machu Picchu is a 15th-century Inca citadel located in the Eastern Cordillera of southern Peru."
            },
            {
                "text": "What is the longest river in the world?",
                "options": ["Amazon River", "Nile River", "Yangtze River", "Mississippi River"],
                "correct_option": 1,
                "explanation": "While there is ongoing debate, the Nile River is traditionally considered the longest river in the world, stretching over 6,650 kilometers."
            },
            {
                "text": "Which European nation features the active volcano Mount Etna?",
                "options": ["Greece", "Italy", "Spain", "Iceland"],
                "correct_option": 1,
                "explanation": "Mount Etna is an active stratovolcano on the east coast of Sicily, Italy."
            }
        ]
    },
    {
        "_id": "seed-quiz-sci",
        "title": "Cosmic Science Quiz",
        "description": "Test your grasp on astronomy, physics, and the mysteries of the universe!",
        "category": "Science",
        "difficulty": "Hard",
        "time_limit": 6,
        "creator_name": "System",
        "questions": [
            {
                "text": "Approximately how long does it take light from the Sun to reach Earth?",
                "options": ["8 seconds", "8 minutes", "8 hours", "8 days"],
                "correct_option": 1,
                "explanation": "Light travels at 300,000 km/s. Given the Sun's distance from Earth, it takes about 8 minutes and 20 seconds for sunlight to reach us."
            },
            {
                "text": "Which particle in an atom carries a negative electrical charge?",
                "options": ["Proton", "Neutron", "Electron", "Quark"],
                "correct_option": 2,
                "explanation": "Electrons carry a negative charge (-1e) and orbit the atomic nucleus, which contains protons (positive) and neutrons (neutral)."
            },
            {
                "text": "What is the main element that makes up the Sun?",
                "options": ["Helium", "Oxygen", "Hydrogen", "Carbon"],
                "correct_option": 2,
                "explanation": "Hydrogen makes up about 73% of the Sun's mass, with helium constituting most of the remaining 25%."
            },
            {
                "text": "Who formulated the laws of electromagnetic induction?",
                "options": ["Nikola Tesla", "Michael Faraday", "James Clerk Maxwell", "Heinrich Hertz"],
                "correct_option": 1,
                "explanation": "Michael Faraday discovered electromagnetic induction in 1831, showing that a magnetic field can induce an electric current."
            },
            {
                "text": "What is the escape velocity required to break free from Earth's gravity?",
                "options": ["5.5 km/s", "11.2 km/s", "24.8 km/s", "42.1 km/s"],
                "correct_option": 1,
                "explanation": "The escape velocity of Earth is approximately 11.2 kilometers per second (about 40,320 km/h or 25,050 mph)."
            }
        ]
    }
]

def seed_db():
    try:
        if db.quizzes.count_documents({}) == 0:
            print("Seeding database with default quizzes...")
            for q in DEFAULT_QUIZZES:
                db.quizzes.insert_one(q)
    except Exception as e:
        print(f"Error seeding database: {e}")

seed_db()

# --- Helpers & Decorators ---
def login_required(f):
    import functools
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_db_status():
    return dict(db_status=get_db_status())

# --- Routes ---

# Home Dashboard
@app.route('/')
def dashboard():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    difficulty = request.args.get('difficulty', '')
    
    query = {}
    if search:
        # In a mock db, simple string checking is done. In MongoDB, regex would be best.
        # Let's support regex-like query in search or direct checking
        pass
        
    quizzes = db.quizzes.find()
    
    # Filter in Python to work perfectly with both MongoDB and JSON Fallback
    filtered_quizzes = []
    for q in quizzes:
        if search and search.lower() not in q.get('title', '').lower() and search.lower() not in q.get('description', '').lower():
            continue
        if category and q.get('category') != category:
            continue
        if difficulty and q.get('difficulty') != difficulty:
            continue
        filtered_quizzes.append(q)
        
    # Get all categories
    categories = sorted(list(set(q.get('category') for q in db.quizzes.find() if q.get('category'))))
    
    # Stats for the logged in user
    user_stats = None
    recent_attempts = []
    if 'user_id' in session:
        user = db.users.find_one({'_id': session['user_id']})
        if user:
            user_stats = user.get('stats', {
                'quizzes_taken': 0,
                'average_score': 0,
                'total_points': 0,
                'category_mastery': {}
            })
            recent_attempts = db.attempts.find({'user_id': session['user_id']}, sort=[('created_at', -1)])[:5]
            
    return render_template('dashboard.html', quizzes=filtered_quizzes, categories=categories, 
                           user_stats=user_stats, recent_attempts=recent_attempts,
                           search=search, category=category, difficulty=difficulty)

# Auth - Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for('register'))
            
        # Check if username exists
        existing_user = db.users.find_one({'username': username})
        if existing_user:
            flash("Username is already taken.", "danger")
            return redirect(url_for('register'))
            
        # Hash password and create user
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = str(uuid.uuid4())
        
        new_user = {
            '_id': user_id,
            'username': username,
            'password': hashed_pw,
            'created_at': datetime.datetime.now().isoformat(),
            'stats': {
                'quizzes_taken': 0,
                'average_score': 0,
                'total_points': 0,
                'category_mastery': {}
            }
        }
        db.users.insert_one(new_user)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

# Auth - Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = db.users.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['_id']
            session['username'] = user['username']
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('login.html')

# Auth - Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Profile & Progress Metrics
@app.route('/profile')
@login_required
def profile():
    user = db.users.find_one({'_id': session['user_id']})
    if not user:
        session.clear()
        return redirect(url_for('login'))
        
    attempts = db.attempts.find({'user_id': session['user_id']}, sort=[('created_at', -1)])
    
    # Calculate stats
    stats = user.get('stats', {
        'quizzes_taken': 0,
        'average_score': 0,
        'total_points': 0,
        'category_mastery': {}
    })
    
    return render_template('profile.html', user=user, attempts=attempts, stats=stats)

# Quiz Taking Interface
@app.route('/quiz/<quiz_id>')
@login_required
def quiz_details(quiz_id):
    quiz = db.quizzes.find_one({'_id': quiz_id})
    if not quiz:
        flash("Quiz not found.", "danger")
        return redirect(url_for('dashboard'))
    return render_template('quiz_details.html', quiz=quiz)

@app.route('/quiz/<quiz_id>/take')
@login_required
def quiz_take(quiz_id):
    quiz = db.quizzes.find_one({'_id': quiz_id})
    if not quiz:
        flash("Quiz not found.", "danger")
        return redirect(url_for('dashboard'))
        
    return render_template('quiz_take.html', quiz=quiz)

# Submit Quiz Attempt
@app.route('/quiz/<quiz_id>/submit', methods=['POST'])
@login_required
def quiz_submit(quiz_id):
    quiz = db.quizzes.find_one({'_id': quiz_id})
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
        
    data = request.get_json() or {}
    user_answers = data.get('answers', {}) # format: { "0": 1, "1": 3, ... }
    time_taken = data.get('time_taken', 0) # in seconds
    
    score = 0
    questions = quiz.get('questions', [])
    total_questions = len(questions)
    
    # Format answers dictionary
    detailed_answers = []
    for i, q in enumerate(questions):
        # user answer string key is due to json serialization
        user_select = user_answers.get(str(i))
        if user_select is not None:
            user_select = int(user_select)
        
        correct = q['correct_option']
        is_correct = (user_select == correct)
        if is_correct:
            score += 1
            
        detailed_answers.append({
            'question_index': i,
            'selected': user_select,
            'correct': correct,
            'is_correct': is_correct
        })
        
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    # Save Attempt
    attempt_id = str(uuid.uuid4())
    attempt = {
        '_id': attempt_id,
        'user_id': session['user_id'],
        'username': session['username'],
        'quiz_id': quiz_id,
        'quiz_title': quiz['title'],
        'quiz_category': quiz['category'],
        'score': score,
        'total_questions': total_questions,
        'percentage': round(percentage, 1),
        'time_taken': time_taken,
        'answers': user_answers,
        'created_at': datetime.datetime.now().isoformat()
    }
    db.attempts.insert_one(attempt)
    
    # Update User Stats
    user = db.users.find_one({'_id': session['user_id']})
    if user:
        all_attempts = db.attempts.find({'user_id': session['user_id']})
        total_taken = len(all_attempts)
        avg_score = sum(att['percentage'] for att in all_attempts) / total_taken
        
        # Calculate category mastery
        cat_scores = {}
        for att in all_attempts:
            cat = att.get('quiz_category', 'General')
            if cat not in cat_scores:
                cat_scores[cat] = []
            cat_scores[cat].append(att['percentage'])
            
        category_mastery = {}
        for cat, scores in cat_scores.items():
            category_mastery[cat] = round(sum(scores) / len(scores), 1)
            
        db.users.update_one({'_id': session['user_id']}, {
            '$set': {
                'stats': {
                    'quizzes_taken': total_taken,
                    'average_score': round(avg_score, 1),
                    'total_points': user.get('stats', {}).get('total_points', 0) + int(score * 10),
                    'category_mastery': category_mastery
                }
            }
        })
        
    # Update Leaderboard Entry
    # Store high score for the user on this specific quiz
    existing_lb = db.leaderboard.find_one({'user_id': session['user_id'], 'quiz_id': quiz_id})
    if not existing_lb or existing_lb['score'] < score or (existing_lb['score'] == score and existing_lb['time_taken'] > time_taken):
        lb_entry = {
            'user_id': session['user_id'],
            'username': session['username'],
            'quiz_id': quiz_id,
            'quiz_title': quiz['title'],
            'quiz_category': quiz['category'],
            'score': score,
            'total_questions': total_questions,
            'percentage': round(percentage, 1),
            'time_taken': time_taken,
            'created_at': datetime.datetime.now().isoformat()
        }
        if existing_lb:
            db.leaderboard.update_one({'_id': existing_lb['_id']}, {'$set': lb_entry})
        else:
            lb_entry['_id'] = str(uuid.uuid4())
            db.leaderboard.insert_one(lb_entry)
            
    return jsonify({
        'success': True,
        'attempt_id': attempt_id
    })

# Quiz Results Page
@app.route('/attempt/<attempt_id>')
@login_required
def quiz_result(attempt_id):
    attempt = db.attempts.find_one({'_id': attempt_id})
    if not attempt or attempt['user_id'] != session['user_id']:
        flash("Attempt record not found.", "danger")
        return redirect(url_for('dashboard'))
        
    quiz = db.quizzes.find_one({'_id': attempt['quiz_id']})
    if not quiz:
        flash("Quiz not found.", "danger")
        return redirect(url_for('dashboard'))
        
    return render_template('quiz_result.html', attempt=attempt, quiz=quiz)

# Create Quiz Form
@app.route('/quiz/create', methods=['GET', 'POST'])
@login_required
def quiz_create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip() or "General"
        difficulty = request.form.get('difficulty', 'Medium')
        time_limit = request.form.get('time_limit', '0')
        
        try:
            time_limit = int(time_limit)
        except ValueError:
            time_limit = 0
            
        # Parse questions from form fields
        questions = []
        q_indices = sorted(list(set(
            k.split('_')[1] for k in request.form.keys() if k.startswith('qtext_')
        )))
        
        for idx in q_indices:
            qtext = request.form.get(f'qtext_{idx}', '').strip()
            if not qtext:
                continue
                
            options = [
                request.form.get(f'qopt_{idx}_0', '').strip(),
                request.form.get(f'qopt_{idx}_1', '').strip(),
                request.form.get(f'qopt_{idx}_2', '').strip(),
                request.form.get(f'qopt_{idx}_3', '').strip()
            ]
            
            correct = request.form.get(f'qcorrect_{idx}', '0')
            try:
                correct = int(correct)
            except ValueError:
                correct = 0
                
            explanation = request.form.get(f'qexp_{idx}', '').strip()
            
            questions.append({
                'text': qtext,
                'options': options,
                'correct_option': correct,
                'explanation': explanation
            })
            
        if not title or len(questions) == 0:
            flash("Title and at least one valid question are required.", "danger")
            return redirect(url_for('quiz_create'))
            
        quiz_id = str(uuid.uuid4())
        new_quiz = {
            '_id': quiz_id,
            'title': title,
            'description': description,
            'category': category,
            'difficulty': difficulty,
            'time_limit': time_limit,
            'creator_id': session['user_id'],
            'creator_name': session['username'],
            'questions': questions,
            'created_at': datetime.datetime.now().isoformat()
        }
        
        db.quizzes.insert_one(new_quiz)
        flash("Quiz created successfully!", "success")
        return redirect(url_for('dashboard'))
        
    return render_template('quiz_create.html')

# Leaderboard
@app.route('/leaderboard')
def leaderboard():
    category = request.args.get('category', '')
    
    query = {}
    if category:
        query['quiz_category'] = category
        
    # Get entries sorted by percentage (descending) and time_taken (ascending)
    lb_entries = db.leaderboard.find(query)
    
    # Sort in Python to handle composite keys correctly across MongoDB and Fallback
    lb_entries.sort(key=lambda x: (x.get('percentage', 0), -x.get('time_taken', 999999)), reverse=True)
    
    # Keep top 20
    top_entries = lb_entries[:20]
    
    # Get all categories for filter
    categories = sorted(list(set(q.get('category') for q in db.quizzes.find() if q.get('category'))))
    
    return render_template('leaderboard.html', entries=top_entries, categories=categories, selected_category=category)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
