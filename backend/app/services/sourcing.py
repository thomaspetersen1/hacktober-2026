"""Stage 2: pick props for a room that fit its budget. All math in whole cents."""

from app.schemas import Item, Prop
from app.services.catalog import GENERAL_THEME

# Cheap set-dressing can be bought in multiples; big props and effects can't.
STACKABLE = {"Decoration", "Lighting"}
MAX_STACK_PRICE = 25
MAX_QUANTITY = 3


def _cents(amount: float) -> int:
    return round(amount * 100)


def pick_items(
    budget: float, themes: list[str], catalog: list[Prop], used: set[str] | None = None
) -> list[Item]:
    """Fill a room's budget with props, never going over it.

    Props that match the room's themes come first (priciest first, so the
    centerpiece gets bought), then general effects like fog and sound. Themed
    props in `used` are skipped so the house doesn't repeat the same gimmick;
    general effects can repeat since every room needs light and sound.
    Leftover money then buys extra copies of cheap decorations and lights.
    """
    used = used if used is not None else set()
    left = _cents(budget)

    def by_price_desc(props: list[Prop]) -> list[Prop]:
        return sorted(props, key=lambda p: (-p.price, p.name))

    themed = by_price_desc([p for p in catalog if p.theme in themes and p.id not in used])
    general = by_price_desc([p for p in catalog if p.theme == GENERAL_THEME])

    chosen: dict[str, tuple[Prop, int]] = {}
    for prop in themed + general:
        price = _cents(prop.price)
        if price <= left:
            chosen[prop.id] = (prop, 1)
            left -= price

    for prop, _ in sorted(chosen.values(), key=lambda pq: pq[0].price):
        if prop.category not in STACKABLE or prop.price > MAX_STACK_PRICE:
            continue
        price = _cents(prop.price)
        quantity = chosen[prop.id][1]
        while quantity < MAX_QUANTITY and price <= left:
            quantity += 1
            left -= price
        chosen[prop.id] = (prop, quantity)

    used.update(prop.id for prop, _ in chosen.values() if prop.theme != GENERAL_THEME)
    return [
        Item(
            id=prop.id,
            name=prop.name,
            category=prop.category,
            unit_price=prop.price,
            quantity=quantity,
            line_total=_cents(prop.price) * quantity / 100,
        )
        for prop, quantity in chosen.values()
    ]


def spent(items: list[Item]) -> float:
    return sum(_cents(item.line_total) for item in items) / 100
