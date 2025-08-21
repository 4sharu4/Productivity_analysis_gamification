# Productitvity_analysis_gamification 🐾

**Gamified Personal Productivity Tracker with Hybrid Local & Cloud Automation**

---

## 🚀 Project Overview

Productitvity_analysis_gamification is an innovative productivity and behavior analytics project designed to help users understand and improve their daily computer usage through gamification. By tracking active window usage locally and evolving virtual pets based on accumulated productive time, this project transforms mundane usage statistics into an engaging, motivating experience.

---

## 🎯 Why This Project?

* **Real-world productivity insight:** Track how you spend time on your computer daily.
* **Gamification to motivate:** Virtual pets evolve based on your productive behavior, encouraging consistent focus.
* **Hybrid automation:** Combines local real-time tracking with cloud-based data processing and gamification.
* **FAANG-worthy skills showcase:** Demonstrates proficiency in scripting, automation, data analytics, cloud CI/CD, and software design.
* **Scalable & extensible:** Easily integrates with dashboards or notifications, and can be expanded to team or social use cases.

---

## 📋 Features

* **Local Usage Tracking:** Logs active application/window usage every 15 seconds.
* **Daily Analytics:** Aggregates usage data into productive and non-productive categories.
* **Pet Gamification:** Unlocks and evolves pets based on total productive hours.
* **Streak & Milestone Recognition:** Unlock new pets at defined usage streaks.
* **Hybrid Automation:**

  * *Local:* Windows Task Scheduler runs usage logging and analysis daily.
  * *Cloud:* GitHub Actions performs daily aggregation, pet growth, and updates repo automatically.
* **Data Visualization Ready:** Generates CSV reports for detailed app usage, productivity ratings, and pet statuses.
* **Configurable Thresholds:** Adjust accumulation thresholds, productivity mappings, and pet evolution stages.

---

## 🛠 Tech Stack

* **Python** — Core language for tracking, analytics, and automation scripts.
* **pandas** — Data processing and analytics.
* **pygetwindow** — Active window detection on Windows.
* **Windows Task Scheduler** — Local automation.
* **GitHub Actions** — Cloud-based CI/CD workflow for daily pet growth.
* **CSV** — Simple data persistence format, easy to extend with databases or dashboards.

---

## 📈 How It Works

1. **Tracking:** `tracker.py` runs every 15 seconds locally, logging the active window/application title and timestamp.
2. **Local Analysis:** `analyze.py` processes daily logs, categorizes app usage by productivity, updates pet levels based on accumulated productive minutes, and generates reports.
3. **Cloud Automation:** GitHub Actions workflow runs `analyze.py` daily in the cloud to update pet progress and commit results, keeping the pet zoo evolving even when the laptop is off.
4. **Gamification:** Pets evolve every 14 hours of accumulated productive time and unlock at streak milestones (1, 2, 5, 10, 15 days, etc.).

---

## ⚙️ Setup & Installation

### Prerequisites

* Python 3.8+ installed locally
* Windows OS for `pygetwindow` active window tracking
* Git & GitHub account

### Local Setup

```bash
git clone https://github.com/yourusername/pet-zoo-tracker.git
cd pet-zoo-tracker
pip install -r requirements.txt  # pandas, pygetwindow
```

### Running Tracker Locally

```bash
python tracker.py
```

*(Recommended: Use Windows Task Scheduler to automate this script daily, see below.)*

### Running Analysis Locally

```bash
python analyze.py
```

### Automate with Windows Task Scheduler

1. Open **Task Scheduler**.
2. Create **Basic Task**:

   * Name: `Pet Tracker Logger`
   * Trigger: Daily at 12:00 AM
   * Action: Start Program

     * Program/script: Full path to `python.exe`
     * Arguments: Full path to `tracker.py`
3. Create another Basic Task:

   * Name: `Daily Analyzer`
   * Trigger: Daily at 11:59 PM
   * Action: Start Program

     * Program/script: Python executable
     * Arguments: Path to `analyze.py`
4. Configure to allow waking from sleep.

### Cloud Automation with GitHub Actions

Add `.github/workflows/petzoo.yml` with:

```yaml
name: Pet Zoo Daily Growth

on:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:

jobs:
  grow_pet_zoo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pandas pygetwindow
      - run: python analyze.py
      - run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add pets.csv daily_summary.csv accumulated_minutes.csv
          git commit -m "Daily pet update $(date)"
          git push
```

Commit and push to GitHub to enable daily cloud pet growth.

---

## 📁 Project Structure

```
pet-zoo-tracker/
├── tracker.py           # Local active window logger
├── analyze.py           # Usage analyzer and pet manager
├── pets.csv             # Pet data (auto-updated)
├── usage_log.csv        # Raw usage logs
├── daily_summary.csv    # App usage summaries
├── accumulated_minutes.csv # Total productive time accumulation
├── .github/workflows/   # GitHub Actions workflows
│   └── petzoo.yml
├── README.md            # This file
└── requirements.txt     # Python dependencies
```

---

## 🎓 Skills Demonstrated

* Python scripting & automation
* Real-time data collection & processing
* Data analytics & visualization prep
* Hybrid automation (local + cloud CI/CD)
* Scheduling & orchestration (Task Scheduler, GitHub Actions)
* Gamification & UX design principles

---

## 🤝 Contributing

Contributions and feature requests are welcome! Feel free to open issues or submit pull requests.

---

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 🔗 References

* [pygetwindow](https://github.com/asweigart/pygetwindow) for active window tracking
* [pandas](https://pandas.pydata.org/) for data processing
* [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

If you want me to generate a **requirements.txt** or **LICENSE** file, or help with anything else — just ask!
