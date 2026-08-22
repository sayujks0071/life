import datetime
import os
import re
import sys


# Keep in sync with JOURNAL_TRACK.md. Never print a date as a journal deadline
# unless that file lists it as journal-imposed.
JOURNAL_NAME = "Spine Deformity (Springer / SRS)"
EDITORIAL_MANAGER = "https://www.editorialmanager.com/sdef/"
WRONG_PORTAL = "https://www.editorialmanager.com/spde/"
DEADLINE_AS_OF = "2026-08-22"


def parse_roadmap(filepath):
    """
    Parses the roadmap markdown file to extract tasks and calculate progress.

    Intentionally ignores any ``Target Submission Date``. Historical roadmaps
    used 2026-04-06 as a self-imposed Spine (LWW) 6-week target, which is not
    a journal-imposed deadline.
    """
    if not os.path.exists(filepath):
        return None, f"Roadmap file not found at {filepath}"

    with open(filepath, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    total_tasks = 0
    completed_tasks = 0
    phases = {}
    current_phase = None
    next_milestones = []

    start_date_match = re.search(r'\*\*Start Date:\*\* (\d{4}-\d{2}-\d{2})', content)
    start_date = datetime.datetime.strptime(start_date_match.group(1), '%Y-%m-%d').date() if start_date_match else None

    for line in lines:
        if line.startswith('## Phase'):
            current_phase = line.strip().replace('## ', '')
            phases[current_phase] = {'total': 0, 'completed': 0}

        if line.strip().startswith('- ['):
            total_tasks += 1
            if current_phase:
                phases[current_phase]['total'] += 1

            if line.strip().startswith('- [x]'):
                completed_tasks += 1
                if current_phase:
                    phases[current_phase]['completed'] += 1
            elif line.strip().startswith('- [ ]'):
                if len(next_milestones) < 3:
                    task = line.strip().replace('- [ ]', '').strip()
                    task = task.replace('**', '')
                    if ':' in task:
                        task = task.split(':')[0]
                    next_milestones.append(task)

    percent_complete = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'percent_complete': percent_complete,
        'phases': phases,
        'start_date': start_date,
        'target_date': None,
        'next_milestones': next_milestones
    }, None


def calculate_projection(data):
    """
    Internal velocity estimate from checkbox counts. Not a journal deadline.
    """
    if not data['start_date']:
        return "Unknown (Start Date missing)"

    today = datetime.date.today()
    days_elapsed = (today - data['start_date']).days

    if days_elapsed <= 0:
        days_elapsed = 1

    velocity = data['completed_tasks'] / days_elapsed

    if velocity <= 0:
        return "Unknown (No tasks completed yet)"

    tasks_remaining = data['total_tasks'] - data['completed_tasks']
    days_remaining_est = tasks_remaining / velocity

    expected_date = today + datetime.timedelta(days=int(days_remaining_est))

    return expected_date


def generate_report(data):
    """
    Generates a formatted daily update report.
    """
    today = datetime.date.today()
    expected_date = calculate_projection(data)

    report = f"""# Daily Update: Spine Deformity Submission

**Date:** {today}
**Target Journal:** {JOURNAL_NAME}
**Backup:** Spine (LWW) only if Spine Deformity desks the paper
**Editorial Manager:** {EDITORIAL_MANAGER}
**Wrong portal:** {WRONG_PORTAL} is a different journal — do not use it.
**Journal-imposed deadline:** none as of {DEADLINE_AS_OF}
**Optional AI/ML collection:** Springer lists Status: Open / deadline Ongoing as of {DEADLINE_AS_OF}. Original cutoff 20 May 2026 23:59 CST is past. Guest editors include Carl-Éric Aubin (omit as suggested reviewer if that collection is selected).
**Stale dates (not clocks):** 2026-04-06 was a self-imposed 6-week *Spine* (LWW, IF 3.30) target from start 2026-02-23. 2026-09-15 was an invented internal date and is not used.
**Why:** Live track in CITATION.cff, cover letter, and manuscript/main.tex. Canonical facts: JOURNAL_TRACK.md.
**Fit score:** Computational/hypothesis-generating original article. Patient-level validation is still a gap (see REMAINING_ITEMS.md).
**Strategy:** Submit the in-repo theory + computational results + open SpineWeb geometry check; do not invent a clinical cohort.

## Status Overview
- **Percent Complete:** {data['percent_complete']:.1f}%
- **Tasks Completed:** {data['completed_tasks']} / {data['total_tasks']}
- **Internal velocity projection (NOT a journal deadline):** {expected_date}

## Phase Breakdown
"""

    active_phase = "None"
    for phase, stats in data['phases'].items():
        phase_percent = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status_icon = "✅" if phase_percent == 100 else "🔄" if phase_percent > 0 else "⚪"
        report += f"- {status_icon} **{phase}:** {phase_percent:.1f}% ({stats['completed']}/{stats['total']})\n"

        if phase_percent < 100 and active_phase == "None":
            active_phase = phase

    report += f"\n**Current Focus:** {active_phase}\n"

    report += "\n## Next Milestones\n"
    next_milestones = data.get('next_milestones') or []
    if next_milestones:
        for i, milestone in enumerate(next_milestones, 1):
            report += f"{i}. {milestone}\n"
    else:
        report += "No milestones remaining!\n"

    report += "\nRun `python scripts/spine_daily_update.py` to regenerate this report."

    return report


def save_report(report):
    """
    Saves the report to a file with the current date.
    """
    today = datetime.date.today()
    output_dir = "reports/daily_updates"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"{today}_spine_update.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        f.write(report)

    latest_filepath = os.path.join("reports", "daily_update_latest.md")
    with open(latest_filepath, 'w') as f:
        f.write(report)

    return filepath


if __name__ == "__main__":
    roadmap_path = "docs/spine_submission_roadmap.md"
    data, error = parse_roadmap(roadmap_path)

    if error:
        print(error)
        sys.exit(1)
    else:
        report = generate_report(data)
        print(report)
        saved_path = save_report(report)
        print(f"\nReport saved to: {saved_path}")
