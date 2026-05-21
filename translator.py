import json

from google import genai
from google.genai import types

from config import GEMINI_API_KEY

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def summarize_schedule(operations: list[dict]) -> list[dict] | None:
    """Send all Pt tim cases to Gemini for grouping, translation, and summarization.

    Returns a list of groups or None if the API key is missing or the call fails:
    [
        {
            "name": "Full academic group name",
            "abbr": "Short 2-3 word title",
            "cases": [
                {"room": ..., "case_no": ..., "name": ..., "age": ..., "dx": ..., "procedure": ...}
            ]
        }
    ]
    """
    if not GEMINI_API_KEY:
        return None

    case_lines = []
    for i, op in enumerate(operations, 1):
        case_lines.append(
            f"Case {i}: Room {op.get('pmo', '?')}, Position {op.get('ttca', '?')}, "
            f"Patient: {(op.get('ten') or '').upper()}, Age: {op.get('tuoi', '?')}, "
            f"Diagnosis: {op.get('chan_doan', '')}, "
            f"Procedure: {op.get('phau_thuat', '')}"
        )

    prompt = f"""You are a medical secretary for a Cardiac & Vascular Surgery department.
Below is today's raw operation schedule (data may be in Vietnamese).

Operating room legend — use these exact labels in the "room" field:
- TIM → Heart Surgery OR
- All other codes: keep as-is (e.g. 6B, 7A)

Tasks:
1. Group cases by surgery type using proper academic medical terminology in English.
2. Choose concise clinical category names only — the disease/condition, not the procedure (e.g. "Cardiac Surgery", "Chronic Venous Insufficiency", "Peripheral Arterial Disease"). Do not include procedure names or techniques in the group name. You may introduce new groups if appropriate.
3. For "abbr": use a short 2–3 word version of the group name (e.g. "Venous Insufficiency", "Cardiac Surgery", "Arterial Disease").
4. Translate Diagnosis and Procedure to English using correct medical terminology.
5. Keep patient names in uppercase.
6. Apply the room legend above; preserve case position exactly as given.

Return ONLY valid JSON — no markdown, no extra text:
{{
  "groups": [
    {{
      "name": "Full academic group name",
      "abbr": "Short 2-3 word title",
      "cases": [
        {{
          "room": "room code",
          "case_no": "position number",
          "name": "PATIENT NAME",
          "age": "age",
          "dx": "Diagnosis in English",
          "procedure": "Procedure in English"
        }}
      ]
    }}
  ]
}}

Raw schedule:
{chr(10).join(case_lines)}"""

    try:
        response = _get_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
        return data.get("groups", [])
    except Exception as e:
        print(f"[translator] Gemini error: {e}")
        return None
