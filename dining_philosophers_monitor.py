
import threading
import time
import random
import json
from collections import deque
from pathlib import Path

N = 4
MEALS = 1
HTML_FILE = Path(__file__).with_name("dining_philosophers_monitor.html")


class DiningMonitor:
    """Monitor that controls philosopher states and fork ownership."""

    def __init__(self):
        self.cv = threading.Condition()
        self.states = ["Thinking"] * N
        self.forks = [None] * N
        self.meals = [0] * N
        self.waiting = deque()
        self.events = []
        self.start_time = time.monotonic()

    def log(self, event, p=None, message=""):
        """Call while holding the monitor lock."""
        self.events.append({
            "step": len(self.events) + 1,
            "time": round(time.monotonic() - self.start_time, 2),
            "event": event,
            "philosopher": p,
            "message": message,
            "states": self.states.copy(),
            "forks": self.forks.copy(),
            "meals": self.meals.copy()
        })

    def record(self, event, p=None, message=""):
        with self.cv:
            self.log(event, p, message)

    def can_eat(self, p):
        left = p
        right = (p + 1) % N
        return self.forks[left] is None and self.forks[right] is None

    def pickup(self, p):
        with self.cv:
            self.states[p] = "Hungry"
            self.waiting.append(p)
            self.log("HUNGRY", p, f"P{p} is hungry and waiting")

            # FIFO admission: the queue's first philosopher gets priority.
            while not (
                self.waiting
                and self.waiting[0] == p
                and self.can_eat(p)
            ):
                self.cv.wait()

            self.waiting.popleft()
            self.states[p] = "Acquiring"
            self.log("ACQUIRING", p, f"P{p} is acquiring forks")

            left, right = p, (p + 1) % N
            self.forks[left] = p
            self.log("FORK_ACQUIRED", p, f"P{p} takes fork F{left}")

            self.forks[right] = p
            self.log("FORK_ACQUIRED", p, f"P{p} takes fork F{right}")

            self.states[p] = "Eating"
            self.log("EATING", p, f"P{p} starts eating")

    def putdown(self, p):
        with self.cv:
            self.states[p] = "Releasing"
            self.log("RELEASING", p, f"P{p} releases both forks")

            left, right = p, (p + 1) % N

            self.forks[left] = None
            self.log("FORK_RELEASED", p, f"P{p} releases fork F{left}")

            self.forks[right] = None
            self.log("FORK_RELEASED", p, f"P{p} releases fork F{right}")

            self.meals[p] += 1
            self.log("MEAL_DONE", p, f"P{p} finishes eating")

            self.states[p] = "Thinking"
            self.log("THINKING", p, f"P{p} returns to thinking")

            # Wake waiting philosophers to recheck the monitor condition.
            self.cv.notify_all()

    def philosopher(self, p):
        for _ in range(MEALS):
            with self.cv:
                self.states[p] = "Thinking"
                self.log("THINKING", p, f"P{p} is thinking")

            time.sleep(random.uniform(0.12, 0.3))
            self.pickup(p)
            time.sleep(random.uniform(0.2, 0.4))
            self.putdown(p)

        with self.cv:
            self.states[p] = "Finished"
            self.log("FINISHED", p, f"P{p} has finished")


def generate_html(events):
    data = json.dumps(events)

    # This HTML replays snapshots recorded by the actual monitor execution.
    html = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dining Philosophers - Monitor</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:white;font-family:Arial,sans-serif}
.sim{max-width:900px;margin:24px auto;background:#191d26;padding:12px;color:#eee}
.toolbar{display:flex;align-items:center;gap:7px;background:#242a36;
padding:8px;border-radius:5px;margin-bottom:12px;flex-wrap:wrap}
button,select{background:#303747;color:#eee;border:1px solid #465064;
border-radius:4px;padding:5px 9px;font-size:11px;cursor:pointer}
#slider{flex:1;min-width:80px;accent-color:#1685ff}
#counter{font-size:10px;white-space:nowrap}
.table{width:min(100%,430px);margin:auto;background:#242a36;border-radius:6px}
svg{display:block;width:100%;height:auto}
.legend{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;
color:#cbd3df;font-size:10px;margin:10px 0}
.dot{display:inline-block;width:8px;height:8px;margin-right:4px}
#message{color:#dce4f0;font-size:11px;text-align:center;
min-height:24px;margin-top:8px}
@media(max-width:500px){.sim{margin:0;padding:8px}}
</style>
</head>
<body>
<div class="sim">
 <div class="toolbar">
  <button id="play">Play</button>
  <button id="step">Step &gt;</button>
  <button id="reset">Reset</button>
  <label for="speed" style="color:#eee;font-size:11px">Speed</label>
  <select id="speed">
   <option value="1100">0.5x</option>
   <option value="650" selected>1x</option>
   <option value="300">2x</option>
  </select>
  <input id="slider" type="range" min="0" value="0">
  <span id="counter"></span>
 </div>
 <div class="table"><svg id="scene" viewBox="0 0 430 430"></svg></div>
 <div class="legend">
  <span><i class="dot" style="background:#c39200"></i>HUNGRY</span>
  <span><i class="dot" style="background:#28aaa3"></i>EATING</span>
  <span><i class="dot" style="background:#758195"></i>THINKING</span>
  <span><i class="dot" style="background:#d6a16c"></i>FREE FORK</span>
 </div>
 <div id="message"></div>
</div>
<script>
const events = __DATA__;
const svg = document.getElementById("scene");
const slider = document.getElementById("slider");
const counter = document.getElementById("counter");
const message = document.getElementById("message");
const NS = "http://www.w3.org/2000/svg";
slider.max = events.length - 1;

let index = 0, timer = null, playing = false;

const colors = {
 Thinking:"#758195", Hungry:"#c39200", Acquiring:"#258fbb",
 Eating:"#28aaa3", Releasing:"#258fbb", Finished:"#687587"
};

function add(tag, attrs, text) {
 const node = document.createElementNS(NS, tag);
 for (const [k,v] of Object.entries(attrs || {}))
  node.setAttribute(k,v);
 if (text !== undefined) node.textContent = text;
 svg.appendChild(node);
 return node;
}

function pos(cx,cy,r,a) {
 return [cx+r*Math.cos(a),cy+r*Math.sin(a)];
}

function draw(e) {
 svg.innerHTML = "";
 const cx=215, cy=215, forkR=104, personR=151;

 add("circle",{cx,cy,r:82,fill:"#202631",stroke:"#465062",
   "stroke-dasharray":"3 4"});
 add("circle",{cx,cy,r:46,fill:"#242a36"});
 add("text",{x:cx,y:cy-4,fill:"#dce4f0","font-size":12,
   "font-weight":"bold","text-anchor":"middle"},"DINING");
 add("text",{x:cx,y:cy+12,fill:"#8e9aaf","font-size":10,
   "text-anchor":"middle"},"MONITOR");

 // Forks sit between neighboring philosophers.
 for(let i=0;i<4;i++){
  const a=-Math.PI/2+i*Math.PI/2+Math.PI/4;
  const [x,y]=pos(cx,cy,forkR,a);
  const owner=e.forks[i];
  const color=owner===null?"#d6a16c":"#28aaa3";

  add("line",{x1:x-12*Math.cos(a),y1:y-12*Math.sin(a),
    x2:x+12*Math.cos(a),y2:y+12*Math.sin(a),
    stroke:color,"stroke-width":16,"stroke-linecap":"round"});

  add("rect",{x:x-15,y:y-9,width:30,height:18,rx:8,
    fill:color,stroke:"#ffffff80",
    transform:`rotate(${a*180/Math.PI},${x},${y})`});

  add("text",{x,y:y+3,fill:"white","font-size":9,
    "font-weight":"bold","text-anchor":"middle"},`F${i}`);

  add("text",{x,y:y+23,fill:owner===null?"#e0b98f":"#60e7d8",
    "font-size":8,"text-anchor":"middle"},
    owner===null?"FREE":`P${owner}`);
 }

 // Philosophers around the table.
 for(let i=0;i<4;i++){
  const a=-Math.PI/2+i*Math.PI/2;
  const [x,y]=pos(cx,cy,personR,a);
  const state=e.states[i];

  add("circle",{cx:x,cy:y,r:28,fill:colors[state]||"#758195",
    stroke:"#ffffff50","stroke-width":1.5});
  add("text",{x,y:y-3,fill:"white","font-size":13,
    "font-weight":"bold","text-anchor":"middle"},`P${i}`);
  add("text",{x,y:y+10,fill:"white","font-size":6.5,
    "font-weight":"bold","text-anchor":"middle"},state.toUpperCase());
  add("text",{x,y:y+40,fill:"#c1cada","font-size":8,
    "text-anchor":"middle"},`${e.meals[i]}/1 MEAL`);
 }
}

function show(i) {
 index=Math.max(0,Math.min(events.length-1,i));
 const e=events[index];
 slider.value=index;
 counter.textContent=`${index+1} / ${events.length}`;
 message.textContent=`#${e.step} | ${e.event.replaceAll("_"," ")} | ${e.message}`;
 draw(e);
}

function stop() {
 if(timer!==null) clearTimeout(timer);
 timer=null;
 playing=false;
 document.getElementById("play").textContent="Play";
}

function advance() {
 if(!playing) return;
 if(index>=events.length-1){stop();return;}
 show(index+1);
 timer=setTimeout(()=>{
  timer=null;
  advance();
 },Number(document.getElementById("speed").value));
}

document.getElementById("play").onclick=()=>{
 if(playing){stop();return;}
 if(index>=events.length-1) show(0);
 playing=true;
 document.getElementById("play").textContent="Pause";
 advance();
};

document.getElementById("step").onclick=()=>{
 stop();show(index+1);
};

document.getElementById("reset").onclick=()=>{
 stop();show(0);
};

slider.oninput=()=>{
 stop();show(Number(slider.value));
};

show(0);
</script>
</body>
</html>"""

    return html.replace("__DATA__", data)


def main():
    random.seed()
    monitor = DiningMonitor()
    monitor.record("START", None, "Monitor simulation started")

    threads = [
        threading.Thread(
            target=monitor.philosopher,
            args=(p,),
            name=f"Philosopher-{p}"
        )
        for p in range(N)
    ]

    for thread in threads:
        thread.start()
        time.sleep(0.03)

    for thread in threads:
        thread.join()

    monitor.record(
        "COMPLETE", None,
        "All four philosophers completed their meal"
    )

    HTML_FILE.write_text(
        generate_html(monitor.events),
        encoding="utf-8"
    )

    print("Monitor simulation completed.")
    print(f"Events recorded: {len(monitor.events)}")
    print(f"HTML file: {HTML_FILE.resolve()}")


if __name__ == "__main__":
    main()
