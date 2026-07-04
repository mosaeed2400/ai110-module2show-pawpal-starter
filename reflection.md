# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Before writing any code, I identified three core actions a user should be able to perform in PawPal+:

1. **Add and manage pet care information** - the user can enter basic owner and pet details, 
   and add or edit care tasks (walks, feeding, meds, grooming, enrichment), each with at least 
   a duration and a priority level.

2. **Generate a daily plan** - the user can trigger the system to build a schedule for the day 
   that respects constraints like total available time and task priority.

3. **View and understand the plan** - the user can see the generated schedule clearly laid out 
   in time order, along with a brief explanation of why tasks were scheduled (or skipped) the 
   way they were.

My initial UML design included four classes:

- **Task** — represents a single care activity (e.g., a walk or feeding). Holds its own 
  description, duration, priority, preferred time, completion status, and frequency 
  (one-time/daily/weekly). Responsible for tracking and updating its own completion state.

- **Pet** — represents an individual pet and owns a list of its Tasks. Responsible for 
  adding tasks and returning its task list.

- **Owner** — represents the pet owner and holds a list of Pets plus scheduling 
  preferences. Responsible for managing pets and aggregating tasks across all of them.
  
- **Scheduler** — the "brain" of the system. Reads from an Owner's tasks and is 
  responsible for generating a daily plan: sorting by priority/time, filtering, 
  detecting conflicts, and explaining its reasoning.

I kept Scheduler separate from Owner/Pet since it represents *behavior* (planning logic), 
not stored data — this keeps responsibilities cleanly divided between "data" classes and 
the one class that reasons about that data.

**b. Design changes**

Yes — after asking my AI coding assistant to review my initial skeleton, it flagged that my 
object graph only pointed downward (Owner → Pet → Task), but my Scheduler works with 
flattened `List[Task]` results from methods like `get_all_tasks()`. Without a way to trace 
a task back to its pet, methods like `explain_plan()` wouldn't be able to say which pet a 
task belonged to once tasks were flattened into a single list.

I added a back-reference (`Task.pet`), excluding it from `repr`/`compare` to avoid infinite 
recursion in the dataclass-generated methods caused by the circular reference.

I also converted `priority` from a free-form string to a `Priority` Enum (LOW/MEDIUM/HIGH), 
since sorting plain strings alphabetically would have put "high" before "low" incorrectly, 
and typos like `"High"` vs `"high"` would have silently broken sorting logic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One subtle tradeoff lives in `Scheduler.sort_by_priority()`, which sorts using 
`key=lambda task: (-task.priority, task.preferred_time)` instead of the seemingly simpler 
`sorted(tasks, key=lambda t: (t.priority, t.preferred_time), reverse=True)`. The `reverse=True` 
version looks cleaner but is actually wrong: it reverses the *entire* ordering, including 
the time tie-break, so two equal-priority tasks would come out in descending time order 
(18:00 before 08:00) instead of ascending. Negating just the priority value keeps HIGH 
tasks first while leaving the time tie-break in its natural ascending order. I confirmed 
this was correct by asking my AI coding assistant to review the method for simplification — 
it recommended keeping the negation as-is and explained exactly why `reverse=True` would 
introduce this bug, which matched my own reasoning about the tradeoff.

Another tradeoff worth noting: `sort_by_time()` and conflict detection both compare 
`preferred_time` as plain strings ("HH:MM"). This works correctly only because the format 
is always zero-padded and 24-hour; it would silently sort incorrectly if a time like "8:00" 
(un-padded) or 12-hour format ever entered the system. I accepted this tradeoff since it 
keeps the code simple and the format is controlled internally, but a more robust version 
would parse times with `datetime.strptime` instead of comparing raw strings.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?