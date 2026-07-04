"""PawPal+ CLI demo — builds a small owner/pet/task setup and prints the
schedule produced by the Scheduler."""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority


def main() -> None:
    # Owner and pets
    alex = Owner("Alex")
    rex = Pet("Rex", "Dog", "")
    whiskers = Pet("Whiskers", "Cat", "")
    alex.add_pet(rex)
    alex.add_pet(whiskers)

    # Tasks across both pets, with different preferred times
    rex.add_task(Task("Morning walk", 30, Priority.HIGH, "08:00"))
    whiskers.add_task(Task("Feeding", 10, Priority.MEDIUM, "07:30"))
    rex.add_task(Task("Evening medication", 5, Priority.HIGH, "18:00"))

    # Build the plan
    scheduler = Scheduler(alex, available_minutes=120)
    plan = scheduler.generate_plan()

    # Print a clean, readable schedule
    print("Today's Schedule")
    print("=" * 40)
    for task in plan:
        pet_name = task.pet.name if task.pet else "Unassigned"
        print(f"{task.preferred_time}  {pet_name}: {task.description} ({task.priority.name})")


if __name__ == "__main__":
    main()
