class DailyFormatter:

    """
    Daily Format:

    Patient's Response:
    
    Patient's current feeling:
    How supported the patient feels:
    A time during the day the patient found tough:
    Something the caregiver does that is helpful:
    Something the caregiver could work on:
    Patients Readiness for recovery on a scale of 1-10:

    Caregiver Response:
    The patient ate their required meals: 
    What the patient might need from the caregiver:

    Additional Comments:
     
    """

    def __init__(self, combined_data):
        self.combined_data = combined_data

    def get_feeling(self, number):
        match number:
            case 0:
                return "Very Sad"
            case 1:
                return "Somewhat Sad"
            case 2:
                return "Neutral"
            case 3:
                return "Somewhat Happy"
            case 4:
                return "Very Happy"
            case _:
                return "Invalid input"

    def get_support(self, number):
        match number:
            case 0:
                return "Not at all supported"
            case 1:
                return "A little supported"
            case 2:
                return "Netural"
            case 3:
                return "Mostly supported"
            case 4:
                return "Completely Supported"
            case _:
                return "Invalid input"

    def get_required_meals(self, number):
        match number:
            case 0:
                return "Strongly disagree"
            case 1:
                return "Somewhat disagree"
            case 2:
                return "Netural"
            case 3:
                return "Somewhat agree"
            case 4:
                return "Strongly agree"
            case _:
                return "Invalid input"


    def patient_format(self):
        data = self.combined_data
        patient_data = data.get('patient_input', {})
        patient_format = f"""
        Patient Answers:
        Patient's current feeling: {self.get_feeling(int(patient_data.get('how-are-you-feeling')))}
        How supported the patient feels: {self.get_support(int(patient_data.get('how-supported-do-you-feel')))}
        A time during the day the patient found tough: {patient_data.get('tough-time')}
        Something the caregiver does that is helpful: {patient_data.get('caregiver-helpful')}
        Something the caregiver could work on: {patient_data.get('caregiver-unhelpful')}
        Patients Readiness for recovery on a scale of 1-10: {patient_data.get('recover-ready')}
        Additional comments from the patient: {patient_data.get('comments')}
        """
        return patient_format

    def caregiver_format(self):
        data = self.combined_data
        caregiver_data = data.get('caregiver_input', {})
        caregiver_format = f"""
        Caregiver Answers: 
        The patient ate their required meals: {self.get_required_meals(int(caregiver_data.get('patient-meal-completion')))}
        What the patient might need from the caregiver: {caregiver_data.get('loved-one-needs')}
        Additional comments from the caregiver: {caregiver_data.get('comments')}
        """
        return caregiver_format
    
    def format(self):
        return self.patient_format() + "\n" + self.caregiver_format()