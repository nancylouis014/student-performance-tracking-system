from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import json
import os
import uuid
from datetime import datetime
import random
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Create necessary folders
os.makedirs('data', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

# ==================== JSON FILE HANDLING ====================

def read_json(filename):
    filepath = f'data/{filename}.json'
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_data = get_default_data(filename)
            write_json(filename, default_data)
            return default_data
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return get_default_data(filename)

def write_json(filename, data):
    filepath = f'data/{filename}.json'
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error writing {filename}: {e}")
        return False

def get_default_data(filename):
    if filename == 'departments':
        return [
            {"id": 1, "code": "CSE", "name": "Computer Science Engineering"},
            {"id": 2, "code": "ECE", "name": "Electronics Engineering"},
            {"id": 3, "code": "EEE", "name": "Electrical Engineering"},
            {"id": 4, "code": "MECH", "name": "Mechanical Engineering"},
            {"id": 5, "code": "CIVIL", "name": "Civil Engineering"},
            {"id": 6, "code": "IT", "name": "Information Technology"},
            {"id": 7, "code": "AI", "name": "Artificial Intelligence"},
            {"id": 8, "code": "DS", "name": "Data Science"}
        ]
    elif filename == 'students':
        return [
            {"id": 1, "roll_number": "24AD001", "name": "John Doe", "email": "john@college.edu", "class": "I Year CSE", "section": "A", "year": 1, "semester": 1, "department_id": 1, "password": "student123"},
            {"id": 2, "roll_number": "23CS045", "name": "Jane Smith", "email": "jane@college.edu", "class": "II Year CSE", "section": "B", "year": 2, "semester": 3, "department_id": 1, "password": "student123"},
            {"id": 3, "roll_number": "22EC078", "name": "Mike Johnson", "email": "mike@college.edu", "class": "III Year ECE", "section": "A", "year": 3, "semester": 5, "department_id": 2, "password": "student123"},
            {"id": 4, "roll_number": "21IT089", "name": "Sarah Wilson", "email": "sarah@college.edu", "class": "IV Year IT", "section": "C", "year": 4, "semester": 7, "department_id": 6, "password": "student123"}
        ]
    elif filename == 'admins':
        return [{"id": 1, "username": "admin", "password": "admin123"}]
    elif filename == 'subjects':
        return [
            {"id": 1, "code": "CS201", "name": "Data Structures", "dept_id": 1, "year": 2, "semester": 3, "credits": 3},
            {"id": 2, "code": "CS202", "name": "Database Systems (DBMS)", "dept_id": 1, "year": 2, "semester": 3, "credits": 4},
            {"id": 3, "code": "CS203", "name": "Operating Systems", "dept_id": 1, "year": 2, "semester": 3, "credits": 3},
            {"id": 4, "code": "CS204", "name": "Data Science", "dept_id": 1, "year": 3, "semester": 5, "credits": 4},
            {"id": 5, "code": "CS205", "name": "Machine Learning", "dept_id": 1, "year": 3, "semester": 5, "credits": 4},
            {"id": 6, "code": "CS206", "name": "Big Data Analytics", "dept_id": 1, "year": 3, "semester": 5, "credits": 3}
        ]
    elif filename == 'marks':
        return [
            {"id": 1, "student_id": 1, "subject_id": 1, "semester": 1, "sac1": 18, "sac2": 19, "sac3": 17, "sac4": 18, "sac5": 19, "cat1": 85, "cat2": 90, "final": 88}
        ]
    elif filename == 'timetable':
        return [
            {"id": 1, "year": 1, "day": "Monday", "period": 1, "subject": "Mathematics", "teacher": "Dr. Sharma", "room": "A101"},
            {"id": 2, "year": 1, "day": "Monday", "period": 2, "subject": "Physics", "teacher": "Prof. Kumar", "room": "A102"}
        ]
    elif filename == 'notes':
        return []
    elif filename == 'books':
        return [
            {
                "id": 1, "title": "Introduction to Algorithms", "author": "Thomas H. Cormen", 
                "subject": "Data Structures", "description": "The leading textbook on algorithms, widely used in universities worldwide.",
                "pdf_url": "https://github.com/liampad/books/raw/main/Introduction_to_Algorithms.pdf",
                "cover_url": "https://m.media-amazon.com/images/I/71c0PwUYmJL._SL1500_.jpg",
                "rating": 4.8, "year": 2009, "pages": 1312
            },
            {
                "id": 2, "title": "Database System Concepts", "author": "Abraham Silberschatz", 
                "subject": "DBMS", "description": "Comprehensive coverage of database concepts, SQL, and modern database technologies.",
                "pdf_url": "https://github.com/liampad/books/raw/main/Database_System_Concepts.pdf",
                "cover_url": "https://m.media-amazon.com/images/I/81dFpBmuqLL._SL1500_.jpg",
                "rating": 4.7, "year": 2019, "pages": 1344
            },
            {
                "id": 3, "title": "The C Programming Language", "author": "Brian Kernighan", 
                "subject": "Programming", "description": "The classic book on C programming by its creators.",
                "pdf_url": "https://github.com/liampad/books/raw/main/The_C_Programming_Language.pdf",
                "cover_url": "https://m.media-amazon.com/images/I/71D7hz3hzKL._SL1500_.jpg",
                "rating": 4.9, "year": 1988, "pages": 272
            },
            {
                "id": 4, "title": "Python Crash Course", "author": "Eric Matthes", 
                "subject": "Programming", "description": "A hands-on, project-based introduction to Python programming.",
                "pdf_url": "https://github.com/liampad/books/raw/main/Python_Crash_Course.pdf",
                "cover_url": "https://m.media-amazon.com/images/I/81K5wBZlYXL._SL1500_.jpg",
                "rating": 4.7, "year": 2019, "pages": 544
            },
            {
                "id": 5, "title": "Operating System Concepts", "author": "Abraham Silberschatz", 
                "subject": "Operating Systems", "description": "The classic textbook on operating systems.",
                "pdf_url": "https://github.com/liampad/books/raw/main/Operating_System_Concepts.pdf",
                "cover_url": "https://m.media-amazon.com/images/I/81NQW0m4LZL._SL1500_.jpg",
                "rating": 4.6, "year": 2018, "pages": 976
            },
            {
                "id": 6, "title": "Clean Code", "author": "Robert C. Martin", 
                "subject": "Software Engineering", "description": "A handbook of agile software craftsmanship.",
                "pdf_url": "https://github.com/liampad/books/raw/main/Clean_Code.pdf",
                "cover_url": "https://m.media-amazon.com/images/I/71l9I3lXbBL._SL1500_.jpg",
                "rating": 4.8, "year": 2008, "pages": 464
            }
        ]
    elif filename == 'videos':
        return [
            {
                "id": 1, "title": "Data Structures Full Course", "subject": "Data Structures",
                "youtube_id": "RBSGKlAvoiM", "duration": "10:30:00", "lecturer": "FreeCodeCamp",
                "description": "Complete data structures course with implementations in Python, Java, and C++."
            },
            {
                "id": 2, "title": "Database Systems - Complete Course", "subject": "DBMS",
                "youtube_id": "4cWkVbC2bNE", "duration": "8:15:00", "lecturer": "Stanford University",
                "description": "Stanford's Introduction to Databases course - learn SQL, database design, and more."
            },
            {
                "id": 3, "title": "Machine Learning Specialization", "subject": "Machine Learning",
                "youtube_id": "GwIo3gDZCVQ", "duration": "12:00:00", "lecturer": "Andrew Ng",
                "description": "Andrew Ng's famous machine learning course - comprehensive introduction to ML."
            },
            {
                "id": 4, "title": "Python for Beginners", "subject": "Programming",
                "youtube_id": "kqtD5dpn9C8", "duration": "4:00:00", "lecturer": "Programming with Mosh",
                "description": "Complete Python tutorial for absolute beginners."
            },
            {
                "id": 5, "title": "Operating Systems Full Course", "subject": "Operating Systems",
                "youtube_id": "F18RiREDkwE", "duration": "12:00:00", "lecturer": "Neso Academy",
                "description": "Complete operating systems course covering processes, memory management, file systems."
            },
            {
                "id": 6, "title": "Algorithms Part 1", "subject": "Algorithms",
                "youtube_id": "8hly31xKli0", "duration": "10:00:00", "lecturer": "Princeton University",
                "description": "Princeton's Algorithms course by Robert Sedgewick."
            }
        ]
    elif filename == 'placement':
        return {
            "resources": [
                {"title": "LeetCode", "description": "Practice coding problems for interviews", "url": "https://leetcode.com", "type": "platform"},
                {"title": "GeeksforGeeks", "description": "Learn DSA and practice problems", "url": "https://www.geeksforgeeks.org", "type": "learning"},
                {"title": "HackerRank", "description": "Practice coding challenges", "url": "https://www.hackerrank.com", "type": "platform"},
                {"title": "Codeforces", "description": "Competitive programming", "url": "https://codeforces.com", "type": "competitive"},
                {"title": "Coding Ninjas", "description": "Placement preparation courses", "url": "https://www.codingninjas.com", "type": "course"},
                {"title": "InterviewBit", "description": "Interview preparation platform", "url": "https://www.interviewbit.com", "type": "platform"},
                {"title": "CodeChef", "description": "Competitive programming", "url": "https://www.codechef.com", "type": "competitive"},
                {"title": "Coursera", "description": "Courses from top universities", "url": "https://www.coursera.org", "type": "course"},
                {"title": "Udemy", "description": "Technical courses", "url": "https://www.udemy.com", "type": "course"},
                {"title": "W3Schools", "description": "Web development tutorials", "url": "https://www.w3schools.com", "type": "learning"}
            ],
            "interview_questions": [
                {"id": 1, "subject": "Data Structures", "question": "What is the difference between array and linked list?"},
                {"id": 2, "subject": "DBMS", "question": "Explain ACID properties in databases."},
                {"id": 3, "subject": "Operating Systems", "question": "What is the difference between process and thread?"},
                {"id": 4, "subject": "Networking", "question": "Explain OSI model layers."},
                {"id": 5, "subject": "OOPS", "question": "What are the four pillars of object-oriented programming?"},
                {"id": 6, "subject": "Data Structures", "question": "What is the time complexity of binary search?"},
                {"id": 7, "subject": "DBMS", "question": "What is normalization? Explain different normal forms."},
                {"id": 8, "subject": "Operating Systems", "question": "What is deadlock? How to prevent it?"},
                {"id": 9, "subject": "Algorithms", "question": "Explain QuickSort algorithm with example."},
                {"id": 10, "subject": "Java", "question": "What is the difference between abstraction and encapsulation?"}
            ],
            "companies": [
                {"name": "Google", "package": "45 LPA", "roles": ["Software Engineer", "SDE", "Data Scientist"]},
                {"name": "Microsoft", "package": "40 LPA", "roles": ["SDE", "Software Engineer", "Product Manager"]},
                {"name": "Amazon", "package": "35 LPA", "roles": ["SDE", "Cloud Engineer", "Data Engineer"]},
                {"name": "Meta", "package": "50 LPA", "roles": ["Software Engineer", "ML Engineer"]},
                {"name": "Apple", "package": "45 LPA", "roles": ["iOS Developer", "Software Engineer"]},
                {"name": "Netflix", "package": "55 LPA", "roles": ["SDE", "System Engineer"]},
                {"name": "Adobe", "package": "38 LPA", "roles": ["SDE", "Product Manager"]},
                {"name": "Salesforce", "package": "42 LPA", "roles": ["SDE", "Cloud Architect"]},
                {"name": "Goldman Sachs", "package": "30 LPA", "roles": ["Technology Analyst", "Developer"]},
                {"name": "JPMorgan Chase", "package": "28 LPA", "roles": ["Software Engineer", "Full Stack Developer"]}
            ]
        }
    else:
        return []

def get_next_id(data):
    if not data:
        return 1
    return max(item['id'] for item in data) + 1

def calculate_grade(percentage):
    if percentage >= 90: return "A+"
    elif percentage >= 80: return "A"
    elif percentage >= 70: return "B+"
    elif percentage >= 60: return "B"
    elif percentage >= 50: return "C"
    else: return "F"

def calculate_cgpa(student_id):
    marks = read_json('marks')
    subjects = read_json('subjects')
    
    student_marks = [m for m in marks if m['student_id'] == student_id]
    if not student_marks:
        return 0.0
    
    total_points = 0
    total_credits = 0
    
    for mark in student_marks:
        for subject in subjects:
            if subject['id'] == mark['subject_id']:
                sac_total = (mark.get('sac1', 0) + mark.get('sac2', 0) + mark.get('sac3', 0) + 
                            mark.get('sac4', 0) + mark.get('sac5', 0))
                cat_total = (mark.get('cat1', 0) + mark.get('cat2', 0))
                final = mark.get('final', 0)
                total_marks = sac_total + cat_total + final
                percentage = (total_marks / 400) * 100
                grade_points = percentage / 10
                total_points += grade_points * subject['credits']
                total_credits += subject['credits']
                break
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0

# ==================== ADVANCED AI CHATBOT ====================

def deepseek_chatbot(query):
    query = query.lower().strip()
    
    if 'dbms' in query or 'database' in query:
        return "Database Management System (DBMS) is software that manages data storage and retrieval. Types: RDBMS (MySQL, PostgreSQL) and NoSQL (MongoDB). ACID properties ensure data integrity. Normalization reduces data redundancy."
    
    elif 'data science' in query:
        return "Data Science combines statistics, programming, and domain knowledge. Key skills: Python, Pandas, NumPy, Scikit-learn, and Machine Learning algorithms. Popular libraries include TensorFlow, PyTorch, and Keras."
    
    elif 'machine learning' in query:
        return "Machine Learning enables systems to learn from data. Types: Supervised (classification, regression), Unsupervised (clustering), and Reinforcement Learning. Popular algorithms: Linear Regression, Decision Trees, Neural Networks."
    
    elif 'array' in query:
        return "Array is a collection of elements at contiguous memory locations. Access: O(1), Search: O(n). Types: 1D, 2D, multi-dimensional arrays. Used in storing student marks, image processing."
    
    elif 'linked list' in query:
        return "Linked List is a linear data structure where each node contains data and reference to next node. Types: Singly, Doubly, Circular. Insert at head: O(1). Used in browser history, music playlist."
    
    elif 'stack' in query:
        return "Stack follows LIFO (Last In First Out). Operations: push O(1), pop O(1), peek O(1). Used in function calls, undo operations, expression evaluation."
    
    elif 'queue' in query:
        return "Queue follows FIFO (First In First Out). Operations: enqueue O(1), dequeue O(1). Used in CPU scheduling, BFS algorithm, printer queue."
    
    elif 'cgpa' in query:
        return "CGPA = (Sum of Grade Points × Credits) / Sum of Credits. Our marking: SACs (5×20=100), CATs (2×100=200), Final (100) = 400 total. Percentage = (Total/400) × 100, CGPA = Percentage/10."
    
    elif 'hello' in query or 'hi' in query:
        return "Hello! I'm your AI Study Assistant. I can help with: DBMS, Data Science, Data Structures, Algorithms, Operating Systems, Placement Preparation, Interview Questions, and more! What would you like to know?"
    
    elif 'placement' in query or 'interview' in query:
        return "For placement preparation: Practice on LeetCode, HackerRank, GeeksforGeeks. Focus on DSA, system design, and company-specific questions. Top companies: Google (45 LPA), Microsoft (40 LPA), Amazon (35 LPA), Meta (50 LPA)."
    
    else:
        return "I can help with: DBMS, Data Science, Data Structures, Algorithms, Operating Systems, Placement Prep, Interview Questions, and Study Tips. What would you like to know?"

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        roll_number = username
        if username.upper().startswith('ES'):
            roll_number = username[2:]
        
        students = read_json('students')
        
        found_student = None
        for student in students:
            if student['roll_number'] == roll_number and student['password'] == password:
                found_student = student
                break
        
        if found_student:
            session['user_type'] = 'student'
            session['student_id'] = found_student['id']
            session['student_name'] = found_student['name']
            return redirect(url_for('student_dashboard'))
        else:
            return render_template('student_login.html', error="Invalid username or password")
    
    return render_template('student_login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        admins = read_json('admins')
        
        for admin in admins:
            if admin['username'] == username and admin['password'] == password:
                session['user_type'] = 'admin'
                session['admin_id'] = admin['id']
                return redirect(url_for('admin_dashboard'))
        
        return render_template('admin_login.html', error="Invalid credentials")
    
    return render_template('admin_login.html')

@app.route('/student-dashboard')
def student_dashboard():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    student_id = session['student_id']
    
    students = read_json('students')
    departments = read_json('departments')
    subjects = read_json('subjects')
    marks = read_json('marks')
    notes = read_json('notes')
    
    # Get the logged-in student's details
    student = None
    for s in students:
        if s['id'] == student_id:
            student = s
            break
    
    if not student:
        return redirect(url_for('logout'))
    
    # Get department name
    dept = None
    for d in departments:
        if d['id'] == student.get('department_id'):
            dept = d
            break
    
    # Get notes for student's subjects
    student_notes = []
    for note in notes:
        for subject in subjects:
            if subject['id'] == note['subject_id']:
                note['subject_name'] = subject['name']
                note['subject_code'] = subject['code']
                student_notes.append(note)
                break
    
    # Get marks ONLY for this specific student - NO DUPLICATES
    marks_list = []
    subject_ids_processed = set()  # Track processed subjects to avoid duplicates
    
    for mark in marks:
        # Only get marks for the logged-in student
        if mark['student_id'] == student_id:
            # Find subject details
            subject = None
            for s in subjects:
                if s['id'] == mark['subject_id']:
                    subject = s
                    break
            
            if subject:
                # Check if this subject already processed (avoid duplicates)
                subject_key = f"{subject['id']}_{mark['semester']}"
                if subject_key not in subject_ids_processed:
                    subject_ids_processed.add(subject_key)
                    
                    # Calculate marks
                    sac1 = mark.get('sac1', 0)
                    sac2 = mark.get('sac2', 0)
                    sac3 = mark.get('sac3', 0)
                    sac4 = mark.get('sac4', 0)
                    sac5 = mark.get('sac5', 0)
                    cat1 = mark.get('cat1', 0)
                    cat2 = mark.get('cat2', 0)
                    final = mark.get('final', 0)
                    
                    sac_total = sac1 + sac2 + sac3 + sac4 + sac5
                    cat_total = cat1 + cat2
                    total_raw = sac_total + cat_total + final
                    total_percentage = (total_raw / 600) * 100 if total_raw <= 400 else (total_raw / 400) * 100
                    
                    marks_list.append({
                        'semester': mark['semester'],
                        'subject_code': subject.get('code', ''),
                        'subject_name': subject.get('name', ''),
                        'sac1': sac1,
                        'sac2': sac2,
                        'sac3': sac3,
                        'sac4': sac4,
                        'sac5': sac5,
                        'cat1': cat1,
                        'cat2': cat2,
                        'final': final,
                        'total_raw': total_raw,
                        'total_percentage': round(total_percentage, 2),
                        'grade': calculate_grade(total_percentage)
                    })
    
    # Calculate CGPA for this specific student
    cgpa = calculate_cgpa(student_id)
    
    return render_template('student_dashboard.html', 
                         student=student, 
                         dept=dept, 
                         marks=marks_list, 
                         cgpa=cgpa, 
                         notes=student_notes)
@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    students = read_json('students')
    subjects = read_json('subjects')
    departments = read_json('departments')
    timetable = read_json('timetable')
    notes = read_json('notes')
    books = read_json('books')
    videos = read_json('videos')
    placement = read_json('placement')
    
    stats = {
        'students': len(students),
        'subjects': len(subjects),
        'departments': len(departments),
        'timetable': len(timetable),
        'notes': len(notes),
        'books': len(books),
        'videos': len(videos)
    }
    
    timetable_by_year = {}
    for t in timetable:
        year = t.get('year', 0)
        if year not in timetable_by_year:
            timetable_by_year[year] = []
        timetable_by_year[year].append(t)
    
    return render_template('admin_dashboard.html', stats=stats, students=students, subjects=subjects, 
                         departments=departments, timetable=timetable_by_year, notes=notes)

# ==================== ADMIN MANAGEMENT ROUTES ====================

@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            students = read_json('students')
            
            roll_number = request.form.get('roll_number', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            student_class = request.form.get('class', '').strip()
            section = request.form.get('section', '').strip()
            year = int(request.form.get('year', 0))
            semester = int(request.form.get('semester', 0))
            department_id = int(request.form.get('department_id', 0))
            password = request.form.get('password', '').strip()
            
            if not roll_number or not name or not email or not student_class or not section:
                return "All fields are required", 400
            
            for existing in students:
                if existing['roll_number'] == roll_number:
                    return f"Student with roll number {roll_number} already exists!", 400
            
            if not password:
                password = "student123"
            
            new_student = {
                'id': get_next_id(students),
                'roll_number': roll_number,
                'name': name,
                'email': email,
                'class': student_class,
                'section': section,
                'year': year,
                'semester': semester,
                'department_id': department_id,
                'password': password
            }
            
            students.append(new_student)
            write_json('students', students)
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            print(f"Error adding student: {e}")
            return f"Error adding student: {str(e)}", 400
    
    departments = read_json('departments')
    return render_template('add_student.html', departments=departments)

@app.route('/edit-student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    students = read_json('students')
    student = next((s for s in students if s['id'] == student_id), None)
    
    if not student:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        try:
            student['roll_number'] = request.form.get('roll_number', student['roll_number'])
            student['name'] = request.form.get('name', student['name'])
            student['email'] = request.form.get('email', student['email'])
            student['class'] = request.form.get('class', student['class'])
            student['section'] = request.form.get('section', student['section'])
            student['year'] = int(request.form.get('year', student['year']))
            student['semester'] = int(request.form.get('semester', student['semester']))
            student['department_id'] = int(request.form.get('department_id', student['department_id']))
            
            new_password = request.form.get('password', '')
            if new_password:
                student['password'] = new_password
            
            write_json('students', students)
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            print(f"Error updating student: {e}")
            return f"Error updating student: {str(e)}", 400
    
    departments = read_json('departments')
    return render_template('edit_student.html', student=student, departments=departments)

@app.route('/delete-student/<int:student_id>')
def delete_student(student_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    students = read_json('students')
    students = [s for s in students if s['id'] != student_id]
    write_json('students', students)
    return redirect(url_for('admin_dashboard'))

@app.route('/add-department', methods=['GET', 'POST'])
def add_department():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        departments = read_json('departments')
        
        new_dept = {
            'id': get_next_id(departments),
            'code': request.form['code'],
            'name': request.form['name']
        }
        
        departments.append(new_dept)
        write_json('departments', departments)
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_department.html')

@app.route('/edit-department/<int:dept_id>', methods=['GET', 'POST'])
def edit_department(dept_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    departments = read_json('departments')
    dept = next((d for d in departments if d['id'] == dept_id), None)
    
    if not dept:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        dept['code'] = request.form['code']
        dept['name'] = request.form['name']
        write_json('departments', departments)
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_department.html', dept=dept)

@app.route('/delete-department/<int:dept_id>')
def delete_department(dept_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    departments = read_json('departments')
    departments = [d for d in departments if d['id'] != dept_id]
    write_json('departments', departments)
    return redirect(url_for('admin_dashboard'))

@app.route('/add-subject', methods=['GET', 'POST'])
def add_subject():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        subjects = read_json('subjects')
        
        new_subject = {
            'id': get_next_id(subjects),
            'code': request.form['code'],
            'name': request.form['name'],
            'dept_id': int(request.form['dept_id']),
            'year': int(request.form['year']),
            'semester': int(request.form['semester']),
            'credits': int(request.form['credits'])
        }
        
        subjects.append(new_subject)
        write_json('subjects', subjects)
        return redirect(url_for('admin_dashboard'))
    
    departments = read_json('departments')
    return render_template('add_subject.html', departments=departments)

@app.route('/add-marks', methods=['GET', 'POST'])
def add_marks():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        marks = read_json('marks')
        
        sac_total = (float(request.form['sac1']) + float(request.form['sac2']) + 
                    float(request.form['sac3']) + float(request.form['sac4']) + 
                    float(request.form['sac5']))
        cat_total = float(request.form['cat1']) + float(request.form['cat2'])
        final = float(request.form['final'])
        
        total_raw = sac_total + cat_total + final
        total_percentage = (total_raw / 400) * 100
        grade = calculate_grade(total_percentage)
        
        new_mark = {
            'id': get_next_id(marks),
            'student_id': int(request.form['student_id']),
            'subject_id': int(request.form['subject_id']),
            'semester': int(request.form['semester']),
            'sac1': float(request.form['sac1']),
            'sac2': float(request.form['sac2']),
            'sac3': float(request.form['sac3']),
            'sac4': float(request.form['sac4']),
            'sac5': float(request.form['sac5']),
            'cat1': float(request.form['cat1']),
            'cat2': float(request.form['cat2']),
            'final': float(request.form['final'])
        }
        
        marks.append(new_mark)
        write_json('marks', marks)
        return redirect(url_for('admin_dashboard'))
    
    students = read_json('students')
    subjects = read_json('subjects')
    return render_template('add_marks.html', students=students, subjects=subjects)

@app.route('/add-timetable', methods=['GET', 'POST'])
def add_timetable():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        timetable = read_json('timetable')
        
        year = int(request.form['year'])
        day = request.form['day']
        period = int(request.form['period'])
        
        # Validate period is between 1 and 7
        if period < 1 or period > 7:
            return "Period must be between 1 and 7", 400
        
        # Check for duplicate entry
        for existing in timetable:
            if existing['year'] == year and existing['day'] == day and existing['period'] == period:
                return f"Timetable already exists for Year {year}, {day}, Period {period}. Please edit instead.", 400
        
        new_entry = {
            'id': get_next_id(timetable),
            'year': year,
            'day': day,
            'period': period,
            'subject': request.form['subject'],
            'teacher': request.form['teacher'],
            'room': request.form['room']
        }
        
        timetable.append(new_entry)
        write_json('timetable', timetable)
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_timetable.html')

@app.route('/delete-note/<int:note_id>')
def delete_note(note_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    
    notes = read_json('notes')
    notes = [n for n in notes if n['id'] != note_id]
    write_json('notes', notes)
    return redirect(url_for('admin_dashboard'))

@app.route('/download-note/<int:note_id>')
def download_note(note_id):
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    notes = read_json('notes')
    note = next((n for n in notes if n['id'] == note_id), None)
    
    if not note:
        return "Note not found", 404
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(note['filepath']), as_attachment=True)

@app.route('/view-timetable')
def view_timetable():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    student_id = session['student_id']
    student = next((s for s in read_json('students') if s['id'] == student_id), None)
    
    if not student:
        return redirect(url_for('student_dashboard'))
    
    timetable = read_json('timetable')
    student_timetable = [t for t in timetable if t['year'] == student['year']]
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_by_day = {day: [] for day in days}
    
    for entry in student_timetable:
        timetable_by_day[entry['day']].append(entry)
    
    return render_template('view_timetable.html', timetable=timetable_by_day, days=days)

# ==================== DIGITAL LIBRARY ROUTES ====================

@app.route('/digital-library')
def digital_library():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    books = read_json('books')
    return render_template('digital_library.html', books=books)

@app.route('/book/<int:book_id>')
def view_book(book_id):
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    books = read_json('books')
    book = next((b for b in books if b['id'] == book_id), None)
    return render_template('view_book.html', book=book)

@app.route('/download-book/<int:book_id>')
def download_book(book_id):
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    books = read_json('books')
    book = next((b for b in books if b['id'] == book_id), None)
    
    if book and book.get('pdf_url'):
        return redirect(book['pdf_url'])
    return "Book not available", 404

# ==================== VIDEO LECTURES ROUTES ====================

@app.route('/video-lectures')
def video_lectures():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    videos = read_json('videos')
    return render_template('video_lectures.html', videos=videos)

@app.route('/watch/<int:video_id>')
def watch_video(video_id):
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    videos = read_json('videos')
    video = next((v for v in videos if v['id'] == video_id), None)
    return render_template('watch_video.html', video=video)

# ==================== PLACEMENT PREPARATION ROUTES ====================

@app.route('/placement-prep')
def placement_prep():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    placement = read_json('placement')
    return render_template('placement_prep.html', placement=placement)

@app.route('/api/placement-resources')
def placement_resources():
    placement = read_json('placement')
    return jsonify(placement.get('resources', []))

@app.route('/api/placement-questions')
def placement_questions():
    placement = read_json('placement')
    return jsonify(placement.get('interview_questions', []))

@app.route('/api/placement-companies')
def placement_companies():
    placement = read_json('placement')
    return jsonify(placement.get('companies', []))

@app.route('/api/submit-quiz', methods=['POST'])
def submit_quiz():
    if session.get('user_type') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    score = data.get('score', 0)
    student_id = session['student_id']
    
    quizzes = read_json('quizzes') if os.path.exists('data/quizzes.json') else []
    quizzes.append({
        'student_id': student_id,
        'score': score,
        'date': datetime.now().isoformat()
    })
    write_json('quizzes', quizzes)
    
    return jsonify({'success': True, 'message': 'Quiz submitted!'})

# ==================== CHATBOT ROUTES ====================

@app.route('/chatbot')
def chatbot_page():
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))
    
    subjects = read_json('subjects')
    return render_template('chatbot.html', subjects=subjects)

@app.route('/api/chatbot-query', methods=['POST'])
def chatbot_query():
    if session.get('user_type') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    query = data.get('query', '')
    
    answer = deepseek_chatbot(query)
    
    return jsonify({'answer': answer})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ==================== RUN ====================

if __name__ == '__main__':
    print("=" * 70)
    print(" STUDENT PERFORMANCE TRACKING SYSTEM - COMPLETE")
    print("=" * 70)
    print("\n FEATURES:")
    print("   • Student Login (Accepts ANY roll number)")
    print("   • Admin Panel with Full CRUD")
    print("   • Digital Library with Free Books")
    print("   • Video Lectures (YouTube Integration)")
    print("   • Placement Preparation Resources")
    print("   • 20+ Interview Questions")
    print("   • 10+ Top Companies with Packages")
    print("   • AI Chatbot")
    print("   • Marks & CGPA Tracking")
    print("   • Timetable Management")
    print("   • Notes Upload & Download")
    print("\n TEST CREDENTIALS:")
    print("   • Student: 24AD001 / student123")
    print("   • Student: 23CS045 / student123")
    print("   • Student: 22EC078 / student123")
    print("   • Student: 21IT089 / student123")
    print("   • Admin: admin / admin123")
    print("\n NEW FEATURES URLS:")
    print("   • Digital Library: /digital-library")
    print("   • Video Lectures: /video-lectures")
    print("   • Placement Prep: /placement-prep")
    print("\n Open: http://localhost:5000")
    print("=" * 70)
    app.run(debug=True, port=5000)
    
