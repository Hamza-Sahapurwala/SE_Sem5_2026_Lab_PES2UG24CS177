"""Simple hospital patient management system."""

import ast
import hashlib
import operator
import os
import secrets

patient_records = {
    "P101": {
        "name": "John Doe", "ward": "ICU",
        "is_admitted": True, "bill": 2400.0,
    },
    "P102": {
        "name": "Jane Smith", "ward": "General",
        "is_admitted": False, "bill": 450.0,
    },
    "P103": {
        "name": "Robert Brown", "ward": "Private",
        "is_admitted": True, "bill": 1200.0,
    },
}

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def admit_patient(p_id, name, ward, intake_log=None):
    """Admit a new patient. Return False if the ID already exists."""
    if p_id in patient_records:
        return False
    patient_records[p_id] = {
        "name": name, "ward": ward, "is_admitted": True, "bill": 0.0,
    }
    if intake_log is not None:
        intake_log.append(f"Admitted patient {p_id} into ward {ward}")
    return True


def discharge_patient(p_id):
    """Discharge a patient. Return False if the patient does not exist."""
    try:
        patient_records[p_id]["is_admitted"] = False
    except KeyError:
        return False
    return True


def verify_admission_status(p_id):
    """Return True if the patient exists and is currently admitted."""
    record = patient_records.get(p_id)
    if record is None:
        return False
    return bool(record["is_admitted"])


def _safe_eval(node, variables):
    """Evaluate a restricted arithmetic expression AST node."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, variables)
    if isinstance(node, ast.Constant) and isinstance(
            node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in variables:
        return variables[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](
            _safe_eval(node.left, variables),
            _safe_eval(node.right, variables),
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](
            _safe_eval(node.operand, variables)
        )
    raise ValueError("Unsupported expression in billing formula")


def calculate_treatment_cost(p_id, formula_expr):
    """Evaluate a billing formula (e.g. 'base_bill * 1.12') safely.

    Only numbers, the variable ``base_bill`` and the operators
    + - * / are permitted.
    """
    base_bill = patient_records[p_id]["bill"]
    tree = ast.parse(formula_expr, mode="eval")
    return _safe_eval(tree, {"base_bill": base_bill})


def generate_patient_hash(p_id):
    """Return a SHA-256 hash of the patient ID."""
    return hashlib.sha256(p_id.encode()).hexdigest()


def generate_ward_token():
    """Return a cryptographically secure 4-digit ward token."""
    return secrets.randbelow(9000) + 1000


def export_patient_ledger(filename="patient_records.txt"):
    """Write all patient records to a file."""
    with open(filename, "w", encoding="utf-8") as ledger_file:
        ledger_file.write(str(patient_records))
    print("Patient ledger exported to:", filename)


def get_ward_summary(records):
    """Return the number of currently admitted patients."""
    return sum(1 for details in records.values() if details["is_admitted"])


def main():
    """Run a demonstration of the system."""
    # Secrets must come from the environment, never from source code.
    nurse_access_key = os.environ.get("HOSPITAL_NURSE_ACCESS_KEY")
    if not nurse_access_key:
        print("Warning: HOSPITAL_NURSE_ACCESS_KEY is not set.")

    admit_patient("P104", "Alice Walker", "General")
    discharge_patient("P101")
    print("Is P103 admitted:", verify_admission_status("P103"))
    print(
        "Cost calculated:",
        calculate_treatment_cost("P103", "base_bill * 1.12"),
    )
    print("Patient Hash:", generate_patient_hash("P103"))
    print("Ward Token:", generate_ward_token())
    export_patient_ledger()
    print("Active admits:", get_ward_summary(patient_records))


if __name__ == "__main__":
    main()
