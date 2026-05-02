from datetime import datetime

def calculate_priority_score(due_date: datetime, task_type: str, effort_hrs: float, current_time: datetime = None) -> float:
    """
    Calculates the priority score based on Urgency, Impact, and Effort factors.
    Score = (Urgency * 0.5) + (Impact * 0.3) + (Effort * 0.2)
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    # 1. Urgency Factor
    if due_date:
        days_left = max(0, (due_date - current_time).total_seconds() / 86400)
        if days_left == 0:
            urgency = 100.0
        else:
            urgency = min(100.0, 100.0 / (days_left ** 1.5))
    else:
        urgency = 10.0 # Low default if no due date
        
    # 2. Impact Factor
    impact_map = {
        "EXAM": 100.0,
        "PROJECT": 80.0,
        "HOMEWORK": 50.0,
        "READING": 20.0
    }
    impact = impact_map.get(task_type, 30.0)
    
    # 3. Effort Factor
    if due_date:
        days_left = max(0.5, (due_date - current_time).total_seconds() / 86400)
    else:
        days_left = 7.0
    burn_rate = effort_hrs / days_left
    effort_factor = min(100.0, burn_rate * 20.0)
    
    # Weights
    W1, W2, W3 = 0.5, 0.3, 0.2
    
    score = (urgency * W1) + (impact * W2) + (effort_factor * W3)
    return score
