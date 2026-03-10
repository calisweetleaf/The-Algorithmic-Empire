from pathlib import Path

path = Path(r"C:/Users/treyr/Documents/algorithmic_empire/tools/python_production_doctor.py")
text = path.read_text(encoding="utf-8", errors="replace")
marker = 'if __name__ == "__main__":\n    main()'
idx = text.find(marker)
if idx == -1:
    raise SystemExit("marker not found")
trimmed = text[: idx + len(marker)] + "\n"
path.write_text(trimmed, encoding="utf-8")
print("trimmed_lines", len(trimmed.splitlines()))
