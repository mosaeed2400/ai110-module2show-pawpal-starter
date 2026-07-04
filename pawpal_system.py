"""PawPal+ — pet care scheduling app.

Class skeletons generated from the UML design. Attributes and method
stubs only; no logic implemented yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Optional


class Priority(IntEnum):
    """Task priority. Ordered so higher value == more urgent, which lets
    sort_by_priority sort on the enum directly."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    description: str
    duration: int
    priority: Priority
    preferred_time: str
    completed: bool = False
    frequency: str = ""
    # Back-reference to the owning Pet. Excluded from repr/compare to avoid
    # infinite recursion and equality cycles through the Pet <-> Task graph.
    pet: Optional[Pet] = field(default=None, repr=False, compare=False)

    def mark_complete(self) -> None:
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        task.pet = self  # keep the back-reference in sync

    def get_tasks(self) -> List[Task]:
        return self.tasks


class Owner:
    def __init__(self, name: str, pets: List[Pet] = None, preferences: Dict = None):
        self.name = name
        self.pets: List[Pet] = pets if pets is not None else []
        self.preferences: Dict = preferences if preferences is not None else {}

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        return [task for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    def __init__(self, owner: Owner, available_minutes: int):
        self.owner = owner
        self.available_minutes = available_minutes

    def generate_plan(self) -> List[Task]:
        tasks = self.owner.get_all_tasks()
        return self.sort_by_time(tasks)

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        pass

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        # preferred_time is "HH:MM" 24-hour; string sort matches chronological
        # order for that fixed-width format.
        return sorted(tasks, key=lambda task: task.preferred_time)

    def filter_tasks(self, tasks: List[Task], criteria) -> List[Task]:
        pass

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        pass

    def explain_plan(self, tasks: List[Task]) -> str:
        pass
