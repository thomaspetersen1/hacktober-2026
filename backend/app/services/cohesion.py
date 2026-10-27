"""Stage 3: check the whole house hangs together and stays on budget."""

from app.schemas import PlanResponse

# Below this, guests are shoulder to shoulder and actors have nowhere to hide.
MIN_ROOM_SQFT = 60


def check_plan(plan: PlanResponse) -> list[str]:
    """Plain-English warnings for the UI. Empty means the plan looks good."""
    warnings: list[str] = []

    # Should never fire; it's here so a bug can't silently overspend.
    if plan.total_spent > plan.budget:
        warnings.append(f"Props cost ${plan.total_spent:,.2f}, which is over the ${plan.budget:,.2f} budget.")

    for room in plan.rooms:
        if room.spent > room.budget:
            warnings.append(f"{room.name} is over its budget.")
        if not room.items:
            warnings.append(f"{room.name} has ${room.budget:,.2f}, which isn't enough for any prop. Try fewer rooms.")

    names = [room.name.lower() for room in plan.rooms]
    if len(set(names)) < len(names):
        warnings.append("Some rooms repeat. Reroll one to keep the story moving.")

    if len(plan.rooms) >= 3:
        climax = plan.rooms[-2]
        if any(room.budget > climax.budget for room in plan.rooms):
            warnings.append(f"{climax.name} is the big scare but isn't the best-funded room.")

    if plan.square_feet:
        per_room = plan.square_feet / len(plan.rooms)
        if per_room < MIN_ROOM_SQFT:
            warnings.append(
                f"About {per_room:.0f} sq ft per room is tight. Guests will walk single file, so plan for small groups."
            )

    leftover = plan.budget - plan.total_spent
    if plan.budget >= 50 and leftover > plan.budget * 0.25:
        warnings.append(
            f"${leftover:,.2f} is left over. Spend it on scare actors, safety lighting, or more rooms."
        )

    return warnings
