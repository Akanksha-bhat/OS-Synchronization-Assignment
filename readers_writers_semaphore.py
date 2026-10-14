import json
import random
import threading
import time
from pathlib import Path

# =====================================================
# READERS-WRITERS SIMULATION USING SEMAPHORES
# =====================================================

OUTPUT_FILE = Path(__file__).with_name("readers_writers_visual.html")

# Semaphores
turnstile = threading.Semaphore(1)
resource = threading.Semaphore(1)
count_mutex = threading.Semaphore(1)

# Shared variables
reader_count = 0
shared_data = 0
active_readers = set()
waiting_readers = set()
waiting_writers = set()
active_writer = None
finished = set()

# Event recording
events = []
state_lock = threading.Lock()
start_time = time.perf_counter()


# =====================================================
# EVENT LOGGING
# =====================================================

def log_event(action, actor, message=""):
    with state_lock:
        assert not (active_writer and active_readers), (
            "Synchronization violation detected"
        )

        events.append({
            "n": len(events) + 1,
            "time": round(time.perf_counter() - start_time, 3),
            "action": action,
            "actor": actor,
            "message": message,
            "activeReaders": sorted(active_readers),
            "waitingReaders": sorted(waiting_readers),
            "waitingWriters": sorted(waiting_writers),
            "activeWriter": active_writer,
            "finished": sorted(finished),
            "sharedData": shared_data,
            "resourceState": (
                "WRITING" if active_writer else
                "READING" if active_readers else
                "AVAILABLE"
            )
        })


# =====================================================
# READER FUNCTION
# =====================================================

def reader(rid, delay):
    global reader_count

    time.sleep(delay)

    with state_lock:
        waiting_readers.add(rid)

    log_event("ARRIVAL", rid, "Reader arrived")

    # Pass through the writer-preference turnstile.
    turnstile.acquire()
    turnstile.release()

    count_mutex.acquire()
    reader_count += 1

    # First reader locks the shared resource.
    if reader_count == 1:
        log_event("WAITING", rid, "Waiting for shared resource")
        resource.acquire()

    with state_lock:
        waiting_readers.discard(rid)
        active_readers.add(rid)

    log_event(
        "ENTER_READ",
        rid,
        "Entered reading critical section"
    )

    count_mutex.release()

    # Simulate reading.
    time.sleep(random.uniform(0.4, 0.8))

    with state_lock:
        value = shared_data

    log_event("READ", rid, f"Read shared data: {value}")

    # Exit reading critical section.
    count_mutex.acquire()

    with state_lock:
        active_readers.discard(rid)

    reader_count -= 1

    log_event("EXIT_READ", rid, "Exited reading section")

    # Last reader releases the resource.
    if reader_count == 0:
        resource.release()
        log_event(
            "RESOURCE_RELEASED",
            rid,
            "Last reader released resource"
        )

    count_mutex.release()

    with state_lock:
        finished.add(rid)

    log_event("FINISHED", rid, "Reader finished")


# =====================================================
# WRITER FUNCTION
# =====================================================

def writer(wid, delay):
    global active_writer, shared_data

    time.sleep(delay)

    with state_lock:
        waiting_writers.add(wid)

    log_event("ARRIVAL", wid, "Writer arrived")

    # Block new readers while waiting for exclusive access.
    turnstile.acquire()

    log_event(
        "WAITING",
        wid,
        "Writer waiting for exclusive access"
    )

    resource.acquire()

    with state_lock:
        waiting_writers.discard(wid)
        active_writer = wid

    log_event(
        "ENTER_WRITE",
        wid,
        "Entered exclusive writing section"
    )

    # Resource semaphore still protects the writer.
    turnstile.release()

    # Simulate writing.
    time.sleep(random.uniform(0.5, 0.9))

    with state_lock:
        shared_data += 10
        value = shared_data

    log_event("WRITE", wid, f"Updated shared data to {value}")

    with state_lock:
        active_writer = None

    log_event("EXIT_WRITE", wid, "Exited writing section")

    resource.release()

    log_event(
        "RESOURCE_RELEASED",
        wid,
        "Writer released shared resource"
    )

    with state_lock:
        finished.add(wid)

    log_event("FINISHED", wid, "Writer finished")


# =====================================================
# HTML GENERATION
# HTML is generated from the recorded execution events.
# =====================================================

def generate_html():

    data = json.dumps(events)

    html_template = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Readers and Writers - Semaphore Lab</title>

<style>
* {
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background: #f1f3f9;
    color: #202942;
    margin: 0 auto;
    padding: 16px 24px;
    max-width: 1200px;
}

header {
    text-align: center;
    margin-bottom: 14px;
}

h1 {
    font-size: 24px;
    margin: 6px 0;
}

.subtitle {
    color: #707b90;
    font-size: 13px;
    margin: 6px;
}

.toolbar {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 12px;
}

button {
    padding: 8px 14px;
    border: none;
    border-radius: 6px;
    background: #26785e;
    color: white;
    font-size: 13px;
    font-weight: bold;
    cursor: pointer;
}

button.secondary {
    background: #dfe5ef;
    color: #25304a;
}

.summary {
    text-align: center;
    margin: 12px;
    font-size: 15px;
    font-weight: bold;
}

.layout {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 13px;
}

.panel {
    background: white;
    border: 1px solid #e1e5ee;
    border-radius: 9px;
    padding: 13px;
    min-height: 190px;
    box-shadow: 0 3px 10px #24334b0a;
}

.panel h2 {
    text-align: center;
    font-size: 14px;
    margin: 4px 0 12px;
    padding-bottom: 9px;
    border-bottom: 2px solid #d9dce4;
}

#critical {
    border: 2px solid #e6ad30;
}

.processes {
    display: flex;
    justify-content: center;
    align-content: flex-start;
    flex-wrap: wrap;
    gap: 7px;
    min-height: 125px;
}

.process {
    color: white;
    background: #2868b2;
    border-radius: 5px;
    padding: 7px 9px;
    font-size: 12px;
    font-weight: bold;
}

.process.writer {
    background: #d9534f;
}

.empty {
    padding-top: 32px;
    font-size: 12px;
    color: #929bad;
}

.log-panel {
    margin-top: 14px;
    padding: 13px;
    background: white;
    border: 1px solid #e1e5ee;
    border-radius: 9px;
}

.log-panel h2 {
    font-size: 14px;
    margin: 0 0 9px;
}

#log {
    height: 145px;
    overflow-y: auto;
    padding: 9px;
    border: 1px solid #e1e5ee;
    background: #fafbfe;
    font-family: monospace;
    font-size: 11px;
    line-height: 1.5;
    white-space: pre-wrap;
}

.controls {
    display: flex;
    align-items: center;
    gap: 9px;
    margin-top: 11px;
    flex-wrap: wrap;
    font-size: 12px;
}

input[type=range] {
    flex: 1;
    min-width: 100px;
}

.current {
    background: #edf3ff;
    padding: 10px;
    border-radius: 6px;
    margin-top: 10px;
    font-size: 12px;
    line-height: 1.5;
}

.legend {
    font-size: 11px;
    color: #707b90;
    margin: 8px 0 0;
}

@media (max-width: 650px) {
    body {
        padding: 12px;
    }

    .layout {
        grid-template-columns: 1fr;
    }

    .panel {
        min-height: 150px;
    }
}
</style>
</head>

<body>

<header>
    <h1>Readers and Writers Synchronization</h1>
    <p class="subtitle">
        Semaphore-based concurrency demonstration
    </p>

    <div class="toolbar">
        <button id="play">Start Simulation</button>
        <button id="reset" class="secondary">Reset</button>
    </div>

    <div class="summary">
        Shared Data: <span id="data">0</span>
        &nbsp; | &nbsp;
        Active Readers: <span id="count">0</span>
    </div>
</header>

<div class="layout">

    <section class="panel">
        <h2>Waiting Room</h2>
        <div id="waitingList" class="processes"></div>
    </section>

    <section class="panel" id="critical">
        <h2>Critical Section</h2>
        <div id="activeList" class="processes"></div>
    </section>

    <section class="panel">
        <h2>Finished</h2>
        <div id="finishedList" class="processes"></div>
    </section>

</div>

<section class="log-panel">
    <h2>Execution Log</h2>
    <div id="log"></div>

    <div class="controls">
        <button id="previous" class="secondary">Previous</button>

        <label for="slider">Timeline</label>
        <input id="slider" type="range" min="0" value="0">

        <span id="counter"></span>

        <button id="next" class="secondary">Next</button>
    </div>

    <div id="current" class="current">
        Press Start Simulation to replay the recorded events.
    </div>
</section>

<script>
const events = __EVENT_DATA__;

let index = 0;
let timer = null;

const el = id => document.getElementById(id);

function stopPlayback() {
    if (timer !== null) {
        clearInterval(timer);
    }

    timer = null;
    el("play").textContent = "Start Simulation";
}

function chip(id) {
    const cls = id.startsWith("Writer")
        ? "process writer"
        : "process";

    return '<span class="' + cls + '">' + id + '</span>';
}

function render(position) {
    if (!events.length) return;

    index = Math.max(
        0,
        Math.min(events.length - 1, position)
    );

    const e = events[index];

    el("slider").value = index;
    el("counter").textContent =
        (index + 1) + " / " + events.length;

    el("data").textContent = e.sharedData;
    el("count").textContent = e.activeReaders.length;

    const active = [...e.activeReaders];

    if (e.activeWriter) {
        active.push(e.activeWriter);
    }

    const waiting = [
        ...e.waitingReaders,
        ...e.waitingWriters
    ];

    el("waitingList").innerHTML = waiting.length
        ? waiting.map(chip).join("")
        : '<span class="empty">No process waiting</span>';

    el("activeList").innerHTML = active.length
        ? active.map(chip).join("")
        : '<span class="empty">Resource available</span>';

    el("finishedList").innerHTML = e.finished.length
        ? e.finished.map(chip).join("")
        : '<span class="empty">No completed processes</span>';

    el("current").textContent =
        "Event " + e.n + " | " + e.actor + " | " +
        e.action.replaceAll("_", " ") + " | " +
        e.message + " | Resource: " + e.resourceState;

    el("log").textContent = events
        .slice(0, index + 1)
        .map(event =>
            "[" + event.time.toFixed(3) + "s] " +
            event.actor + " - " +
            event.action + ": " + event.message
        )
        .join("\n");

    el("log").scrollTop = el("log").scrollHeight;
}

el("slider").max = Math.max(0, events.length - 1);

el("slider").addEventListener("input", event => {
    stopPlayback();
    render(Number(event.target.value));
});

el("previous").onclick = () => {
    stopPlayback();
    render(index - 1);
};

el("next").onclick = () => {
    stopPlayback();
    render(index + 1);
};

el("play").onclick = () => {
    if (timer !== null) {
        stopPlayback();
        return;
    }

    if (index >= events.length - 1) {
        render(0);
    }

    el("play").textContent = "Pause";

    timer = setInterval(() => {
        if (index >= events.length - 1) {
            stopPlayback();
            return;
        }

        render(index + 1);
    }, 650);
};

el("reset").onclick = () => {
    stopPlayback();
    render(0);
};

render(0);
</script>

</body>
</html>'''

    return html_template.replace("__EVENT_DATA__", data)


# =====================================================
# MAIN PROGRAM
# =====================================================

def main():
    global start_time

    start_time = time.perf_counter()

    log_event(
        "START",
        "SYSTEM",
        "Launching reader and writer processes"
    )

    # Different arrival times demonstrate waiting and contention.
    threads = [
        threading.Thread(
            target=reader, args=("Reader 1", 0.00)
        ),
        threading.Thread(
            target=reader, args=("Reader 2", 0.05)
        ),
        threading.Thread(
            target=writer, args=("Writer 1", 0.12)
        ),
        threading.Thread(
            target=reader, args=("Reader 3", 0.20)
        ),
        threading.Thread(
            target=writer, args=("Writer 2", 0.30)
        ),
        threading.Thread(
            target=reader, args=("Reader 4", 0.38)
        ),
        threading.Thread(
            target=reader, args=("Reader 5", 0.45)
        )
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    log_event(
        "COMPLETE",
        "SYSTEM",
        "All processes completed"
    )

    # Generate HTML using the actual execution trace.
    html_content = generate_html()

    OUTPUT_FILE.write_text(
        html_content,
        encoding="utf-8"
    )

    print("\nReaders-Writers Simulation Completed")
    print("------------------------------------")
    print("Events recorded:", len(events))
    print("Final shared data:", shared_data)
    print("HTML file:", OUTPUT_FILE.resolve())
    print("Open the HTML file in your browser.")


if __name__ == "__main__":
    main()
