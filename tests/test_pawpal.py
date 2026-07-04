"""Tests for pawpal_system core behavior."""

from pawpal_system import Pet, Task, Priority


def test_mark_complete_sets_completed_true():
    task = Task("Morning walk", 30, Priority.HIGH, "08:00")
    assert task.completed is False  # sanity: defaults to not completed

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Rex", "Dog", "Lab")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feeding", 10, Priority.MEDIUM, "07:30"))

    assert len(pet.get_tasks()) == 1
