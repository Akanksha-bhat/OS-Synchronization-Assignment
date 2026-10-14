# OS Synchronization Assignment

**Name:** M Akanksha Bhat  
**USN:** NNM24IS115

**Programming Language:** Python 3  
**Dependencies:** Python standard library; no additional installations are required if the programs use only standard-library modules.

---

## 1. Project Overview

This assignment demonstrates two operating system synchronization problems using semaphores and monitors:

1. Readers-Writers Problem using Semaphores
2. Readers-Writers Problem using Monitors
3. Dining Philosophers Problem using Semaphores
4. Dining Philosophers Problem using Monitors

The programs demonstrate how threads share resources safely. They record execution events and provide HTML simulations so that the synchronization process can be viewed in a web browser. The order of events may vary each time the program runs because thread scheduling can change.

## 2. Project Structure

The repository contains the following files:

- `readers_writers_semaphore.py` — Readers-Writers implementation using semaphores.
- `readers_writers_monitors.py` — Readers-Writers implementation using monitor-style synchronization.
- `dining_philosophers_semaphore.py` — Dining Philosophers implementation using semaphores.
- `dining_philosophers_monitor.py` — Dining Philosophers implementation using monitor-style synchronization.
- `readers_writers_visual.html` — Saved HTML visualization for the Readers-Writers problem.
- `dining_philosophers_simulation.html` — Saved HTML visualization for the Dining Philosophers problem.
- `readers_writers_semaphore.png` — Screenshot for the Readers-Writers semaphore implementation.
- `readers_writers_monitors.png` — Screenshot for the Readers-Writers monitor implementation.
- `dining_philosophers_semaphore.png` — Screenshot for the Dining Philosophers semaphore implementation.
- `dining_philosophers_monitors.png` — Screenshot for the Dining Philosophers monitor implementation.

## 3. Tools and Requirements

- Python 3
- A terminal or command prompt
- A modern web browser, such as Chrome, Edge, or Firefox
- Git and GitHub for version control and submission

The Python programs are intended to use the Python standard library. If a source file imports any third-party package, install that package before running the program.

Check that Python is installed:

```bash
python --version
```

On some systems, use `python3 --version` instead.

## 4. How to Run the Programs

Open a terminal in the folder containing the Python files. Run each implementation separately.

### A. Readers-Writers using Semaphores

```bash
python readers_writers_semaphore.py
```

### B. Readers-Writers using Monitors

```bash
python readers_writers_monitors.py
```

### C. Dining Philosophers using Semaphores

```bash
python dining_philosophers_semaphore.py
```

### D. Dining Philosophers using Monitors

```bash
python dining_philosophers_monitor.py
```

If your computer uses `python3`, replace `python` with `python3` in the commands.

The console should display the events printed by each program. The exact output and event order may differ between runs.

## 5. Generating the HTML Simulations

1. Run the relevant Python program using the commands in Section 4.
2. Wait for the program to finish executing.
3. Check the terminal output and the Python code to confirm where the HTML file is saved.
4. If the program generates an HTML file, open that file in a browser as described below.

The repository currently contains saved HTML files. Confirm by running the current Python source code that the simulations are generated or updated automatically; a saved HTML file alone does not prove that it is regenerated on every run.

## 6. Opening the HTML Simulations

1. Open the project folder in File Explorer.
2. Find `readers_writers_visual.html` or `dining_philosophers_simulation.html`.
3. Double-click the file to open it in your default browser. Alternatively, right-click the file and choose a browser.
4. If the browser already has the file open after a new run, refresh the page to see the latest saved version.

## 7. Expected Output

### Readers-Writers Problem

- Readers and writers access shared data according to the synchronization rules.
- Synchronization prevents readers and writers from accessing the shared resource in conflicting ways.
- The console and HTML simulation show the execution events that the program records.

### Dining Philosophers Problem

- Four philosophers share four chopsticks.
- A philosopher can begin eating only after acquiring both required chopsticks.
- Synchronization coordinates access to the chopsticks and is designed to prevent deadlock.
- The console and HTML simulation show the states and events recorded by the program.

The actual order of events may change between runs because multiple threads can execute in different orders.

## 8. Sample Screenshots

The repository includes these screenshots:

- `readers_writers_semaphore.png`
- `readers_writers_monitors.png`
- `dining_philosophers_semaphore.png`
- `dining_philosophers_monitors.png`

Open the image files on GitHub to view the screenshots. Make sure they represent the final version of your programs and simulations.

## 9. Known Limitations

- The execution order and timestamps can vary between runs.
- The HTML simulation can display only the events and states recorded by the program.
- A saved HTML file may not show the latest run until it is regenerated and the browser is refreshed.
- Deadlock prevention and starvation depend on the synchronization logic; these properties should be checked through testing.
- The exact output depends on the implementation and the order in which threads are scheduled.

## 10. AI Tools Used and Prompt Log

**AI tool:** ChatGPT by OpenAI.

AI assistance was used for help with understanding synchronization concepts, implementation, debugging, and documentation, where applicable. The code should be reviewed and tested to ensure that the student understands how it works.

**Prompt log:** Add the URL to the prompt log submitted with the assignment, if a separate prompt log is required.

## 11. References and Acknowledgements

- Operating Systems lecture notes and assignment instructions.
- Python documentation: https://docs.python.org/3/
- Python threading documentation: https://docs.python.org/3/library/threading.html
- GitHub documentation: https://docs.github.com/
- OpenAI ChatGPT: https://chatgpt.com/

This project was prepared for academic learning and to demonstrate synchronization, thread coordination, and visualization of operating system concepts.
