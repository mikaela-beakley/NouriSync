from flask import Flask, render_template, request, redirect, jsonify
import json
import os
from datetime import datetime, timedelta
from DailyLogFormatter import DailyFormatter
from DailyLogAI import DailyLogAI
from EmotionAI import EmotionAI

app = Flask(__name__)

# this is where we will hold the patient data for now
temp_patient_data = {}

def llm_call(data, debug):
    """
    fake LLM function that returns structured response
    this will connect to the LLM jay working on + Jas model too
    """

    if debug == True:
        #Mock response based on the input data
        patient_data = data.get('patient_input', {})
        caregiver_data = data.get('caregiver_input', {})

        # Simple risk assessment based on form responses
        emotions_list = ["extremly happy", "depressed"]
        risk_score = "low"
        risk_factors = []
        
        # Check patient mood (scale-question-1)
        patient_mood = int(patient_data.get('scale-question-1', 2))
        if patient_mood <= 1:
            risk_score = "medium"
            risk_factors.append("Low mood reported")
        
        # Check patient support feeling (scale-question-2)
        patient_support = int(patient_data.get('scale-question-2', 2))
        if patient_support <= 1:
            risk_score = "medium"
            risk_factors.append("Low support feeling")
        
        # Check recovery readiness
        recovery_ready = float(patient_data.get('recover-ready', 5))
        if recovery_ready <= 3:
            risk_score = "medium"
            risk_factors.append("Low recovery motivation")
        
        # Check caregiver meal observation
        meals_eaten = int(caregiver_data.get('scale-question-1', 2))
        if meals_eaten <= 1:
            risk_score = "high"
            risk_factors.append("Meal completion < 50%")
        
        # If no specific risk factors, add default
        if not risk_factors:
            risk_factors.append("Regular monitoring indicated")
        
        # Generate plan based on risk assessment
        plan = []
        
        if risk_score == "high":
            plan.extend([
                {
                    "step": "Full meal supervision (≥30 min).",
                    "rationale": "Reduces post-meal purge attempts.",
                    "source": "Lock et al., *J Adol Health*, 2020"
                },
                {
                    "step": "No bathroom alone for 1 h after meals.",
                    "rationale": "Limits compensatory behaviours.",
                    "source": "NICE Guideline NG69"
                },
                {
                    "step": "Contact clinician if HR < 50 bpm.",
                    "rationale": "Bradycardia threshold for ED readmit.",
                    "source": "SAHM Position Paper, 2018"
                }
            ])
        elif risk_score == "medium":
            plan.extend([
                {
                    "step": "Check in every 2 hours during meal times.",
                    "rationale": "Regular monitoring prevents escalation.",
                    "source": "FBT Guidelines, 2019"
                },
                {
                    "step": "Encourage engagement in planned activities.",
                    "rationale": "Structured activities reduce rumination.",
                    "source": "CBT-E Manual, 2016"
                }
            ])
        else:
            plan.extend([
                {
                    "step": "Continue regular meal support.",
                    "rationale": "Maintain positive momentum in recovery.",
                    "source": "Recovery-oriented care principles"
                },
                {
                    "step": "Celebrate small wins together.",
                    "rationale": "Positive reinforcement enhances motivation.",
                    "source": "Behavioral therapy principles"
                }
            ])
        
        
        return {
            "emotions_list": emotions_list,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "plan": plan
        }
    else:
        #real llm
        Formatter = DailyFormatter(data)
        combined = Formatter.format()
        patient = Formatter.patient_format()
        
        #get mood from mood
        EmotionCooker = EmotionAI()
        emotions = EmotionCooker.get_emotions(data.get('patient_input').get('day-description'))

        DailyAI = DailyLogAI()
        response = DailyAI.queryLLM(combined, emotions)
        return json.loads(response)

def load_logs():
    """load existing logs from logs.json file"""
    # Get the directory where server.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to web/, then into data/
    logs_path = os.path.join(script_dir, '..', 'data', 'logs.json')
    logs_path = os.path.abspath(logs_path)  # Convert to absolute path
    
    try:
        if os.path.exists(logs_path):
            with open(logs_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading logs: {e}")
        return []

def save_logs(logs):
    """save logs to logs.json file"""
    # Get the directory where server.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to web/, then into data/
    logs_path = os.path.join(script_dir, '..', 'data', 'logs.json')
    logs_path = os.path.abspath(logs_path)  # Convert to absolute path
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(logs_path), exist_ok=True)
        
        print(f"Saving logs to: {logs_path}")  # Debug print
        
        with open(logs_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError) as e:
        print(f"Error saving logs: {e}")
        return False

def calculate_streak(logs):
    """Calculate current streak based on log dates"""
    if not logs:
        return {
            'current_streak': 0,
            'logged_today': False,
            'last_7_days': [False] * 7
        }
    
    # Sort logs by timestamp (newest first)
    sorted_logs = sorted(logs, key=lambda x: datetime.strptime(x['timestamp'], "%m/%d/%Y - %I:%M %p"), reverse=True)
    
    # Get today's date
    today = datetime.now().date()
    
    # Check if logged today
    logged_today = False
    if sorted_logs:
        latest_log_date = datetime.strptime(sorted_logs[0]['timestamp'], "%m/%d/%Y - %I:%M %p").date()
        logged_today = latest_log_date == today
    
    # Calculate streak
    current_streak = 0
    check_date = today if logged_today else today - timedelta(days=1)
    
    # Create set of log dates for faster lookup
    log_dates = set()
    for log in logs:
        log_date = datetime.strptime(log['timestamp'], "%m/%d/%Y - %I:%M %p").date()
        log_dates.add(log_date)
    
    # Count consecutive days
    while check_date in log_dates:
        current_streak += 1
        check_date -= timedelta(days=1)
    
    # Get last 7 days status (Sunday to Saturday, with today being positioned correctly)
    last_7_days = []
    today_weekday = today.weekday()  # 0=Monday, 6=Sunday
    
    # Calculate how many days back to go to get to last Sunday
    days_since_sunday = (today_weekday + 1) % 7
    last_sunday = today - timedelta(days=days_since_sunday)
    
    # Fill in the 7 days from Sunday to Saturday
    for i in range(7):
        check_day = last_sunday + timedelta(days=i)
        last_7_days.append(check_day in log_dates)
    
    return {
        'current_streak': current_streak,
        'logged_today': logged_today,
        'last_7_days': last_7_days
    }

#better route labels added
@app.route("/", methods=['GET'])
def index():
    """Index route"""
    return render_template('index.html')

@app.route("/questionnaire", methods=['GET'])
def questionnaire():
    """Questionnaire route"""
    return render_template('questionnaire.html')
# removed the get part of the route bc not needed here
@app.route("/questionnaire-patient-info", methods=['POST'])
def post_patient_answers():
    """
    Handle patient form submission - store temporarily in memory
    """
    form_answers = request.form
    print(form_answers)
    try:
        # Get all form data
        patient_data = {
            'scale-question-1': form_answers.get('scale-question-1'),
            'scale-question-2': form_answers.get('scale-question-2'),
            'tough-time': form_answers.get('tough-time', ''),
            'day-description': form_answers.get('day-description', ''),
            'caregiver-helpful': form_answers.get('caregiver-helpful', ''),
            'caregiver-unhelpful': form_answers.get('caregiver-unhelpful', ''),
            'recover-ready': form_answers.get('recover-ready'),
            'comments': form_answers.get('comments', '')
        }
        
        # Store in temporary memory (in production, you might want to use session ID)
        temp_patient_data['latest'] = patient_data
        
        print("Patient data stored temporarily:", patient_data)
        
        # For now, redirect back to questionnaire
        # In a real app, you might want to show a "waiting for caregiver" message
        return redirect("/questionnaire?phase=2")
        
    except Exception as e:
        print(f"Error processing patient data: {e}")
        return jsonify({"error": "Failed to process patient data"}), 500

# since we got the forms split up the patient one jus stores it in memory, then we process everything here after caregiver finishes answering
@app.route("/questionnaire-caregiver-info", methods=['POST'])
def post_caregiver_answers():
    """
    Handle caregiver form submission - combine with patient data and process
    """
    form_answers = request.form
    try:
        # Get caregiver form data
        caregiver_data = {
            'patient-meal-completion': form_answers.get('scale-question-1'),
            'loved-one-needs': form_answers.get('scale-question-2'),
            'avoided-food': form_answers.get('avoided-food', ''),
            'caloric-intake': form_answers.get('caloric-intake', ''),
            'comments': form_answers.get('comments', '')
        }
        
        # Check if we have patient data
        if 'latest' not in temp_patient_data:
            return jsonify({"error": "No patient data found. Patient must submit first."}), 400
        
        patient_data = temp_patient_data['latest']
        
        # Combine patient and caregiver data
        combined_data = {
            'patient_input': patient_data,
            'caregiver_input': caregiver_data
        }
        
        print("Combined data:", combined_data)
        
        # Load existing logs
        logs = load_logs()
        print(f"Loaded {len(logs)} existing logs")
        
        # Call LLM function

        #FALSE for real LLM, TRUE for debug test
        ai_response = llm_call(combined_data, False)
        
        # Create complete log entry
        timestamp = datetime.now().strftime("%m/%d/%Y - %I:%M %p")
        log_entry = {
            'id': len(logs) + 1,
            'timestamp': timestamp,
            'patient_input': patient_data,
            'caregiver_input': caregiver_data,
            'ai_response': ai_response
        }
        
        # Add to logs
        logs.append(log_entry)
        print(f"Created log entry with ID: {log_entry['id']}")
        
        # Save logs
        if not save_logs(logs):
            return jsonify({"error": "Failed to save log entry"}), 500
        
        print(f"Successfully saved {len(logs)} logs")
        
        # Clear temporary patient data
        temp_patient_data.pop('latest', None)
        
        print("Log entry saved successfully")
        
        # Return AI response as JSON (just for testing, to see the response)
        #return jsonify(ai_response)
        # Redirect back to home page to see the new log
        return redirect("/")
        
    except Exception as e:
        print(f"Error processing caregiver data: {e}")
        return jsonify({"error": "Failed to process caregiver data"}), 500

@app.route("/logs", methods=['GET'])
def get_logs():
    """
    GET endpoint to retrieve all log entries
    """
    try:
        logs = load_logs()
        return jsonify(logs)
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return jsonify({"error": "Failed to retrieve logs"}), 500

@app.route("/streak", methods=['GET'])
def get_streak():
    """
    GET endpoint to retrieve streak information
    """
    try:
        logs = load_logs()
        streak_data = calculate_streak(logs)
        return jsonify(streak_data)
    except Exception as e:
        print(f"Error retrieving streak data: {e}")
        return jsonify({"error": "Failed to retrieve streak data"}), 500

@app.route("/date", methods=['GET'])

def get_date_format():
    moment = Moment(app)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)