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

    # Tasks across both pets. The morning walk recurs daily; Rex's walk and
    # Whiskers' feeding are both at 08:00, which creates a conflict.
    rex.add_task(Task("Morning walk", 30, Priority.HIGH, "08:00", frequency="daily"))
    whiskers.add_task(Task("Feeding", 10, Priority.MEDIUM, "08:00"))
    rex.add_task(Task("Evening medication", 5, Priority.HIGH, "18:00"))

    scheduler = Scheduler(alex, available_minutes=120)

    # 1. Priority-sorted view — most urgent first
    print("By Priority")
    print("=" * 40)
    for task in scheduler.sort_by_priority(alex.get_all_tasks()):
        pet_name = task.pet.name if task.pet else "Unassigned"
        print(f"{task.priority.name:<6} {task.preferred_time}  {pet_name}: {task.description}")

    # 2. Filter — Rex's outstanding tasks only
    print("\nRex's Outstanding Tasks")
    print("=" * 40)
    for task in scheduler.filter_tasks(alex.get_all_tasks(), pet_name="Rex", completed=False):
        print(f"{task.preferred_time}  {task.description}")

    # 3. Recurring task — completing the daily walk respawns tomorrow's
    print("\nCompleting Rex's Morning Walk (daily)")
    print("=" * 40)
    morning_walk = rex.get_tasks()[0]
    next_walk = morning_walk.mark_complete()
    print(f"Completed: {morning_walk.description} (completed={morning_walk.completed})")
    print(f"Respawned: {next_walk.description} at {next_walk.preferred_time} "
          f"(completed={next_walk.completed}, frequency={next_walk.frequency})")

    # 4. Conflict detection — Rex's walk vs Whiskers' feeding at 08:00
    print("\nConflicts")
    print("=" * 40)
    conflicts = scheduler.detect_conflicts(alex.get_all_tasks())
    if conflicts:
        for conflict in conflicts:
            print(f"⚠ {conflict}")
    else:
        print("No conflicts.")

    # Final plan — filter out completed tasks before explaining
    print("\n" + "=" * 40)
    pending = scheduler.filter_tasks(alex.get_all_tasks(), completed=False)
    print(scheduler.explain_plan(pending))


if __name__ == "__main__":
    main()
