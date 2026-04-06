import re
from typing import Optional
from .generator import get_all_cvars

DANGEROUS_COMMANDS = {
    "exec",
    "download",
    "upload",
    "rcon",
    "rcon_password",
    "sv_cheats",
    "sv_password",
    "connect",
    "retry",
    "quit",
    "exit",
    "kill",
    "kickall",
    "ban",
    "banid",
    "removeid",
    "writecfg",
    "developer",
    "alias",
    "cl_filterstuffcmd",
}

BIND_PATTERN = re.compile(r'^bind\s+"([^"]+)"\s+"([^"]+)"$', re.IGNORECASE)
CVAR_PATTERN = re.compile(r'^(\S+)\s+"([^"]*)"$')
COMMENT_PATTERN = re.compile(r"^\s*//")


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.valid_count: int = 0
        self.total_count: int = 0

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


def _build_cvar_lookup() -> dict:
    """Flatten the CVAR database into a single lookup dict."""
    cvars_db = get_all_cvars()
    lookup: dict = {}
    for _category, cvars in cvars_db.items():
        for cvar_name, cvar_info in cvars.items():
            lookup[cvar_name.lower()] = cvar_info
    return lookup


def validate_value(cvar_name: str, value: str, cvar_info: dict) -> Optional[str]:
    """Validate a single CVAR value against its spec. Returns error string or None."""
    cvar_type = cvar_info.get("type", "string")

    if "values" in cvar_info:
        if value not in cvar_info["values"]:
            return f"{cvar_name}: value '{value}' not in allowed values {cvar_info['values']}"

    if "range" in cvar_info:
        try:
            num_val = float(value)
            lo, hi = cvar_info["range"]
            if num_val < lo or num_val > hi:
                return f"{cvar_name}: value {value} out of range [{lo}, {hi}]"
        except ValueError:
            return f"{cvar_name}: expected numeric value, got '{value}'"

    if cvar_type == "int":
        try:
            if "." in value:
                float(value)
            else:
                int(value)
        except ValueError:
            return f"{cvar_name}: expected integer, got '{value}'"

    if cvar_type == "float":
        try:
            float(value)
        except ValueError:
            return f"{cvar_name}: expected float, got '{value}'"

    return None


def validate_cfg_text(cfg_text: str) -> ValidationResult:
    """Validate a full .cfg file content."""
    result = ValidationResult()
    cvar_lookup = _build_cvar_lookup()

    for line_num, line in enumerate(cfg_text.splitlines(), 1):
        line = line.strip()
        if not line or COMMENT_PATTERN.match(line):
            continue

        result.total_count += 1

        bind_match = BIND_PATTERN.match(line)
        if bind_match:
            result.valid_count += 1
            cmd = bind_match.group(2).split(";")[0].strip().lstrip("+").lstrip("-")
            if cmd.lower() in DANGEROUS_COMMANDS:
                result.add_warning(
                    f"Line {line_num}: potentially dangerous bind command '{cmd}'"
                )
            continue

        cvar_match = CVAR_PATTERN.match(line)
        if cvar_match:
            cvar_name = cvar_match.group(1)
            cvar_value = cvar_match.group(2)

            if cvar_name.lower() in DANGEROUS_COMMANDS:
                result.add_warning(
                    f"Line {line_num}: dangerous command '{cvar_name}'"
                )
                continue

            cvar_info = cvar_lookup.get(cvar_name.lower())
            if cvar_info:
                err = validate_value(cvar_name, cvar_value, cvar_info)
                if err:
                    result.add_error(f"Line {line_num}: {err}")
                else:
                    result.valid_count += 1
            else:
                result.valid_count += 1
            continue

        parts = line.split(None, 1)
        if parts:
            cmd = parts[0].lower()
            if cmd in DANGEROUS_COMMANDS:
                result.add_warning(
                    f"Line {line_num}: dangerous command '{cmd}'"
                )
            else:
                result.valid_count += 1

    return result


def validate_config_dict(settings: dict[str, str]) -> ValidationResult:
    """Validate a dict of CVAR -> value pairs."""
    result = ValidationResult()
    cvar_lookup = _build_cvar_lookup()

    for cvar_name, value in settings.items():
        result.total_count += 1

        if cvar_name.lower() in DANGEROUS_COMMANDS:
            result.add_warning(f"Dangerous command: {cvar_name}")
            continue

        cvar_info = cvar_lookup.get(cvar_name.lower())
        if cvar_info:
            err = validate_value(cvar_name, value, cvar_info)
            if err:
                result.add_error(err)
            else:
                result.valid_count += 1
        else:
            result.valid_count += 1

    return result


def check_dangerous(cfg_text: str) -> list[str]:
    """Quick scan for dangerous commands, returns list of warnings."""
    warnings: list[str] = []
    for line_num, line in enumerate(cfg_text.splitlines(), 1):
        line = line.strip()
        if not line or COMMENT_PATTERN.match(line):
            continue
        first_word = line.split()[0].lower().strip('"')
        if first_word in DANGEROUS_COMMANDS:
            warnings.append(f"Line {line_num}: dangerous command '{first_word}'")
        if first_word == "bind":
            parts = line.split('"')
            if len(parts) >= 4:
                bound_cmd = parts[3].split(";")[0].strip().lstrip("+").lstrip("-")
                if bound_cmd.lower() in DANGEROUS_COMMANDS:
                    warnings.append(
                        f"Line {line_num}: dangerous bind to '{bound_cmd}'"
                    )
    return warnings
