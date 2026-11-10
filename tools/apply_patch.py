from pathlib import Path
import sys

if len(sys.argv) != 4:
    print("Usage: apply_patch.py <file> <old> <new>")
    raise SystemExit(1)

file_path = Path(sys.argv[1])
old_text = sys.argv[2]
new_text = sys.argv[3]

text = file_path.read_text()

if old_text not in text:
    print("ERROR: Pattern not found")
    raise SystemExit(1)

text = text.replace(old_text, new_text, 1)

file_path.write_text(text)

print("SUCCESS")
