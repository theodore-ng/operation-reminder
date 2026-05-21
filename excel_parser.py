import openpyxl
from typing import List, Dict

from config import (
    DEPARTMENT_NAME, COL_THU, COL_STT, COL_PMO, COL_TTCA,
    COL_KHOA, COL_TEN, COL_TUOI, COL_CHAN_DOAN, COL_PHAU_THUAT,
    COL_BAC_SI, COL_GHI_CHU
)


def parse_operations(filepath: str, department: str = DEPARTMENT_NAME) -> List[Dict]:
    wb = openpyxl.load_workbook(filepath, data_only=True)
    operations = []

    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            if not _is_data_row(row):
                continue

            khoa = _cell(row, COL_KHOA)
            if khoa and khoa.strip().lower() == department.strip().lower():
                operations.append({
                    "thu": _cell(row, COL_THU),
                    "stt": _cell(row, COL_STT),
                    "pmo": _cell(row, COL_PMO),
                    "ttca": _cell(row, COL_TTCA),
                    "khoa": khoa.strip(),
                    "ten": _cell(row, COL_TEN),
                    "tuoi": _cell(row, COL_TUOI),
                    "chan_doan": _cell(row, COL_CHAN_DOAN),
                    "phau_thuat": _cell(row, COL_PHAU_THUAT),
                    "bac_si": _cell(row, COL_BAC_SI),
                    "ghi_chu": _cell(row, COL_GHI_CHU),
                })

    return operations


def _is_data_row(row) -> bool:
    if not row or len(row) <= COL_KHOA:
        return False
    if not any(row):
        return False
    # Skip header rows — first cell in data rows is a numeric day (e.g. 5)
    first = row[0]
    return isinstance(first, (int, float)) and 1 <= first <= 7


def _cell(row, index: int) -> str:
    if index >= len(row) or row[index] is None:
        return ""
    val = row[index]
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    return str(val).strip()
