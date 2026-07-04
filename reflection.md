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

My Scheduler considers two main constraints: task priority (LOW/MEDIUM/HIGH) and preferred 
time. Priority determines urgency ordering when using `sort_by_priority()`, while preferred 
time drives the default chronological view and conflict detection (two tasks are only 
flagged as conflicting if they share the exact same `preferred_time`). I decided priority 
and time mattered most because they're the two things a real pet owner would actually ask 
when planning a day — "what's most urgent?" and "when does it need to happen?" I did not 
end up using `available_minutes` as an active constraint — it's stored on the Scheduler but 
`generate_plan()` doesn't currently enforce it — and `Owner.preferences` is similarly 
unused. Both are documented as known limitations in the README rather than left silently 
unfinished, since I'd rather be upfront about scope than imply a feature exists when it 
doesn't.

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

I used my AI coding assistant (Claude Code) throughout every phase of this project — for 
brainstorming the initial UML design, scaffolding class skeletons, implementing the core 
logic for Task/Pet/Owner/Scheduler, writing and debugging the pytest suite, wiring the 
Streamlit UI to my backend, and finalizing documentation. I also used it to review my own 
work at key checkpoints, such as asking it to check my class skeleton for missing 
relationships before I wrote any real logic.

The most effective prompts were narrow and specific to one concern at a time — for example, 
"implement sort_by_time using a lambda key on preferred_time" produced better, more focused 
results than a vague "make the scheduler smart." Prompts that asked it to *explain its 
reasoning* before making a change (like the timedelta/due_date explanation, or the 
sort_by_priority negation explanation) were also especially useful, since they caught 
potential issues and taught me the underlying concept rather than just handing me code I'd 
have to trust blindly. Starting a fresh chat session for each new phase (e.g., a dedicated 
session for Phase 4's algorithmic work, and another for Phase 5's testing) also helped keep 
each conversation focused on one concern instead of accumulating unrelated context.

**b. Judgment and verification**

One clear example came during Phase 4's evaluation step: I asked my AI assistant how 
`sort_by_priority()` could be simplified for readability. It considered replacing the 
`-task.priority` negation trick with the seemingly more "Pythonic" `reverse=True`, but 
correctly identified that this would introduce a real bug — `reverse=True` flips the 
*entire* sort order, including the time tie-break, so two equal-priority tasks would come 
out in the wrong (descending) time order instead of ascending. I kept the original 
negation-based version rather than "simplifying" it, since the seemingly cleaner 
alternative was actually incorrect. I verified this myself by manually tracing through what 
would happen to two HIGH-priority tasks at different times under each version, rather than 
just trusting the AI's explanation at face value.

A second example: during test planning in Phase 5, my AI assistant found three real latent 
bugs (a double-completion bug in `mark_complete()`, a silent no-op for unknown `frequency` 
values, and the non-zero-padded time sort issue). Rather than asking it to silently fix all 
three, I chose to have it write tests that *document* the current behavior as known 
limitations, since fixing them was out of scope for this project's timeline. This was a 
deliberate judgment call — I verified this was the right call by confirming the limitations 
wouldn't affect a typical pet owner's actual usage pattern, and by documenting them 
honestly in the README and confidence rating rather than hiding them.

---

## 4. Testing and Verification

**a. What you tested**

My test suite (32 tests total) covers task completion and addition, sorting correctness 
(chronological order, priority ordering with a time tie-break, and stability when two 
tasks share the same time), filtering (by pet name, by completion status, both combined, 
and the important `None` vs `False` distinction for the `completed` filter), conflict 
detection (same-time clashes, multi-task clashes, exclusion of completed tasks, and 
unassigned-pet labeling), recurring tasks (daily/weekly respawn with `due_date` correctly 
advanced via `timedelta`, including a deliberately constructed month-boundary case), and 
several empty/edge states (a pet with no tasks, an owner with no pets, an empty plan). 
These behaviors mattered because they're the actual logic a pet owner depends on to trust 
the schedule they're shown — if sorting or conflict detection silently misbehaved, the app 
would give bad advice without any visible error.

I also included three tests that intentionally document known limitations rather than 
hide them: non-zero-padded time strings sorting incorrectly, an unknown `frequency` value 
silently behaving like a one-off task, and calling `mark_complete()` twice on a recurring 
task spawning a second occurrence. These tests pass today by asserting the current 
(imperfect) behavior, so if I ever fix the underlying logic, these specific tests will fail 
and flag exactly where the fix needs to happen.

**b. Confidence**

I'd rate my confidence at 4 out of 5 stars. The core scheduling logic — sorting, filtering, 
conflict detection, and recurrence — is thoroughly tested and behaves correctly for the 
scenarios a typical pet owner would actually hit. I'm holding back one star because of the 
three documented known limitations, plus the fact that `available_minutes` isn't enforced 
at all, meaning the "plan" doesn't actually respect a real time budget yet. If I had more 
time, I'd test: a full end-to-end scenario where the schedule genuinely exceeds the 
available time budget (currently untestable since the feature doesn't exist), what happens 
if `Owner.preferences` is read by scheduling logic in the future, and behavior when a `Pet` 
is removed from an `Owner` after tasks have already been added to it (a scenario the current 
model doesn't explicitly handle).

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how the Task-Pet back-reference and Priority enum design decisions 
held up throughout the entire project. Both were flagged by an AI code review very early 
(Phase 1), before I'd written any real logic, and both turned out to be genuinely important 
foundations — the back-reference made `explain_plan()` and conflict messages readable 
("Rex: Morning walk" instead of just "Morning walk"), and the Priority enum made correct 
sorting possible without string-comparison bugs. Catching these early, before they were 
baked into a lot of working code, saved significant rework later.

**b. What you would improve**

If I had another iteration, I'd implement the `available_minutes` time-budget enforcement 
that the Scheduler currently accepts but ignores — right now `generate_plan()` just sorts 
everything regardless of whether it actually fits in the owner's available time, which is a 
real gap between what the class's constructor implies and what it actually does. I'd also 
fix the double-completion bug in `mark_complete()` rather than just documenting it, since a 
user could plausibly double-click a "Mark complete" button in the UI and get an unintended 
duplicate task.

**c. Key takeaway**

The biggest thing I learned about being the "lead architect" when working with AI is that 
the most valuable moments weren't when the AI wrote correct code — that was expected — but 
when it explained *why* a seemingly reasonable alternative was actually wrong, like the 
`reverse=True` sorting bug or the non-zero-padded time string issue. My job wasn't to write 
every line myself, but to ask the right follow-up questions, decide which tradeoffs were 
acceptable for this project's scope, and make sure limitations were documented honestly 
rather than either hidden or silently "fixed" without understanding the full implication. 
AI assistance was fastest and most reliable when I gave it narrow, well-scoped tasks and 
asked it to explain its reasoning, rather than open-ended requests to "make it smarter."