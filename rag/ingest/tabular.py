from __future__ import annotations
from pathlib import Path
import pandas as pd

def extract_excel_text(path: Path, max_rows_per_sheet: int = 5000) -> str:
    xl = pd.ExcelFile(path)
    out = []
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        out.append(f"## Sheet: {sheet}")
        out.append(f"Rows: {len(df)} | Cols: {len(df.columns)}")
        out.append("Columns: " + ", ".join(map(str, df.columns.tolist())))

        if len(df) > max_rows_per_sheet:
            sample = df.head(max_rows_per_sheet)
            out.append(f"(Showing first {max_rows_per_sheet} rows)\n")
            out.append(sample.to_csv(index=False))
        else:
            out.append(df.to_csv(index=False))
        out.append("")
    return "\n".join(out).strip()
