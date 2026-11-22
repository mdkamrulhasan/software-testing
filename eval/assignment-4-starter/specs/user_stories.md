# Course Registration: User Stories

The **customer's** view of the system, agreed with the Registrar's
Office (the product owner). This file is the test basis for your
acceptance tests in Assignment 4. Every scenario you write should name
the acceptance criterion it confirms (e.g. `# US-1.3`).

The stories use the seed data in `SPEC.md` (students S01-S14, the nine
courses). Money is in dollars; the semester fee is $100 per credit for
the first 12 credits and $75 per credit above 12.

---

## US-1 Enroll in a course

**As a** student, **I want to** enroll in a course, **so that** I can
take it this semester.

| ID | Acceptance criterion |
|---|---|
| **US-1.1** | I can enroll in a course that has a free seat, if I have completed its prerequisite and the course keeps me within my credit limit. I am told my new total credits and my semester fee. |
| **US-1.2** | When I am enrolled, I receive a confirmation showing my semester fee, and the course appears on my schedule. |
| **US-1.3** | If I have not completed the prerequisite, I am told which course I am missing, I am not enrolled, and I receive a rejection saying why. |
| **US-1.4** | I can never have more than **18** credits, and I cannot add a course once I already have **more than 15**. If a course would break either rule, I am told "credit limit exceeded" and I receive a rejection. |
| **US-1.5** | If every seat is taken, I am told the course is full, I am not enrolled, and I receive a rejection. |
| **US-1.6** | If I try to enroll in a course I am already in, I am told so, and nothing changes. |

*Examples:* to be written by you (Assignment 4, Section 4).

---

## US-2 Withdraw from a course

**As a** student, **I want to** withdraw from a course, **so that** I
am not charged for a course I will not take.

| ID | Acceptance criterion |
|---|---|
| **US-2.1** | After I withdraw, the course is no longer on my schedule, and my total credits and semester fee go down. |
| **US-2.2** | My seat becomes free for someone else. |
| **US-2.3** | Withdrawing affects **only me**: every other student in the course stays enrolled. |
| **US-2.4** | If I am not in the course, I am told "not enrolled". |

*(Not part of Assignment 4.)*

---

## US-3 See my schedule

**As a** student, **I want to** see my schedule, **so that** I know
what I am taking and what I owe.

| ID | Acceptance criterion |
|---|---|
| **US-3.1** | My schedule lists the courses I am enrolled in, my total credits, and my semester fee. |
| **US-3.2** | My schedule also lists every waitlist I am on, with my position on each. |

*Example (US-3.1), automated in the starter as a worked example:*
S14 sees MTH201, HIS105, PHY230, and ENG150, 15 credits, and a fee of
$1,425.00.

---

## US-4 Waitlist for a full course

**As a** student, **I want to** join the waitlist of a full course,
**so that** I get a seat automatically if one opens.

*First draft (what the developer implemented, see SPEC.md REQ-9 to
REQ-11):* "When a course is full, students can join a waitlist. When a
seat opens, the first student on the waitlist gets it."

*Acceptance criteria, after the three-amigos session below:*

| ID | Acceptance criterion |
|---|---|
| **US-4.1** | When a course I can take is full, I can join its waitlist. I am told my position and receive a message confirming that I am waiting. |
| **US-4.2** | My position is my place among the students **still waiting**: when someone ahead of me gets a seat or leaves, I move up. |
| **US-4.3** | When a seat opens, it goes to the student who has waited longest **among those who can still take the course**. Anyone passed over is told why and taken off the waitlist. |
| **US-4.4** | The student who gets the seat is enrolled exactly as if they had enrolled themselves: same confirmation, same fee. |
| **US-4.5** | I cannot join the waitlist of a course that has a free seat, a course I am in, a course I am already waiting for, or a course I cannot take. I am told why. |
| **US-4.6** | I can leave a waitlist; I then do not get a seat when one opens. |

### Three-amigos session for US-4

Product owner: Registrar's Office. Developer: the team's backend
developer. Tester: the team's QA engineer. Every example below starts
from the seed data, with **SE499 full**: S01, S02, and S03 are enrolled
in it (3 of 3 seats).

| # | Question | Product owner's answer | Agreed example |
|---|---|---|---|
| E1 | *Tester:* What if the first student on the waitlist can no longer take the course when a seat opens -- say they have since enrolled in other courses? | Skip them, tell them why, and give the seat to the next student who can take it. A seat should never sit empty while an eligible student is waiting. | S04, then S05, join the SE499 waitlist. S04 then enrolls in MTH201, HIS105, PHY230, and CHM110 (16 credits). S01 withdraws from SE499. **S04** is told "credit limit exceeded" and is no longer waiting. **S05** is enrolled in SE499, receives a confirmation of $300.00, and is no longer waiting. SE499 is full again (3 of 3). |
| E2 | *Tester:* Is my position the order I joined in, or my place among the people still waiting? | Your place among the people still waiting. If I am second and the first person gets a seat, I am now first. | S04, S05, and S06 join the SE499 waitlist (positions 1, 2, 3). S01 withdraws; S04 gets the seat. S05's schedule shows position **1** for SE499 and S06's shows **2**. S07 then joins and is told position **3**. |
| E3 | *Developer:* Does a student who gets a seat from the waitlist pay the normal fee and get the normal confirmation? | Yes. Exactly as if they had enrolled themselves. | S04 joins the SE499 waitlist. S01 withdraws. S04 is enrolled in SE499, receives a confirmation of $300.00, sees SE499 on their schedule with 3 credits, and is no longer waiting. |
| E4 | *Developer:* Can a student wait for a course that still has free seats? | No. They should just enroll. | S01 tries to join the SE413 waitlist and is told "course has open seats". S01 is on no waitlist. |
| E5 | *Tester:* Can a student wait for a course they cannot take? | No, and tell them why, the same way as when they enroll. | S13 tries to join the SE499 waitlist, is told "prerequisite CIS350 not completed", receives a rejection saying so, and is on no waitlist. |
| E6 | *Developer:* What if nobody is waiting when a seat opens? | The seat is simply free. | S01 withdraws from SE499. SE499 has 2 of 3 seats taken; nobody else is enrolled. |
| E7 | *Tester:* If I leave the waitlist, can I still be given a seat? | No. Leaving means leaving. | S04, then S05, join the SE499 waitlist. S04 leaves it. S01 withdraws. S05 is enrolled in SE499; S04 is not enrolled in SE499 and is on no waitlist. |
| -- | *Developer:* Can a student be on several waitlists, or have a limit on how many? | Several, no limit, this release. | (recorded; no example) |
| -- | *Developer:* Should a student be able to decline a seat they were given? | Out of scope this release: they can withdraw. | (out of scope, recorded) |
