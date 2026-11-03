"""Write participant-facing and research records to the local outputs folder."""

import json
import re
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
FEEDBACK_DIR = OUTPUT_DIR / "feedback"
ANALYSIS_DIR = OUTPUT_DIR / "analysis"
CONTENT_DIR = OUTPUT_DIR / "content"
COUNTER_PATH = OUTPUT_DIR / ".participant_counter"


def ensure_output_dirs():
    for directory in (FEEDBACK_DIR, ANALYSIS_DIR, CONTENT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def allocate_participant_id():
    """Allocate a persistent, zero-padded participant number."""
    ensure_output_dirs()
    try:
        last_number = int(COUNTER_PATH.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        last_number = 0

    for path in OUTPUT_DIR.rglob("*"):
        match = re.match(r"^(\d+)_", path.name)
        if match:
            last_number = max(last_number, int(match.group(1)))

    next_number = last_number + 1
    COUNTER_PATH.write_text(str(next_number), encoding="utf-8")
    return f"{next_number:02d}"


def _record_stem(participant_id, session_id):
    return f"{participant_id}_{session_id}"


def save_conversation_text(record):
    ensure_output_dirs()
    path = CONTENT_DIR / f"{_record_stem(record['participant_id'], record['session_id'])}.txt"
    lines = [
        f"Participant: {record['participant_id']}",
        f"Session: {record['session_id']}",
        f"Created: {record['created_at']}",
        f"Status: {record['status']}",
        "",
    ]
    for message in record.get("messages", []):
        lines.extend([
            f"[{message.get('timestamp', '')}] {message.get('role', '').upper()}",
            message.get("content", ""),
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")


def save_analysis_text(record):
    ensure_output_dirs()
    path = ANALYSIS_DIR / f"{_record_stem(record['participant_id'], record['session_id'])}.txt"
    path.write_text(
        "TeachCL analysis record\n\n" + json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_feedback(participant_id, session_id, feedback_text, chart_bytes):
    ensure_output_dirs()
    stem = _record_stem(participant_id, session_id)
    (FEEDBACK_DIR / f"{stem}.txt").write_text(feedback_text, encoding="utf-8")
    (FEEDBACK_DIR / f"{stem}.png").write_bytes(chart_bytes)
