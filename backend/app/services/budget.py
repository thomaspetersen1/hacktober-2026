"""Deterministic budget math. The LLM never does arithmetic."""


def room_weights(rooms: int) -> list[float]:
    """Weight rooms so spending builds toward the big scare.

    Rooms ramp up linearly; the second-to-last room (the climax) gets a bonus
    and the final room (the exit) is kept modest.
    """
    if rooms == 1:
        return [1.0]
    weights = [1.0 + i * 0.25 for i in range(rooms)]
    climax = rooms - 2 if rooms >= 3 else rooms - 1
    weights[climax] *= 1.5
    if rooms >= 3:
        weights[-1] = weights[0]
    return weights


def allocate(budget: float, rooms: int) -> list[float]:
    """Split the budget across rooms in whole cents, summing exactly to budget."""
    weights = room_weights(rooms)
    total_cents = round(budget * 100)
    total_weight = sum(weights)
    cents = [int(total_cents * w / total_weight) for w in weights]
    # Hand leftover cents to the climax-heavy rooms first
    leftover = total_cents - sum(cents)
    for i in sorted(range(rooms), key=lambda i: -weights[i])[:leftover]:
        cents[i] += 1
    return [c / 100 for c in cents]
