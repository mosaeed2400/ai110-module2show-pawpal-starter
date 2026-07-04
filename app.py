import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Priority

PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}

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

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    preferred_time = st.text_input("Preferred time (HH:MM)", value="09:00")

if st.button("Add task"):
    pet = owner.pets[0]
    pet.add_task(
        Task(task_title, int(duration), PRIORITY_MAP[priority], preferred_time)
    )

# Read tasks straight from the pet rather than a parallel session_state list.
current_tasks = owner.pets[0].get_tasks()
if current_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "description": task.description,
                "duration": task.duration,
                "priority": task.priority.name,
                "preferred_time": task.preferred_time,
            }
            for task in current_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's plan by ordering the pet's tasks by time.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner, available_minutes=120)
    plan = scheduler.generate_plan()

    st.markdown("#### Today's Schedule")
    if plan:
        for task in plan:
            pet_name = task.pet.name if task.pet else "Unassigned"
            st.write(
                f"**{task.preferred_time}** — {pet_name}: {task.description} "
                f"({task.priority.name})"
            )
    else:
        st.info("No tasks to schedule yet. Add a task above first.")
