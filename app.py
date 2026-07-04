import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Priority

PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
FREQUENCY_MAP = {"one-time": "", "daily": "daily", "weekly": "weekly"}
STATUS_FILTER_MAP = {"All": None, "Completed": True, "Incomplete": False}


def format_conflict(conflict: str) -> str:
    """Turn a raw Scheduler.detect_conflicts() entry into an owner-friendly warning.

    detect_conflicts() returns strings like "08:00: Morning walk (Rex), Feeding
    (Whiskers)"; this rephrases them as a single readable sentence.
    """
    time, _, rest = conflict.partition(": ")
    parts = [p.strip() for p in rest.split(", ") if p.strip()]
    if len(parts) <= 1:
        joined = "".join(parts)
        verb = "is"
    elif len(parts) == 2:
        joined = f"{parts[0]} and {parts[1]}"
        verb = "are both"
    else:
        joined = ", ".join(parts[:-1]) + f", and {parts[-1]}"
        verb = "are all"
    return f"⚠️ Scheduling conflict at {time}: {joined} {verb} scheduled at this time."


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Persist a real Owner across reruns. Streamlit re-executes this whole script
# on every interaction, so anything not stored in st.session_state is rebuilt
# from scratch. Creating the Owner only when it's missing keeps it stable.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)

owner = st.session_state.owner

# Create the Pet once and attach it to the owner. The flag records that we've
# already added it, so we don't add a duplicate pet on the next rerun.
if not st.session_state.get("pet_created", False):
    owner.add_pet(Pet(pet_name, species, ""))
    st.session_state.pet_created = True

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    preferred_time = st.text_input("Preferred time (HH:MM)", value="09:00")
with col5:
    repeat = st.selectbox("Repeat", ["one-time", "daily", "weekly"])

if st.button("Add task"):
    pet = owner.pets[0]
    pet.add_task(
        Task(
            task_title,
            int(duration),
            PRIORITY_MAP[priority],
            preferred_time,
            frequency=FREQUENCY_MAP[repeat],
        )
    )
    st.success(f"Added '{task_title}' at {preferred_time}.")

# Show a one-shot confirmation set by an action on the previous rerun (e.g.
# marking a task complete), then clear it so it doesn't linger.
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

# Read tasks straight from the pet rather than a parallel session_state list.
current_tasks = owner.pets[0].get_tasks()
# Scheduler exposes the sorting/filtering logic this table is built on.
scheduler = Scheduler(owner, available_minutes=120)

if current_tasks:
    st.write("Current tasks:")

    view_col, filter_col = st.columns(2)
    with view_col:
        sort_mode = st.radio("Sort by", ["By Time", "By Priority"], horizontal=True)
    with filter_col:
        status_filter = st.radio("Show", ["All", "Incomplete", "Completed"], horizontal=True)

    tasks_to_show = scheduler.filter_tasks(
        current_tasks, completed=STATUS_FILTER_MAP[status_filter]
    )
    if sort_mode == "By Priority":
        tasks_to_show = scheduler.sort_by_priority(tasks_to_show)
    else:
        tasks_to_show = scheduler.sort_by_time(tasks_to_show)

    if tasks_to_show:
        widths = [3, 1, 1, 1, 1, 2]
        header = st.columns(widths)
        for col, label in zip(
            header, ["Task", "Duration", "Priority", "Time", "Status", ""]
        ):
            col.markdown(f"**{label}**")

        for i, task in enumerate(tasks_to_show):
            row = st.columns(widths)
            repeat_note = f" ({task.frequency})" if task.frequency else ""
            row[0].write(f"{task.description}{repeat_note}")
            row[1].write(f"{task.duration} min")
            row[2].write(task.priority.name)
            row[3].write(task.preferred_time)
            row[4].write("✅ Done" if task.completed else "⬜ Open")
            if task.completed:
                row[5].write("—")
            elif row[5].button("Mark complete", key=f"complete_{i}"):
                respawned = task.mark_complete()
                if respawned is not None:
                    st.session_state.flash = (
                        f"✅ Completed '{task.description}'. Recurring "
                        f"({task.frequency}) — next one scheduled for "
                        f"{respawned.due_date} at {respawned.preferred_time}."
                    )
                else:
                    st.session_state.flash = f"✅ Completed '{task.description}'."
                st.rerun()
    else:
        st.info("No tasks match this filter.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's plan by ordering the pet's tasks by time.")

if st.button("Generate schedule"):
    plan = scheduler.generate_plan()

    st.markdown("#### Today's Schedule")
    if plan:
        for task in plan:
            pet_name = task.pet.name if task.pet else "Unassigned"
            st.write(
                f"**{task.preferred_time}** — {pet_name}: {task.description} "
                f"({task.priority.name})"
            )

        conflicts = scheduler.detect_conflicts(plan)
        if conflicts:
            st.markdown("#### Conflicts")
            for conflict in conflicts:
                st.warning(format_conflict(conflict))
        else:
            st.success("No scheduling conflicts — every task has its own time slot. 🎉")
    else:
        st.info("No tasks to schedule yet. Add a task above first.")
