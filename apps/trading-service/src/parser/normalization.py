import re
from dataclasses import dataclass
from typing import List
from src.parser.constants import UNICODE_DASHES

@dataclass
class NormalizationResult:
    original_text: str
    normalized_text: str
    normalized_lines: List[str]

def normalize_text(raw_text: str) -> NormalizationResult:
    if not raw_text:
        return NormalizationResult(original_text="", normalized_text="", normalized_lines=[])

    # 1. Normalize line endings (CRLF -> LF)
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Replace non-breaking spaces & tabs with standard space
    text = text.replace("\xa0", " ").replace("\t", " ")

    # 3. Normalize unicode dashes to standard ASCII dash (-)
    for dash in UNICODE_DASHES:
        text = text.replace(dash, "-")

    # 4. Normalize curly apostrophes
    text = text.replace("’", "'").replace("‘", "'")

    # 5. Split lines and strip each line
    lines = [line.strip() for line in text.split("\n")]
    
    # Remove consecutive empty lines (keep at most single line separation if present)
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                cleaned_lines.append("")
                prev_empty = True
        else:
            # Collapse multiple spaces within line
            line_single_space = re.sub(r" +", " ", line)
            cleaned_lines.append(line_single_space)
            prev_empty = False

    # Remove leading/trailing empty lines
    while cleaned_lines and cleaned_lines[0] == "":
        cleaned_lines.pop(0)
    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()

    normalized_text = "\n".join(cleaned_lines)
    non_empty_lines = [l for l in cleaned_lines if l != ""]

    return NormalizationResult(
        original_text=raw_text,
        normalized_text=normalized_text,
        normalized_lines=non_empty_lines
    )
