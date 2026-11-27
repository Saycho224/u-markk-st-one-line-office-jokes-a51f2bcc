#!/usr/bin/env python3
"""Shredder fan-club joke — make.fun one-line office jokes entry.

The program carries exactly one joke line and publishes it as the
competition entry: it validates the line against the gate (UTF-8 text,
1-199 characters), writes it to ``entry.txt`` inside the output
directory the harness provides, and then proves the write by reading
the file back and comparing bytes, size and sha256 digest.

Nothing here reaches the network, spawns a process, or evaluates code:
the only environment value consulted is MAKEFUN_OUTPUT_DIR, used
purely as a directory path.
"""

import hashlib
import os
import sys

ENTRY = (
    "Our shredder jammed on a single sheet of paper, so now it has "
    "a maintenance contract, a warning label, and a fan club that "
    "feeds it one page a week."
)

MIN_CHARS = 1
MAX_CHARS = 199


def gate_problems(text):
    """Return a list of gate violations for *text* (empty means OK)."""
    problems = []
    if not isinstance(text, str):
        problems.append("entry is not text")
        return problems
    if len(text) < MIN_CHARS:
        problems.append("entry is empty")
    if len(text) > MAX_CHARS:
        problems.append(
            "entry is %d chars, over the %d-char limit"
            % (len(text), MAX_CHARS)
        )
    if text != text.strip():
        problems.append("entry has leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        problems.append("entry must be a single line")
    return problems


def to_bytes(text):
    """Encode the entry as UTF-8, refusing anything unencodable."""
    try:
        return text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise SystemExit("entry is not valid UTF-8: %s" % exc)


def fingerprint(data):
    """Hex sha256 of *data*."""
    return hashlib.sha256(data).hexdigest()


def resolve_output_dir():
    """Directory the harness wants the entry in (default /output)."""
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if not chosen:
        raise SystemExit("MAKEFUN_OUTPUT_DIR is set but empty")
    return chosen


def publish(text, out_dir):
    """Write *text* to entry.txt under *out_dir* and verify it back."""
    payload = to_bytes(text)
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    with open(target, "wb") as handle:
        handle.write(payload)
    with open(target, "rb") as handle:
        back = handle.read()
    if back != payload:
        raise SystemExit("round-trip mismatch: file differs from entry")
    print(
        "wrote %s (%d bytes, sha256 %s)"
        % (target, len(back), fingerprint(back))
    )
    return target


def run(argv=None):
    """Gate the entry, publish it, and report the verified digest."""
    problems = gate_problems(ENTRY)
    if problems:
        for problem in problems:
            print("gate failed: %s" % problem, file=sys.stderr)
        return 1
    target = publish(ENTRY, resolve_output_dir())
    print("entry OK: %d chars -> %s" % (len(ENTRY), target))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
