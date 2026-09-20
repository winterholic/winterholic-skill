from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


CONNECTOR_MARKERS = {"marker", "marker-start", "marker-mid", "marker-end"}
PATH_TOKEN_RE = re.compile(r"[A-Za-z]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
PATH_PARAM_COUNTS = {
    "M": 2,
    "L": 2,
    "H": 1,
    "V": 1,
    "C": 6,
    "S": 4,
    "Q": 4,
    "T": 2,
    "A": 7,
    "Z": 0,
}


def diagnostic(
    code: str,
    subject: str,
    message: str,
    evidence: dict[str, Any],
    supported_fixes: list[str],
) -> dict[str, Any]:
    return {
        "code": code,
        "subject": subject,
        "message": message,
        "evidence": evidence,
        "supported_fixes": supported_fixes,
    }


class GeometryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.diagnostics: list[dict[str, Any]] = []
        self.line_number = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.line_number = self.getpos()[0]
        tag = tag.casefold()
        if tag not in {"line", "path"}:
            return
        data = {name.casefold(): value or "" for name, value in attrs}
        if not CONNECTOR_MARKERS.intersection(data) and "data-diagram-connector" not in data:
            return
        exemption = data.get("data-geometry-exempt", "")
        if exemption == "radial":
            return
        if exemption:
            identifier = data.get("id", "")
            subject = f"#{identifier}" if identifier else f"{tag}:{self.line_number}"
            self.diagnostics.append(
                diagnostic(
                    "geometry/unknown-exemption",
                    subject,
                    f"Unknown geometry exemption: {exemption}",
                    {"exemption": exemption, "line": self.line_number},
                    ["remove the exemption", "use the documented radial exemption"],
                )
            )
            return
        if tag == "path":
            segment = first_diagonal_path_segment(data.get("d", ""))
            if segment is None:
                return
            identifier = data.get("id", "")
            subject = f"#{identifier}" if identifier else f"path:{self.line_number}"
            self.diagnostics.append(
                diagnostic(
                    "geometry/diagonal-segment",
                    subject,
                    "Connector paths must not contain explicit diagonal L segments.",
                    {"from": segment[0], "to": segment[1], "line": self.line_number},
                    [
                        "replace the L segment with H/V segments and a rounded Q elbow",
                        "use a documented type-specific curved connector instead of L",
                    ],
                )
            )
            return
        try:
            x1 = float(data["x1"])
            y1 = float(data["y1"])
            x2 = float(data["x2"])
            y2 = float(data["y2"])
        except (KeyError, ValueError):
            return
        if x1 == x2 or y1 == y2:
            return
        identifier = data.get("id", "")
        subject = f"#{identifier}" if identifier else f"line:{self.line_number}"
        self.diagnostics.append(
            diagnostic(
                "geometry/diagonal-connector",
                subject,
                "Connector lines must share an x or y axis; use a rounded orthogonal path.",
                {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "line": self.line_number},
                [
                    "replace the line with an H/V path and a rounded Q elbow",
                    "realign the endpoints onto one shared axis",
                ],
            )
        )


def first_diagonal_path_segment(
    path_data: str,
) -> tuple[list[float], list[float]] | None:
    tokens = PATH_TOKEN_RE.findall(path_data)
    current = (0.0, 0.0)
    subpath_start = current
    command = ""
    index = 0
    move_seen = False
    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            if command.upper() == "Z":
                current = subpath_start
                command = ""
                continue
        if not command:
            return None
        upper = command.upper()
        count = PATH_PARAM_COUNTS.get(upper)
        if count is None or index + count > len(tokens):
            return None
        try:
            values = [float(value) for value in tokens[index : index + count]]
        except ValueError:
            return None
        index += count
        relative = command.islower()
        previous = current
        if upper in {"M", "L", "T"}:
            target = (values[-2], values[-1])
            if relative:
                target = (current[0] + target[0], current[1] + target[1])
            is_line = upper == "L" or (upper == "M" and move_seen)
            if is_line and target[0] != current[0] and target[1] != current[1]:
                return ([current[0], current[1]], [target[0], target[1]])
            current = target
            if upper == "M" and not move_seen:
                subpath_start = current
                move_seen = True
        elif upper == "H":
            current = (current[0] + values[0] if relative else values[0], current[1])
        elif upper == "V":
            current = (current[0], current[1] + values[0] if relative else values[0])
        elif upper in {"C", "S", "Q", "A"}:
            target = (values[-2], values[-1])
            current = (
                previous[0] + target[0] if relative else target[0],
                previous[1] + target[1] if relative else target[1],
            )
        if upper == "M":
            command = "l" if relative else "L"
    return None


def verify(path: Path) -> list[dict[str, Any]]:
    source = path.read_text(encoding="utf-8")
    parser = GeometryParser()
    parser.feed(source)
    parser.close()
    return parser.diagnostics
