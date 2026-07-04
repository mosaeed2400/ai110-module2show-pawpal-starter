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

    # Recurring task — complete a daily task and show the respawn's new due_date
    print("\nRecurring Task (daily)")
    print("=" * 40)
    daily_walk = Task("Daily walk", 30, Priority.HIGH, "08:00", frequency="daily")
    rex.add_task(daily_walk)
    print(f"Original: {daily_walk.description}  due {daily_walk.due_date}  "
          f"(completed={daily_walk.completed})")
    next_walk = daily_walk.mark_complete()
    print(f"Respawned: {next_walk.description}  due {next_walk.due_date}  "
          f"(completed={next_walk.completed})")
    print(f"→ new due_date is {(next_walk.due_date - daily_walk.due_date).days} "
          f"day later, as expected for a daily task")

    # Next available slot — fit a new 45-min task around the existing incomplete
    # tasks. A "quiet hours" block (00:00-07:00) plus Whiskers' feeding
    # (07:30-07:40) and Rex's morning walk (08:00-08:30) are all outstanding, so
    # the search must step past every early candidate before landing on the
    # first real gap at 08:30.
    print("\nFind Next Available Slot")
    print("=" * 40)
    quiet_hours = Task("Sleep/quiet hours", 7 * 60, Priority.LOW, "00:00")
    incomplete = [quiet_hours] + scheduler.filter_tasks(all_tasks, completed=False)
    print("Outstanding tasks blocking time:")
    for task in scheduler.sort_by_time(incomplete):
        end = scheduler._to_hhmm(scheduler._to_minutes(task.preferred_time) + task.duration)
        print(f"  {task.preferred_time}-{end}  {task.description} ({task.duration} min)")

    slot = scheduler.find_next_available_slot(incomplete, duration=45)
    print(f"→ next free 45-min slot: {slot}  "
          f"(searched past quiet hours, feeding, and the walk)")

    # A day packed solid from 00:00 shows the None case.
    packed = [Task("All-day event", 24 * 60, Priority.HIGH, "00:00")]
    print(f"→ next free 30-min slot in a fully booked day: "
          f"{scheduler.find_next_available_slot(packed, duration=30)}")


if __name__ == "__main__":
    main()
