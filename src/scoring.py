from src.reference_data import SCORING_OPTIONS, THRESHOLDS


def score_metric(dimension: str, metric: str, option_text: str) -> int:
    """Return the score (1-5) for the given option text."""
    dim_options = SCORING_OPTIONS.get(dimension)
    if dim_options is None:
        raise ValueError(f"Unknown dimension: {dimension}")
    metric_options = dim_options.get(metric)
    if metric_options is None:
        raise ValueError(f"Unknown metric: {metric} in dimension {dimension}")
    for option, score in metric_options:
        if option == option_text:
            return score
    raise ValueError(f"Unknown option '{option_text}' for {dimension}.{metric}")


def score_dimension(scores: list) -> float:
    """Return the average score for a dimension. Raises if scores is empty."""
    if not scores:
        raise ValueError("No scores provided to score_dimension")
    return sum(scores) / len(scores)


def detect_tech_debt(scores: list) -> bool:
    """Return True if average >= THRESHOLDS['avg'] OR max >= THRESHOLDS['max']."""
    if not scores:
        return False
    avg = sum(scores) / len(scores)
    maximum = max(scores)
    return avg >= THRESHOLDS["avg"] or maximum >= THRESHOLDS["max"]
