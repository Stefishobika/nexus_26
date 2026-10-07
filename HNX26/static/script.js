const input = document.getElementById("videoInput");
const dropzone = document.getElementById("dropzone");
const dropTitle = document.getElementById("dropTitle");
const dropHint = document.getElementById("dropHint");
const analyzeButton = document.getElementById("analyzeButton");
const statusEl = document.getElementById("status");
const result = document.getElementById("result");
const resultVideo = document.getElementById("resultVideo");
const summary = document.getElementById("summary");
const eventList = document.getElementById("eventList");

let timer = null;


function setStatus(text, isError = false) {
    statusEl.textContent = text;
    statusEl.classList.toggle("error", isError);
}

function formatElapsed(seconds) {
    const m = Math.floor(seconds / 60);
    const s = String(seconds % 60).padStart(2, "0");
    return `${m}:${s}`;
}

function setFile(file) {
    if (!file) return;
    dropTitle.textContent = file.name;
    dropHint.textContent = `${(file.size / 1048576).toFixed(1)} MB. Click to choose a different video.`;
    dropzone.classList.add("has-file");
    analyzeButton.disabled = false;
    result.hidden = true;
    setStatus("");
}

function setBusy(busy) {
    analyzeButton.disabled = busy;
    input.disabled = busy;
}

function showResult(data) {
    // The backend always writes the same filename, so bust the browser cache
    resultVideo.src = `${data.video}?t=${Date.now()}`;

    eventList.innerHTML = "";
    const events = Array.isArray(data.events) ? data.events : [];
    for (const e of events) {
        const li = document.createElement("li");
        const time = document.createElement("time");
        time.textContent = e.time;
        const text = document.createElement("span");
        text.textContent = e.text;
        li.append(time, text);
        eventList.append(li);
    }
    summary.hidden = events.length === 0;

    result.hidden = false;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
}


input.addEventListener("change", () => setFile(input.files[0]));

["dragenter", "dragover"].forEach((type) => {
    dropzone.addEventListener(type, (e) => {
        e.preventDefault();
        dropzone.classList.add("dragging");
    });
});

["dragleave", "drop"].forEach((type) => {
    dropzone.addEventListener(type, () => dropzone.classList.remove("dragging"));
});

dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    if (input.disabled || !e.dataTransfer.files.length) return;
    input.files = e.dataTransfer.files;
    setFile(input.files[0]);
});

analyzeButton.addEventListener("click", async () => {
    const file = input.files[0];
    if (!file) return;

    const body = new FormData();
    body.append("video", file);

    const started = Date.now();
    setBusy(true);
    setStatus("Analyzing... 0:00. Long videos can take a few minutes.");
    timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - started) / 1000);
        setStatus(`Analyzing... ${formatElapsed(elapsed)}. Long videos can take a few minutes.`);
    }, 1000);

    try {
        const res = await fetch("/analyze", { method: "POST", body });
        const data = await res.json().catch(() => ({}));

        if (!res.ok || !data.success) {
            throw new Error(data.message || "Analysis failed");
        }

        setStatus("Done.");
        showResult(data);
    } catch (err) {
        const unreachable = err instanceof TypeError;
        setStatus(unreachable ? "Could not reach the server." : err.message, true);
    } finally {
        clearInterval(timer);
        setBusy(false);
    }
});