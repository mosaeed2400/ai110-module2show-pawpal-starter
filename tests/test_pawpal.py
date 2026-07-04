"""Tests for pawpal_system core behavior."""

from datetime import timedelta

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


def test_daily_task_respawns_one_day_later():
    task = Task("Morning walk", 30, Priority.HIGH, "08:00", frequency="daily")

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == task.due_date + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.frequency == "daily"


def test_weekly_task_respawns_seven_days_later():
    task = Task("Vet checkup", 60, Priority.MEDIUM, "10:00", frequency="weekly")

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == task.due_date + timedelta(days=7)
    assert next_task.completed is False
    assert next_task.frequency == "weekly"


def test_non_recurring_task_does_not_respawn():
    task = Task("One-off bath", 20, Priority.LOW, "12:00")

    next_task = task.mark_complete()

    assert next_task is None
    assert task.completed is True
