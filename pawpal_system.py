"""PawPal+ — pet care scheduling app.

Class skeletons generated from the UML design. Attributes and method
stubs only; no logic implemented yet.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Task:
    description: str
    duration: int
    priority: str
    preferred_time: str
    completed: bool = False
    frequency: str = ""

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


class Owner:
    def __init__(self, name: str, pets: List[Pet] = None, preferences: Dict = None):
        self.name = name
        self.pets: List[Pet] = pets if pets is not None else []
        self.preferences: Dict = preferences if preferences is not None else {}

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner, available_minutes: int):
        self.owner = owner
        self.available_minutes = available_minutes

    def generate_plan(self) -> List[Task]:
        pass

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        pass

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        pass

    def filter_tasks(self, tasks: List[Task], criteria) -> List[Task]:
        pass

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        pass

    def explain_plan(self, tasks: List[Task]) -> str:
        pass
