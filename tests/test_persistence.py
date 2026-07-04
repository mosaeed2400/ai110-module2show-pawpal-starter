"""Tests for JSON persistence (save_to_json / load_from_json)."""

from datetime import date

import pytest

from pawpal_system import (
    Owner,
    Pet,
    Priority,
    Task,
    load_from_json,
    save_to_json,
)


def test_round_trip_simple_owner_one_pet_one_task(tmp_path):
    # A minimal owner -> pet -> task graph survives a save/load round trip.
    owner = Owner("Alex")
    pet = Pet("Rex", "Dog", "Lab")
    pet.add_task(Task("Morning walk", 30, Priority.HIGH, "08:00"))
    owner.add_pet(pet)

    path = tmp_path / "owner.json"
    save_to_json(owner, str(path))
    loaded = load_from_json(str(path))

    assert loaded.name == "Alex"
    assert len(loaded.pets) == 1
    assert loaded.pets[0].name == "Rex"
    assert loaded.pets[0].species == "Dog"
    assert loaded.pets[0].breed == "Lab"

    task = loaded.pets[0].get_tasks()[0]
    assert task.description == "Morning walk"
    assert task.duration == 30
    assert task.priority == Priority.HIGH
    assert task.preferred_time == "08:00"


def test_round_trip_preserves_due_date_and_non_default_frequency(tmp_path):
    # The date field (ISO conversion) and a non-default frequency round trip
    # exactly, including type — a real date, not a string.
    owner = Owner("Sam")
    pet = Pet("Milo", "Cat", "Tabby")
    pet.add_task(
        Task(
            "Vet checkup",
            60,
            Priority.MEDIUM,
            "10:00",
            frequency="weekly",
            due_date=date(2026, 1, 31),
        )
    )
    owner.add_pet(pet)

    path = tmp_path / "owner.json"
    save_to_json(owner, str(path))
    loaded = load_from_json(str(path))

    task = loaded.pets[0].get_tasks()[0]
    assert task.frequency == "weekly"
    assert task.due_date == date(2026, 1, 31)
    assert isinstance(task.due_date, date)


def test_load_restores_task_pet_back_reference(tmp_path):
    # The circular Task.pet back-reference is not serialized; confirm it is
    # correctly re-established after loading (task.pet points back at its pet).
    owner = Owner("Jordan")
    pet = Pet("Bella", "Dog", "Poodle")
    pet.add_task(Task("Feeding", 10, Priority.LOW, "07:30"))
    owner.add_pet(pet)

    path = tmp_path / "owner.json"
    save_to_json(owner, str(path))
    loaded = load_from_json(str(path))

    loaded_pet = loaded.pets[0]
    loaded_task = loaded_pet.get_tasks()[0]
    assert loaded_task.pet is loaded_pet  # same object, back-reference intact
    assert loaded_task.pet.name == "Bella"


def test_load_nonexistent_file_raises_file_not_found(tmp_path):
    # Loading a path that doesn't exist raises the clear, standard error
    # rather than crashing with something opaque.
    missing = tmp_path / "does_not_exist.json"

    with pytest.raises(FileNotFoundError):
        load_from_json(str(missing))
