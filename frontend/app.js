// ============================================================
// VISION SOS DASHBOARD
// ============================================================

let lastEventId = null;


// ============================================================
// UPDATE SYSTEM STATUS
// ============================================================

async function updateStatus() {

    try {

        const response = await fetch(
            "/api/status?t=" + Date.now()
        );

        const data = await response.json();

        const state = data.state || "NORMAL";
        const countdown = data.countdown;


        const statusCard =
            document.getElementById("status-card");

        const statusText =
            document.getElementById("current-status");

        const statusDescription =
            document.getElementById("status-description");

        const statusIcon =
            document.getElementById("status-icon");

        const overlay =
            document.getElementById("camera-status-overlay");


        // ----------------------------------------
        // NORMAL
        // ----------------------------------------

        if (state === "NORMAL") {

            statusCard.className =
                "status-card normal";

            statusText.textContent =
                "NORMAL";

            statusDescription.textContent =
                "Monitoring for potential emergencies";

            statusIcon.textContent =
                "✓";

            overlay.textContent =
                "NORMAL";

            overlay.className =
                "camera-overlay";
        }


        // ----------------------------------------
        // FALL SUSPECTED
        // ----------------------------------------

        else if (state === "FALL_SUSPECTED") {

            statusCard.className =
                "status-card warning";

            statusText.textContent =
                "FALL SUSPECTED";

            if (countdown !== null) {

                statusDescription.textContent =
                    `Confirming emergency · ${
                        countdown.toFixed(1)
                    }s`;

                overlay.textContent =
                    `FALL SUSPECTED · ${
                        countdown.toFixed(1)
                    }s`;

            } else {

                statusDescription.textContent =
                    "Potential fall detected";

                overlay.textContent =
                    "FALL SUSPECTED";
            }

            statusIcon.textContent =
                "!";

            overlay.className =
                "camera-overlay warning";
        }


        // ----------------------------------------
        // EMERGENCY
        // ----------------------------------------

        else if (state === "EMERGENCY") {

            statusCard.className =
                "status-card emergency";

            statusText.textContent =
                "EMERGENCY";

            statusDescription.textContent =
                "Emergency confirmed · Response initiated";

            statusIcon.textContent =
                "🚨";

            overlay.textContent =
                "🚨 EMERGENCY";

            overlay.className =
                "camera-overlay emergency";
        }


        // ----------------------------------------
        // SYSTEM BADGE
        // ----------------------------------------

        const badge =
            document.getElementById("system-badge");

        if (data.system === "ACTIVE") {

            badge.className =
                "system-badge active";

            badge.innerHTML =
                '<span class="dot"></span> SYSTEM ACTIVE';

        } else {

            badge.className =
                "system-badge";

            badge.innerHTML =
                '<span class="dot"></span> SYSTEM OFFLINE';
        }


    } catch (error) {

        console.error(
            "Status update failed:",
            error
        );
    }
}


// ============================================================
// LIVE CAMERA
// ============================================================

function updateCamera() {

    const camera =
        document.getElementById("live-camera");

    const placeholder =
        document.getElementById("camera-placeholder");


    if (!camera) {

        console.error(
            "Live camera element not found"
        );

        return;
    }


    // Simply reload the latest JPEG.
    camera.src =
        "/api/frame?t=" +
        Date.now();


    camera.style.display =
        "block";


    if (placeholder) {

        placeholder.style.display =
            "none";
    }
}


// ============================================================
// UPDATE LATEST EVENT
// ============================================================

function updateLatestEvent(event) {

    const noEvent =
        document.getElementById("no-event");

    const details =
        document.getElementById("event-details");


    if (!event) {

        noEvent.classList.remove(
            "hidden"
        );

        details.classList.add(
            "hidden"
        );

        return;
    }


    noEvent.classList.add(
        "hidden"
    );

    details.classList.remove(
        "hidden"
    );


    const eventTitle =
        document.getElementById(
            "event-title"
        );

    eventTitle.textContent =
        event.event_type === "seizure"
            ? "🚨 SEIZURE-LIKE EVENT"
            : "🚨 COLLAPSE";


    document.getElementById(
        "event-label"
    ).textContent =
        event.severity_label || "UNKNOWN";


    document.getElementById(
        "event-score"
    ).textContent =
        `${event.severity}/100`;


    document.getElementById(
        "event-confidence"
    ).textContent =
        `${Math.round(
            (event.confidence || 0) * 100
        )}%`;


    document.getElementById(
        "event-motionless"
    ).textContent =
        `${event.motionless_sec || 0}s`;


    document.getElementById(
        "event-time"
    ).textContent =
        event.timestamp || "—";
}


// ============================================================
// EVENT HISTORY
// ============================================================

async function updateEvents() {

    try {

        const response =
            await fetch(
                "/api/events?t=" +
                Date.now()
            );


        const events =
            await response.json();


        const history =
            document.getElementById(
                "event-history"
            );


        const count =
            document.getElementById(
                "event-count"
            );


        count.textContent =
            `${events.length} ${
                events.length === 1
                    ? "event"
                    : "events"
            }`;


        if (events.length === 0) {

            history.innerHTML =
                `
                <div class="empty-history">
                    No events recorded
                </div>
                `;

            updateLatestEvent(
                null
            );

            return;
        }


        // Latest event
        updateLatestEvent(
            events[0]
        );


        // History
        history.innerHTML =
            events.map(
                event => {

                    const label =
                        event.severity_label ||
                        "UNKNOWN";


                    const severityClass =
                        "severity-" +
                        label.toLowerCase();


                    const type =
                        event.event_type ===
                        "seizure"
                            ? "🚨 SEIZURE"
                            : "🚨 COLLAPSE";


                    return `
                        <div class="history-row">

                            <div class="history-type">
                                ${type}
                            </div>

                            <div class="
                                history-severity
                                ${severityClass}
                            ">
                                ${label}
                            </div>

                            <div class="history-score">
                                ${event.severity}/100
                            </div>

                            <div class="history-time">
                                ${event.timestamp || "—"}
                            </div>

                        </div>
                    `;
                }
            ).join("");


    } catch (error) {

        console.error(
            "Event update failed:",
            error
        );
    }
}


// ============================================================
// INITIAL LOAD
// ============================================================

async function refreshDashboard() {

    await updateStatus();

    await updateEvents();

    updateCamera();
}


refreshDashboard();


// ============================================================
// CONTINUOUS UPDATES
// ============================================================

setInterval(
    updateStatus,
    500
);


setInterval(
    updateEvents,
    1000
);


setInterval(
    updateCamera,
    100
);