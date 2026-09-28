const form = document.getElementById("predictionForm");

const riskScore = document.getElementById("riskScore");
const riskStatus = document.getElementById("riskStatus");
const riskMessage = document.getElementById("scoreMessage");

const meterMarker = document.getElementById("meterMarker");

const historyList = document.getElementById("historyList");

const clearHistory =
    document.getElementById("clearHistory");

const themeBtn =
    document.getElementById("themeBtn");

const mobileTheme =
    document.getElementById("mobileTheme");


// ================= THEME =================

function toggleTheme() {

    document.body.classList.toggle("dark");

    const dark =
        document.body.classList.contains("dark");

    localStorage.setItem(
        "theme",
        dark ? "dark" : "light"
    );
}


if (themeBtn) {
    themeBtn.addEventListener(
        "click",
        toggleTheme
    );
}

if (mobileTheme) {
    mobileTheme.addEventListener(
        "click",
        toggleTheme
    );
}


if (
    localStorage.getItem("theme") === "dark"
) {
    document.body.classList.add("dark");
}


// ================= PREDICTION =================

/*
    IMPORTANT:

    JavaScript does NOT generate the prediction.

    Flask + ML model generates the prediction.

    Same input → Same model → Same result.
*/

if (form) {

    form.addEventListener("submit", function () {

        const button =
            form.querySelector("button[type='submit']");

        if (button) {

            button.disabled = true;

            const originalText =
                button.textContent;

            button.textContent =
                "Analyzing...";

            /*
                Flask will process the form.

                We do NOT use:
                Math.random()
                here.
            */

            setTimeout(function () {

                button.textContent =
                    originalText;

                button.disabled = false;

            }, 3000);
        }

    });
}


// ================= SHOW RESULT =================

function showResult(score) {

    score = Number(score);

    if (isNaN(score)) {
        return;
    }

    // Keep score between 0 and 100
    score = Math.max(
        0,
        Math.min(100, score)
    );


    // Score
    riskScore.textContent =
        score.toFixed(1);


    // Meter
    meterMarker.style.left =
        score + "%";


    let status;
    let message;
    let className;


    // ================= HIGH RISK =================

    if (score >= 70) {

        status = "High Risk";

        message =
            "The model score is elevated. Further clinical evaluation is recommended.";

        className = "high";

    }


    // ================= MODERATE RISK =================

    else if (score >= 40) {

        status = "Moderate Risk";

        message =
            "The model score is moderate. Consider discussing your results with a healthcare professional.";

        className = "moderate";

    }


    // ================= LOW RISK =================

    else {

        status = "Low Risk";

        message =
            "The model score is lower based on the entered information.";

        className = "low";
    }


    // Status
    riskStatus.textContent =
        status;


    // Status color
    riskStatus.style.color =
        `var(--${
            className === "high"
                ? "red"
                : className === "moderate"
                    ? "yellow"
                    : "green"
        })`;


    // Message
    riskMessage.textContent =
        message;
}


// ================= HISTORY =================

function saveHistory(score) {

    score = Number(score);

    if (isNaN(score)) {
        return;
    }


    let history =
        JSON.parse(
            localStorage.getItem(
                "diabetesHistory"
            )
        ) || [];


    const date =
        new Date().toLocaleString();


    let status;

    if (score >= 70) {

        status = "High Risk";

    }

    else if (score >= 40) {

        status = "Moderate Risk";

    }

    else {

        status = "Low Risk";

    }


    history.unshift({

        score: score,

        date: date,

        status: status

    });


    // Keep only last 20
    history =
        history.slice(0, 20);


    localStorage.setItem(
        "diabetesHistory",
        JSON.stringify(history)
    );


    displayHistory();
}


// ================= DISPLAY HISTORY =================

function displayHistory() {

    if (!historyList) {
        return;
    }


    const history =
        JSON.parse(
            localStorage.getItem(
                "diabetesHistory"
            )
        ) || [];


    if (history.length === 0) {

        historyList.innerHTML = `

            <div class="empty-history">

                <div class="empty-icon">◷</div>

                <h3>No predictions yet</h3>

                <p>
                    Your prediction history will appear here.
                </p>

            </div>

        `;

        return;
    }


    historyList.innerHTML =
        history.map((item) => {

            const type =
                item.score >= 70
                    ? "high"
                    : item.score >= 40
                        ? "moderate"
                        : "low";


            return `

                <div class="history-item">

                    <div class="history-info">

                        <strong>
                            Diabetes Risk Assessment
                        </strong>

                        <span>
                            ${item.date}
                        </span>

                    </div>

                    <div
                        class="history-risk ${type}"
                    >

                        ${Number(item.score).toFixed(1)}%

                    </div>

                </div>

            `;

        }).join("");
}


// ================= CLEAR HISTORY =================

if (clearHistory) {

    clearHistory.addEventListener(
        "click",
        function() {

            localStorage.removeItem(
                "diabetesHistory"
            );

            displayHistory();

        }
    );
}


// ================= LOAD SERVER RESULT =================

/*
    Flask will put the real ML prediction
    into window.serverPrediction.

    Example:

    window.serverPrediction = 63.42;
*/

if (
    typeof window.serverPrediction !== "undefined" &&
    window.serverPrediction !== null
) {

    const score =
        Number(window.serverPrediction);


    if (!isNaN(score)) {

        showResult(score);

        saveHistory(score);

    }
}


// ================= INITIALIZE =================

displayHistory();