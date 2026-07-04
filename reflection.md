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

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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