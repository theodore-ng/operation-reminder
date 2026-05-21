from datetime import datetime
from typing import Dict, List

from config import CALENDAR_ID, GEMINI_API_KEY, TIMEZONE
from translator import summarize_schedule

# Fallback keyword → category mapping (used when Gemini is unavailable)
_CATEGORY_RULES = [
    ("CARDIAC", [
        "van hai lá", "van động mạch chủ", "van ba lá", "van phổi",
        "sửa van", "thay van", "mạch vành", "cabg", "cầu nối vành",
        "tim hở", "vách liên", "màng ngoài tim",
        "máy tạo nhịp", "pacemaker", "icd", "loạn nhịp tim",
        "bít ống động mạch", "bít thông liên", "thông liên nhĩ", "thông liên thất",
    ]),
    ("VENOUS", [
        "tĩnh mạch", "suy tĩnh mạch", "laser nội mạch", "giãn tĩnh mạch",
        "stripping", "điều trị tĩnh mạch",
    ]),
    ("PAD_OPEN", [
        "mạch máu ngoại vi", "bypass", "cầu nối động mạch", "embolectomy",
        "lấy huyết khối động mạch", "endarterectomy", "phẫu thuật động mạch chi",
        "phẫu thuật động mạch đùi", "phẫu thuật động mạch chậu",
    ]),
    ("PAD_INTERVENTION", [
        "can thiệp động mạch", "stent động mạch", "nong động mạch",
        "angioplasty", "can thiệp nội mạch chi",
    ]),
]

_SECTION_LABEL = {
    "CARDIAC":          "CARDIAC SURGERY",
    "VENOUS":           "CHRONIC VENOUS INSUFFICIENCY",
    "PAD_OPEN":         "PERIPHERAL ARTERIAL DISEASE — OPEN SURGERY",
    "PAD_INTERVENTION": "PERIPHERAL ARTERIAL DISEASE — ENDOVASCULAR INTERVENTION",
    "OTHER":            "OTHER VASCULAR PROCEDURE",
}

_TITLE_ABBR = {
    "CARDIAC":          "Cardiac",
    "VENOUS":           "Venous",
    "PAD_OPEN":         "PAD Open",
    "PAD_INTERVENTION": "PAD Intervention",
    "OTHER":            "Other",
}

_CATEGORY_ORDER = ["CARDIAC", "VENOUS", "PAD_OPEN", "PAD_INTERVENTION", "OTHER"]


def _classify(op: Dict) -> str:
    surgery = (op.get("phau_thuat") or "").lower()
    for cat, keywords in _CATEGORY_RULES:
        if any(kw in surgery for kw in keywords):
            return cat
    return "OTHER"


def grouped_event_exists(service, operation_date: datetime) -> bool:
    date_str = operation_date.strftime("%Y-%m-%d")
    result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=f"{date_str}T00:00:00+07:00",
        timeMax=f"{date_str}T23:59:59+07:00",
        q="OPERATION SCHEDULE",
        singleEvents=True,
    ).execute()
    return len(result.get("items", [])) > 0


def _build_from_gemini(operations: List[Dict]) -> tuple[str, str] | None:
    """Call Gemini to group and translate all cases. Returns (title_abbr_str, description) or None."""
    groups = summarize_schedule(operations)
    if not groups:
        return None

    n_total = len(operations)
    abbr_parts = []
    sections = []

    for group in groups:
        name = group.get("name", "Unknown Group")
        abbr = group.get("abbr", name)
        cases = group.get("cases", [])
        n = len(cases)
        abbr_parts.append(f"{n} {abbr}")

        header = f"{name.upper()} — {n} case{'s' if n != 1 else ''}"
        lines = [header]
        for case in cases:
            lines.append(f"\nRoom {case.get('room', '?')}, Case {case.get('case_no', '?')}")
            lines.append(f"  {case.get('name', '?')}, {case.get('age', '?')} y/o")
            lines.append(f"  Dx: {case.get('dx', '—')}")
            lines.append(f"  Procedure: {case.get('procedure', '—')}")
        sections.append("\n".join(lines))

    title = (
        f"OR Schedule · {n_total} case{'s' if n_total != 1 else ''}"
        f" ({' · '.join(abbr_parts)})"
    )
    description = "\n\n◆ ─ ◆\n\n".join(sections)
    return title, description


def _build_fallback(operations: List[Dict]) -> tuple[str, str]:
    """Keyword-based grouping fallback (Vietnamese, no translation)."""
    groups: dict[str, list] = {}
    for op in operations:
        cat = _classify(op)
        groups.setdefault(cat, []).append(op)

    abbr_parts = [
        f"{len(groups[c])} {_TITLE_ABBR[c]}"
        for c in _CATEGORY_ORDER
        if c in groups
    ]
    n_total = len(operations)
    title = (
        f"OR Schedule · {n_total} case{'s' if n_total != 1 else ''}"
        f" ({' · '.join(abbr_parts)})"
    )

    sections = []
    for cat in _CATEGORY_ORDER:
        if cat not in groups:
            continue
        ops = groups[cat]
        n = len(ops)
        header = f"{_SECTION_LABEL[cat]} — {n} case{'s' if n != 1 else ''}"
        bar = "━" * len(header)
        lines = [header, bar]
        for op in ops:
            name = (op.get("ten") or "Unknown").upper()
            age = op.get("tuoi") or "?"
            room = op.get("pmo") or "?"
            case_no = op.get("ttca") or "?"
            dx = op.get("chan_doan") or "—"
            procedure = op.get("phau_thuat") or "—"
            lines.append(f"\nRoom {room}, Case {case_no}")
            lines.append(f"  {name}, {age} y/o")
            lines.append(f"  Dx: {dx}")
            lines.append(f"  Procedure: {procedure}")
        sections.append("\n".join(lines))

    return title, "\n\n".join(sections)


def create_grouped_event(service, operations: List[Dict], operation_date: datetime) -> dict:
    if GEMINI_API_KEY:
        result = _build_from_gemini(operations)
    else:
        result = None

    if result is None:
        title, description = _build_fallback(operations)
    else:
        title, description = result

    date_str = operation_date.strftime("%Y-%m-%d")
    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": f"{date_str}T07:30:00", "timeZone": TIMEZONE},
        "end": {"dateTime": f"{date_str}T16:30:00", "timeZone": TIMEZONE},
        "colorId": "11",  # Tomato red
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 90},  # 6 AM on operation day
            ],
        },
    }

    return service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
