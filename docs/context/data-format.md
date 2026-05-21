# Data Format

## Excel column mapping (0-based indices, defined in `config.py`)

| Column | Index | Field |
|--------|-------|-------|
| Thu | 0 | Day of week |
| STT | 1 | Sequential number (not shown in reminder) |
| PMO | 2 | Operating room |
| TTCA | 3 | Case order within room |
| Khoa | 5 | Department — filter value: `Pt tim` |
| Ten | 6 | Patient name |
| Tuoi | 7 | Age |
| Chan doan | 8 | Diagnosis |
| Phau thuat | 9 | Surgery / procedure |
| Bac si | 10 | Surgeon |
| Ghi chu | 11 | Notes |

Data rows are identified by column 0 being an integer 1–7 (day of week).

## Surgery classification

**Primary (Gemini):** All cases are sent in one batch to `translator.py → summarize_schedule()`. Gemini chooses its own academic English category names and groups cases accordingly. Category names and abbreviations vary per schedule based on what Gemini decides is most clinically accurate.

**Fallback (no API key):** `calendar_creator.py → _CATEGORY_RULES` — keyword lists matched against `phau_thuat` in lowercase. First match wins.

| Key | Section header | Example keywords |
|-----|---------------|-----------------|
| `CARDIAC` | Cardiac Surgery | van hai lá, sửa van, mạch vành, máy tạo nhịp |
| `VENOUS` | Chronic Venous Insufficiency | tĩnh mạch, laser nội mạch, suy tĩnh mạch |
| `PAD_OPEN` | Peripheral Arterial Disease — Open Surgery | mạch máu ngoại vi, bypass, embolectomy |
| `PAD_INTERVENTION` | Peripheral Arterial Disease — Endovascular Intervention | stent động mạch, can thiệp nội mạch |
| `OTHER` | Other Vascular Procedure | fallback for unmatched cases |

## Operating room legend (passed to Gemini prompt)

| Raw code | Display label |
|----------|--------------|
| `TIM` | Heart Surgery OR |
| all others | kept as-is (e.g. `6B`, `7A`) |

## Calendar event format

**Title:**
```
OR Schedule · 5 cases (1 Valvular Heart Disease · 3 Venous Insufficiency · 1 Peripheral Arterial Disease)
```

**Body** — sections separated by `◆ ─ ◆`, groups ordered by Gemini:
```
VALVULAR HEART DISEASE — 1 case

Heart Surgery OR, Case 1
  PHẠM CÔNG CHUNG, 72 y/o
  Dx: Mitral Regurgitation
  Procedure: Endoscopic Mitral Valve Repair

◆ ─ ◆

CHRONIC VENOUS INSUFFICIENCY — 3 cases

Room 6B, Case 3
  NGUYỄN NGỌC NGHINH, 67 y/o
  Dx: Chronic Venous Insufficiency (Lower Extremity Varicose Veins)
  Procedure: Endovenous Laser Ablation
```

Diagnosis and procedure text is translated to English by Gemini using correct medical terminology.
