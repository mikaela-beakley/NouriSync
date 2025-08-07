console.log("questionnaire.js loaded")

const mainQuestionnaireContent = document.getElementById("main-questionnaire-content");

function submitForm(form, path) {
    let http = new XMLHttpRequest();
    http.open('POST', path, true);
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    let params = new FormData(form);
    http.send(params);
    http.onload = function() {
        alert(http.responseText);
    }
}

function createPatientBlock() {
    return `<div class="questionnaire-form-caregiver form-page">
            <a href="/">
                <img src="../static/home.png" alt="home button" class="home-button">
            </a>
            <h1>Patient Questions</h1>
            <form action="/questionnaire-patient-info" method="post" class="questionnaire caregiver-questionnaire">
                <div class="scale-question">
                    <p>How are you feeling today?</p>
                    <input type="radio" name="scale-question-1" id="strongly-disagree" value=0>
                    <label for="strongly-disagree">Very Sad</label>
                    <br>
                    <input type="radio" name="scale-question-1" id="somewhat-disagree" value=1>
                    <label for="somewhat-disagree">Somewhat Sad</label>
                    <br>
                    <input type="radio" name="scale-question-1" id="neutral" value=2>
                    <label for="neutral">Neutral</label>
                    <br>
                    <input type="radio" name="scale-question-1" id="somewhat-agree" value=3>
                    <label for="somewhat-agree">Somewhat Happy</label>
                    <br>
                    <input type="radio" name="scale-question-1" id="strongly-agree" value=4>
                    <label for="strongly-agree">Very Happy</label>
                </div>
                <br>
                <br>
                <div class="scale-question">
                    <p>How supported do you feel by the people around you this week?</p>
                    <input type="radio" name="scale-question-2" id="strongly-disagree" value=0>
                    <label for="strongly-disagree">Not at all supported</label>
                    <br>
                    <input type="radio" name="scale-question-2" id="somewhat-disagree" value=1>
                    <label for="somewhat-disagree">A little supported</label>
                    <br>
                    <input type="radio" name="scale-question-2" id="neutral" value=2>
                    <label for="neutral">Neutral</label>
                    <br>
                    <input type="radio" name="scale-question-2" id="somewhat-agree" value=3>
                    <label for="somewhat-agree">Mostly supported</label>
                    <br>
                    <input type="radio" name="scale-question-2" id="strongly-agree" value=4>
                    <label for="strongly-agree">Completely supported</label>
                </div>
                <br>
                <br>
                <div class="open-question">
                    <label for="tough-time">Please describe a time during the day that felt especially tough.</label>
                    <br>
                    <textarea
                        type="text"
                        id="tough-time"
                        name="tough-time"
                        rows="4"
                        cols="30"
                        placeholder="You can write a few sentences here..."
                    ></textarea>
                </div>
                <br>
                <br>
                <div class="open-question">
                    <label for="day-description">Please describe how your day went :)</label>
                    <br>
                    <textarea
                        type="text"
                        id="day-description" name="day-description"
                        rows="4"
                        cols="30"
                        placeholder="You can write a few sentences here..."
                    ></textarea>
                </div>
                <br>
                <br>
                <div class="open-question">
                    <label for="tough-time">Please describe something that your caregiver does that feels helpful.</label>
                    <br>
                    <textarea
                        type="text"
                        id="caregiver-helpful" name="caregiver-helpful"
                        rows="4"
                        cols="30"
                        placeholder="You can write a few sentences here..."
                    > </textarea>
                </div>
                <br>
                <br>
                <div class="open-question">
                    <label for="tough-time">Please describe something that you want your caregiver to work on.</label>
                    <br>
                    <textarea
                        type="text"
                        id="caregiver-unhelpful" name="caregiver-unhelpful"
                        rows="4"
                        cols="30"
                        placeholder="You can write a few sentences here..."
                    > </textarea>
                </div>
                <br>
                <br>
                <div class="slider-question">
                    <label for="recover-ready">How ready do you feel to continue working on your recovery?</label>
                    <br>
                    Not ready
                    <input type="range" id="recover-ready" name="recover-ready" min="0" max="10" step="0.1">
                    Let's go!
                </div>
                <br>
                <br>
                <div class="open-question">
                    <label for="comments">Is there anything you would like to privately note for the journal?</label>
                    <br>
                    <textarea
                        type="text"
                        id="comments" name="comments" 
                        rows="4"
                        cols="30"
                        placeholder="You can write a few sentences here..."
                    > </textarea>
                </div>
                <br>
                <br>
                <input type="submit" value="I'm done" class="patient-done-button">
            </form>
        </div>`
}

function createCaregiverBlock() {
    return `<div class="questionnaire-form-caregiver">
            <a href="/">
                <img src="../static/home.png" alt="home button" class="home-button">
            </a>
            <h1>Caregiver Questions</h1>
            <form action="/questionnaire-caregiver-info" method="post" class="questionnaire caregiver-questionnaire">
                <div class="scale-question">
                    <p>The patient ate their required meals</p>
                    <input type="radio" name="scale-question-1" id="strongly-disagree" value=0>
                    <label for="strongly-disagree">Strongly Disagree</label>
                    <br>
                    <input type="radio" name="scale-question-1" id="somewhat-disagree" value=1>
                    <label for="somewhat-disagree">Somewhat Disagree</label>
                    <br>
                    <input type="radio" name="scale-question-1" id="neutral" value=2>
                    <label for="neutral">Neutral</label>
                    <br>
                    <input type="radio" name="scale-question-1" id="somewhat-agree" value=3>
                    <label for="somewhat-agree">Somewhat Agree</label>
                    <br>
                    <input type="radio" name="scale-question-1" id="strongly-agree" value=4>
                    <label for="strongly-agree">Strongly Agree</label>
                </div>
                <br>
                <br>
                <div class="scale-question">
                    <p>What do you think your loved one might need from you right now?</p>
                    <input type="radio" name="scale-question-2" id="strongly-disagree" value="Space and patience">
                    <label for="strongly-disagree">Space and patience</label>
                    <br>
                    <input type="radio" name="scale-question-2" id="somewhat-disagree" value="Encouragement and presence">
                    <label for="somewhat-disagree">Encouragement and presence</label>
                    <br>
                    <input type="radio" name="scale-question-2" id="neutral" value="A small positive distraction">
                    <label for="neutral">A small positive distraction</label>
                    <br>
                    <input type="radio" name="scale-question-2" id="somewhat-agree" value="I'm not sure">
                    <label for="somewhat-agree">I'm not sure</label>
                    <br>
                    <input type="radio" name="scale-question-2" id="strongly-agree" value="Other">
                    <label for="strongly-agree">Other</label>
                </div>
                <br>
                <br>
                <div class="open-question">
                    <label for="avoided-food">Is there any particular type of food you've notice the patient avoiding? If so, please explain what it is.</label><br>
                    <textarea
                        type="text"
                        id="avoided-food" name="avoided-food" 
                        rows="4"
                        cols="30"
                        placeholder="You can write a few sentences here..."
                    > </textarea>
                </div>
                <br>
                <br>
                <div class="open-question">
                    <label for="caloric-intake">If you are measuring daily caloric intake, please input what it is for today below.</label><br>
                    <textarea
                        type="number"
                        id="caloric-intake" name="caloric-intake" 
                        rows="4"
                        cols="30"
                        placeholder="You can write a few sentences here..."
                    > </textarea>
                </div>
                <br>
                <br>
                <div class="open-question">
                    <label for="comments">Is there anything you would like to privately note for the journal?</label><br>
                    <textarea
                        type="text"
                        id="comments" name="comments"
                        rows="4"
                        cols="30"
                        placeholder="You can write a few sentences here..."
                    > </textarea>
                </div>
                <br>
                <br>
                <input type="submit" value="Submit" class="form-done-button">
            </form>
        </div>`;
}

function switchToPatient() {
    console.log("Switchin");
    renderBlock(createPatientBlock());
}

function switchToCaregiver(e) {
    submitForm(document.getElementById("patient-form"), "/questionnaire-patient-info");
    renderBlock(createCaregiverBlock());
}

function renderBlock(block) {
    mainQuestionnaireContent.innerHTML = block;
}

function createIntroBlock() {
    date = Date().split(' ');
    date = date[0] + ', ' + date[1] + " " + date[2];
    return `<div class="form-page intro-block">
                <a href="/">
                    <img src="../static/home.png" alt="home button" class="home-button">
                </a>                
                <h2>Daily Check-In</h2>
                <p id="current-date">Friday, August 8</p>
                <img src="../static/family-img.png" alt="form intro image" class="form-intro-image">
                <h1>Let's answer today's questions together</h1>
                <p class="questionnaire-intro-subtitle">You will answer first, then pass the phone to your caregiver.</p>
                <a href="/questionnaire?phase=1"><button class="questionnaire-begin-button">Begin!</button></a>
            </div>`
}

let searchParams = new URLSearchParams(window.location.href.split('?')[1])

console.log(searchParams.get('phase'))

switch(searchParams.get('phase')) {
    case '1':
        console.log('case 1')
        renderBlock(createPatientBlock());
        break;
    case '2':
        renderBlock(createCaregiverBlock());
        break;
    default:
        renderBlock(createIntroBlock());
        break;
}

document.addEventListener("DOMContentLoaded", function () {
    const slider = document.getElementById("recover-ready");

    function updateSliderBackground(value) {
        const percent = (value / 10) * 100;
        const color = getColor(value);

        slider.style.background = `linear-gradient(to right, 
            ${color} 0%, 
            ${color} ${percent}%, 
            gray ${percent}%, 
            gray 100%)`;
    }


    slider.addEventListener("input", function () {
        updateSliderBackground(this.value);
    });

    updateSliderBackground(slider.value); // initialize
});

function hexToRgb(hex) {
    const bigint = parseInt(hex.slice(1), 16);
    return {
        r: (bigint >> 16) & 255,
        g: (bigint >> 8) & 255,
        b: bigint & 255
    };
}

function rgbToHex({ r, g, b }) {
    return "#" + [r, g, b].map(x =>
        x.toString(16).padStart(2, '0')
    ).join('');
}

function interpolateColor(color1, color2, factor) {
    const c1 = hexToRgb(color1);
    const c2 = hexToRgb(color2);
    const result = {
        r: Math.round(c1.r + (c2.r - c1.r) * factor),
        g: Math.round(c1.g + (c2.g - c1.g) * factor),
        b: Math.round(c1.b + (c2.b - c1.b) * factor)
    };
    return rgbToHex(result);
}

function getColor(value) {
    if (value <= 5) {
        const factor = value / 5;
        return interpolateColor('#c22700', '#ffae00', factor);
    } else {
        const factor = (value - 5) / 5;
        return interpolateColor('#ffae00', '#008a17', factor);
    }
}

document.addEventListener("DOMContentLoaded", () => {
  const dateElement = document.getElementById("current-date");
  if (dateElement) {
    const today = moment().format("dddd, MMMM D, YYYY");
    dateElement.textContent = today;
  }
});