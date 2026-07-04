"""PawPal+ CLI demo — builds a small owner/pet/task setup and demonstrates
the Scheduler's priority sorting, filtering, recurring tasks, and conflict
detection."""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority


def main() -> None:
    # Owner and pets
    alex = Owner("Alex")
    rex = Pet("Rex", "Dog", "")
    whiskers = Pet("Whiskers", "Cat", "")
    alex.add_pet(rex)
    alex.add_pet(whiskers)

    # Add tasks in deliberately NON-chronological order (18:00, 07:30, 08:00)
    # so the time sort has something real to reorder.
    rex.add_task(Task("Evening medication", 5, Priority.HIGH, "18:00"))
    whiskers.add_task(Task("Feeding", 10, Priority.MEDIUM, "07:30"))
    rex.add_task(Task("Morning walk", 30, Priority.HIGH, "08:00"))

    # Mark one of Rex's tasks complete so the "incomplete only" filter has an
    # effect to show.
    rex.get_tasks()[0].mark_complete()  # Evening medication -> completed

    scheduler = Scheduler(alex, available_minutes=120)
    all_tasks = alex.get_all_tasks()

    # Insertion order — proves the list starts out unsorted
    print("Insertion Order (as added)")
    print("=" * 40)
    for task in all_tasks:
        print(f"{task.preferred_time}  {task.pet.name}: {task.description}")

    # Time-sorted view — should come out 07:30, 08:00, 18:00
    print("\nTime-Sorted")
    print("=" * 40)
    for task in scheduler.sort_by_time(all_tasks):
        print(f"{task.preferred_time}  {task.pet.name}: {task.description}")

    # Filtered view — only Rex's incomplete tasks
    print("\nRex's Incomplete Tasks")
    print("=" * 40)
    rex_pending = scheduler.filter_tasks(all_tasks, pet_name="Rex", completed=False)
    for task in rex_pending:
        print(f"{task.preferred_time}  {task.description}")


if __name__ == "__main__":
    main()
