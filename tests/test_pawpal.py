"""Tests for pawpal_system core behavior."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def make_scheduler():
    """A scheduler over an empty owner. available_minutes is unused by the
    sorting/filtering/conflict methods, so any value works here."""
    return Scheduler(Owner("Test Owner"), available_minutes=60)


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


def test_weekly_task_across_month_boundary():
    task = Task(
        "Fence check",
        20,
        Priority.MEDIUM,
        "09:00",
        frequency="weekly",
        due_date=date(2024, 1, 26),
    )

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date(2024, 2, 2)
    assert next_task.completed is False
    assert next_task.frequency == "weekly"


def test_weekly_task_across_year_boundary():
    task = Task(
        "Holiday check",
        30,
        Priority.MEDIUM,
        "10:00",
        frequency="weekly",
        due_date=date(2023, 12, 28),
    )

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date(2024, 1, 4)
    assert next_task.completed is False
    assert next_task.frequency == "weekly"


def test_non_recurring_task_does_not_respawn():
    task = Task("One-off bath", 20, Priority.LOW, "12:00")

    next_task = task.mark_complete()

    assert next_task is None
    assert task.completed is True


# --- Sorting ---------------------------------------------------------------


def test_sort_by_time_empty_list_returns_empty():
    scheduler = make_scheduler()

    assert scheduler.sort_by_time([]) == []


def test_sort_by_priority_empty_list_returns_empty():
    scheduler = make_scheduler()

    assert scheduler.sort_by_priority([]) == []


def test_sort_by_time_orders_chronologically():
    scheduler = make_scheduler()
    late = Task("Evening walk", 30, Priority.LOW, "18:00")
    early = Task("Breakfast", 10, Priority.HIGH, "07:00")

    ordered = scheduler.sort_by_time([late, early])

    assert ordered == [early, late]


def test_sort_by_time_is_stable_for_equal_times():
    scheduler = make_scheduler()
    first = Task("Feed", 10, Priority.LOW, "08:00")
    second = Task("Brush", 10, Priority.HIGH, "08:00")

    # Equal preferred_time -> stable sort keeps input order.
    ordered = scheduler.sort_by_time([first, second])

    assert ordered == [first, second]


def test_sort_by_priority_orders_most_urgent_first():
    scheduler = make_scheduler()
    low = Task("Nap check", 5, Priority.LOW, "13:00")
    high = Task("Medication", 5, Priority.HIGH, "13:00")
    medium = Task("Play", 5, Priority.MEDIUM, "13:00")

    ordered = scheduler.sort_by_priority([low, high, medium])

    assert ordered == [high, medium, low]


def test_sort_by_priority_tie_broken_by_earlier_time():
    scheduler = make_scheduler()
    later_high = Task("Walk", 30, Priority.HIGH, "17:00")
    earlier_high = Task("Meds", 5, Priority.HIGH, "09:00")

    ordered = scheduler.sort_by_priority([later_high, earlier_high])

    assert ordered == [earlier_high, later_high]


def test_sort_by_time_nonpadded_hour_sorts_incorrectly():
    # KNOWN LIMITATION: sort_by_time relies on lexicographic string order,
    # which is only chronological for zero-padded "HH:MM". "9:00" (no leading
    # zero) sorts AFTER "10:00" as a string, so the plan comes out wrong.
    # Documenting current behavior; do not treat this test as the desired one.
    scheduler = make_scheduler()
    nine = Task("Nine", 10, Priority.LOW, "9:00")
    ten = Task("Ten", 10, Priority.LOW, "10:00")

    ordered = scheduler.sort_by_time([nine, ten])

    assert ordered == [ten, nine]  # chronologically wrong, but current behavior


# --- Filtering -------------------------------------------------------------


def test_filter_no_filters_returns_all():
    scheduler = make_scheduler()
    tasks = [Task("A", 10, Priority.LOW, "08:00"), Task("B", 10, Priority.LOW, "09:00")]

    assert scheduler.filter_tasks(tasks) == tasks


def test_filter_no_matches_returns_empty():
    scheduler = make_scheduler()
    pet = Pet("Rex", "Dog", "Lab")
    pet.add_task(Task("Walk", 30, Priority.HIGH, "08:00"))

    assert scheduler.filter_tasks(pet.get_tasks(), pet_name="Ghost") == []


def test_filter_completed_false_returns_only_incomplete():
    scheduler = make_scheduler()
    done = Task("Done", 10, Priority.LOW, "08:00", completed=True)
    todo = Task("Todo", 10, Priority.LOW, "09:00")

    assert scheduler.filter_tasks([done, todo], completed=False) == [todo]


def test_filter_completed_none_ignores_completion_status():
    # completed=None must mean "don't filter", distinct from completed=False.
    scheduler = make_scheduler()
    done = Task("Done", 10, Priority.LOW, "08:00", completed=True)
    todo = Task("Todo", 10, Priority.LOW, "09:00")

    assert scheduler.filter_tasks([done, todo], completed=None) == [done, todo]


def test_filter_by_pet_name_excludes_unassigned_task():
    scheduler = make_scheduler()
    pet = Pet("Rex", "Dog", "Lab")
    assigned = Task("Walk", 30, Priority.HIGH, "08:00")
    pet.add_task(assigned)
    orphan = Task("Mystery", 10, Priority.LOW, "08:00")  # pet is None

    result = scheduler.filter_tasks([assigned, orphan], pet_name="Rex")

    assert result == [assigned]


def test_filter_combines_pet_name_and_completed():
    scheduler = make_scheduler()
    rex = Pet("Rex", "Dog", "Lab")
    rex_done = Task("Rex done", 10, Priority.LOW, "08:00", completed=True)
    rex_todo = Task("Rex todo", 10, Priority.LOW, "09:00")
    rex.add_task(rex_done)
    rex.add_task(rex_todo)
    milo = Pet("Milo", "Cat", "Tabby")
    milo_todo = Task("Milo todo", 10, Priority.LOW, "09:00")
    milo.add_task(milo_todo)

    result = scheduler.filter_tasks(
        [rex_done, rex_todo, milo_todo], pet_name="Rex", completed=False
    )

    assert result == [rex_todo]


# --- Conflict detection ----------------------------------------------------


def test_detect_conflicts_same_time_reports_conflict():
    scheduler = make_scheduler()
    a = Task("Feed Rex", 10, Priority.LOW, "08:00")
    b = Task("Feed Milo", 10, Priority.LOW, "08:00")

    conflicts = scheduler.detect_conflicts([a, b])

    assert len(conflicts) == 1
    assert conflicts[0].startswith("08:00:")


def test_detect_conflicts_different_times_returns_none():
    scheduler = make_scheduler()
    a = Task("Feed", 10, Priority.LOW, "08:00")
    b = Task("Walk", 10, Priority.LOW, "09:00")

    assert scheduler.detect_conflicts([a, b]) == []


def test_detect_conflicts_empty_list_returns_none():
    scheduler = make_scheduler()

    assert scheduler.detect_conflicts([]) == []


def test_detect_conflicts_ignores_completed_tasks():
    scheduler = make_scheduler()
    done = Task("Done", 10, Priority.LOW, "08:00", completed=True)
    todo = Task("Todo", 10, Priority.LOW, "08:00")

    # Only one outstanding task at 08:00 once the completed one is ignored.
    assert scheduler.detect_conflicts([done, todo]) == []


def test_detect_conflicts_three_tasks_single_entry():
    scheduler = make_scheduler()
    tasks = [
        Task("A", 10, Priority.LOW, "08:00"),
        Task("B", 10, Priority.LOW, "08:00"),
        Task("C", 10, Priority.LOW, "08:00"),
    ]

    conflicts = scheduler.detect_conflicts(tasks)

    assert len(conflicts) == 1
    assert conflicts[0].count("(") == 3  # all three listed in one entry


def test_detect_conflicts_labels_unassigned_task():
    scheduler = make_scheduler()
    orphan_a = Task("Mystery A", 10, Priority.LOW, "08:00")  # pet is None
    orphan_b = Task("Mystery B", 10, Priority.LOW, "08:00")

    conflicts = scheduler.detect_conflicts([orphan_a, orphan_b])

    assert len(conflicts) == 1
    assert "Unassigned" in conflicts[0]


# --- Recurrence edge cases -------------------------------------------------


def test_recurring_task_with_no_pet_returns_detached_task():
    task = Task("Solo walk", 30, Priority.HIGH, "08:00", frequency="daily")
    assert task.pet is None

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.pet is None  # nowhere to attach it, so it stays detached
    assert next_task.due_date == task.due_date + timedelta(days=1)


def test_unknown_frequency_documents_current_behavior():
    # KNOWN LIMITATION: an unrecognized frequency (not "daily"/"weekly") is
    # silently treated as a one-off -- no next occurrence is spawned and the
    # caller gets None back with no error. Documenting current behavior.
    task = Task("Monthly grooming", 45, Priority.MEDIUM, "10:00", frequency="monthly")

    next_task = task.mark_complete()

    assert next_task is None
    assert task.completed is True


def test_double_completion_documents_current_behavior():
    # KNOWN LIMITATION: mark_complete is not idempotent. Calling it again on an
    # already-completed recurring task spawns ANOTHER occurrence rather than
    # no-op'ing. Documenting current behavior.
    pet = Pet("Rex", "Dog", "Lab")
    task = Task("Morning walk", 30, Priority.HIGH, "08:00", frequency="daily")
    pet.add_task(task)

    first = task.mark_complete()
    second = task.mark_complete()

    assert first is not None
    assert second is not None
    # Original + two spawned occurrences all live on the pet.
    assert len(pet.get_tasks()) == 3


def test_daily_respawn_crosses_month_boundary():
    task = Task(
        "Meds", 5, Priority.HIGH, "08:00", frequency="daily", due_date=date(2026, 1, 31)
    )

    next_task = task.mark_complete()

    assert next_task.due_date == date(2026, 2, 1)


# --- Next available slot ---------------------------------------------------


def test_find_next_available_slot_finds_free_slot():
    scheduler = make_scheduler()
    # Occupies 08:00-08:30. A 30-min task can't start at 08:00 (overlap) but
    # 08:30 is clear, and 15-min grid steps reach it exactly.
    existing = [Task("Walk", 30, Priority.HIGH, "08:00")]

    slot = scheduler.find_next_available_slot(existing, duration=30)

    # 00:00 is actually the earliest free slot (the day is empty before 08:00),
    # so the search returns the very start rather than jumping past the task.
    assert slot == "00:00"


def test_find_next_available_slot_skips_early_conflict():
    scheduler = make_scheduler()
    # Block the start of the day so the search must step past the conflict:
    # 00:00-00:45 is occupied, so a 30-min task first fits at 00:45.
    existing = [Task("Early block", 45, Priority.HIGH, "00:00")]

    slot = scheduler.find_next_available_slot(existing, duration=30)

    assert slot == "00:45"


def test_find_next_available_slot_fully_booked_returns_none():
    scheduler = make_scheduler()
    # One task spanning the entire day leaves no room for anything.
    existing = [Task("All-day event", 24 * 60, Priority.HIGH, "00:00")]

    assert scheduler.find_next_available_slot(existing, duration=30) is None


def test_find_next_available_slot_empty_list_returns_start_of_day():
    scheduler = make_scheduler()

    # No existing tasks -> the earliest candidate (00:00) is immediately free.
    assert scheduler.find_next_available_slot([], duration=30) == "00:00"


def test_find_next_available_slot_ignores_completed_tasks():
    scheduler = make_scheduler()
    # A completed task at 00:00 shouldn't block the slot it nominally occupies.
    done = Task("Done", 45, Priority.LOW, "00:00", completed=True)

    assert scheduler.find_next_available_slot([done], duration=30) == "00:00"


# --- Aggregation and empty states ------------------------------------------


def test_pet_with_no_tasks_returns_empty():
    pet = Pet("Rex", "Dog", "Lab")

    assert pet.get_tasks() == []


def test_owner_with_no_pets_produces_empty_plan():
    owner = Owner("Alex")
    scheduler = Scheduler(owner, available_minutes=60)

    assert owner.get_all_tasks() == []
    assert scheduler.generate_plan() == []


def test_explain_plan_empty_reports_no_conflicts():
    scheduler = make_scheduler()

    result = scheduler.explain_plan([])

    assert result == "Today's plan:\nNo conflicts."


def test_explain_plan_labels_unassigned_task():
    scheduler = make_scheduler()
    orphan = Task("Mystery", 10, Priority.LOW, "08:00")  # pet is None

    result = scheduler.explain_plan([orphan])

    assert "Unassigned" in result
