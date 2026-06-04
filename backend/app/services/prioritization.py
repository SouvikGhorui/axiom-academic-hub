from datetime import datetime
import math

IMPACT_DEFAULTS = {
    "EXAM": 85.0, 
    "PROJECT": 70.0, 
    "HOMEWORK": 45.0, 
    "READING": 20.0
}

def calculate_urgency(due_date: datetime, now: datetime) -> float:
    if due_date is None:
        return 10.0
    delta_days = max(0.01, (due_date - now).total_seconds() / 86400)
    return min(100.0, 100.0 / (delta_days ** 1.5))

def calculate_impact(task_type: str, weight_pct: float | None) -> float:
    if weight_pct is not None and 0 < weight_pct <= 100:
        return float(weight_pct)
    return IMPACT_DEFAULTS.get(task_type, 30.0)

def calculate_effort_pressure(effort_hrs: float, due_date: datetime, now: datetime) -> float:
    if due_date is None:
        delta_days = 7.0
    else:
        delta_days = max(0.1, (due_date - now).total_seconds() / 86400)
    burn_rate = (effort_hrs or 1.0) / delta_days
    return min(100.0, burn_rate * 20.0)

def calculate_priority_score(
    due_date: datetime,
    task_type: str,
    effort_hrs: float,
    weight_pct: float | None = None,
    now: datetime | None = None,
) -> float:
    now = now or datetime.utcnow()
    U = calculate_urgency(due_date, now)
    I = calculate_impact(task_type, weight_pct)
    E = calculate_effort_pressure(effort_hrs, due_date, now)
    return round((U * 0.50) + (I * 0.30) + (E * 0.20), 2)
