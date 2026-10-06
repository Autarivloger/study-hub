from dataclasses import dataclass, replace
from enum import Enum
from typing import Protocol, Callable

class Category(Enum):
    BOOK = "book"
    TOOL = "tool"

@dataclass(frozen=True)
class Item:
    sku: str
    name: str
    quantity: int
    category: Category

    def __post_init__(self) -> None:
        if not self.sku.strip() or not self.name.strip():
            raise ValueError("sku and name required")
        if type(self.quantity) is not int or self.quantity < 0:
            raise ValueError("quantity must be a nonnegative integer")
        if not isinstance(self.category, Category):
            raise TypeError("Category required")

class Repository(Protocol):
    def find(self, sku: str) -> Item | None: ...
    def save(self, item: Item) -> None: ...

class MemoryRepository:
    def __init__(self) -> None:
        self._items: dict[str, Item] = {}
    def find(self, sku: str) -> Item | None:
        return self._items.get(sku)
    def save(self, item: Item) -> None:
        self._items[item.sku] = item

def make_repository(kind: str) -> Repository:
    if kind == "memory":
        return MemoryRepository()
    raise ValueError("unknown repository")

def never_low(item: Item) -> bool:
    return False

def low_below_two(item: Item) -> bool:
    return item.quantity < 2

class Inventory:
    def __init__(self, repository: Repository,
                 low_policy: Callable[[Item], bool]) -> None:
        self._repository = repository
        self._low_policy = low_policy

    def add(self, item: Item) -> None:
        if self._repository.find(item.sku) is not None:
            raise ValueError("duplicate sku")
        self._repository.save(item)

    def get(self, sku: str) -> Item:
        item = self._repository.find(sku)
        if item is None:
            raise KeyError(sku)
        return item

    def remove(self, sku: str, amount: int) -> Item:
        if type(amount) is not int or amount <= 0:
            raise ValueError("positive integer amount required")
        current = self.get(sku)
        if amount > current.quantity:
            raise ValueError("not enough stock")
        updated = replace(current, quantity=current.quantity - amount)
        self._repository.save(updated)
        return updated

    def is_low(self, sku: str) -> bool:
        return self._low_policy(self.get(sku))

def render(item: Item) -> str:
    return f"{item.sku}: {item.name} / {item.quantity} / {item.category.value}"

inventory = Inventory(make_repository("memory"), low_below_two)
inventory.add(Item("B1", "Python", 3, Category.BOOK))
old = inventory.get("B1")
updated = inventory.remove("B1", 2)
print(render(updated))
print(old.quantity, updated.quantity, inventory.is_low("B1"))
try:
    inventory.remove("B1", 2)
except ValueError as error:
    print(error)
print(inventory.get("B1").quantity)
