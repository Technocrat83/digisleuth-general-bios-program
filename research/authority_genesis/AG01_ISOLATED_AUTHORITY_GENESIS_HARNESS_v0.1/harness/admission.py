import json
from pathlib import Path
def validate_admission(path, expected):
    token=json.loads(Path(path).read_text())
    return token.get("single_use") is True and all(token.get(k)==v for k,v in expected.items())
def mint_admission(*a,**k):
    raise PermissionError("ValidateAdmission != GrantAdmission")
