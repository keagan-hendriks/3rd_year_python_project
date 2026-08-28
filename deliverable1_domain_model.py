from datetime import date
from typing import List


class Learner:
    """represents a learner in the platform"""

    def __init__(self, learner_id: str, name: str, surname: str, email: str):
        self.learner_id = learner_id
        self.name = name
        self.surname = surname
        self.email = email
        self.registrations: List["Registration"] = []
        self.support_tickets: List["SupportTicket"] = []

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if "@" not in value or "." not in value:
            raise ValueError(f"Invalid email address format: '{value}'")
        self._email = value

    def register_course(self, course: "Course") -> "Registration":
        """Factory helper method to register learner for a course."""
        return Registration(
            f"Created registration: Learner ({self.learner_id}) for course ({course.course_id})", self, course
        )

    def __str__(self) -> str:
        return f"Learner ID: {self.learner_id}, Name: {self.name}, Surname: {self.surname}, Email: {self.email}"


class Course:
    """course representation in platform"""

    def __init__(self, course_id: str, title: str, capacity: int = 30):
        self.course_id = course_id
        self.title = title
        self.capacity = capacity
        self.assessments: List["Assessment"] = []
        self.registrations: List["Registration"] = []
        self._active_count = 0  #part of optimisation, is a state tracker

    @property
    def capacity(self) -> int:
        return self._capacity

    @capacity.setter
    def capacity(self, value: int):
        if value <= 0:
            raise ValueError("Course capacity cannot be negative or null.")
        self._capacity = value

    # commented out for question 3.3 to prove optimisation
    # def is_full(self) -> bool:
    #     active_registrations = [
    #         r for r in self.registrations if r.status == "ACTIVE"
    #     ]
    #     return len(active_registrations) >= self.capacity

    # optimised solution for def is_full(self)
    def is_full(self) -> bool:
        """O(1) complexity solution attempt"""
        return self._active_count >= self.capacity

    def __str__(self) -> str:
        return f"Course: {self.course_id} - {self.title}"


class Registration:
    """conjugate class between Learners and Courses, creates many to many for those classes"""

    def __init__(self, registration_id: str, learner: Learner, course: Course):
        if course.is_full():
            raise ValueError(
                f"Cannot register: Course '{course.title}' has reached full capacity."
            )

        self.registration_id = registration_id
        self.learner = learner
        self.course = course
        self.status = "ACTIVE"  # ACTIVE, COMPLETED, CANCELLED
        self.registration_date = date.today()

        #bi-directional association
        learner.registrations.append(self)
        course.registrations.append(self)

        #OPTIMIZATION FIX: Increment course active student counter
        course._active_count += 1

    def complete(self):
        if self.status == "ACTIVE":
            self.course._active_count -= 1
        self.status = "COMPLETED"

    def cancel(self):
        if self.status == "ACTIVE":
            self.course._active_count -= 1
        self.status = "CANCELLED"

    def __str__(self) -> str:
        return f"{self.learner.name} is registered for {self.course.title}"


class Assessment:
    """represents an assignment in a course"""

    def __init__(
        self, assessment_id: str, course: Course, title: str, max_score: float
    ):
        self.assessment_id = assessment_id
        self.course = course
        self.title = title
        self.max_score = max_score

        # Wire association with course
        course.assessments.append(self)

    @property
    def max_score(self) -> float:
        return self._max_score

    @max_score.setter
    def max_score(self, value: float):
        if value < 0:
            raise ValueError("Max score cannot be negative.")
        self._max_score = float(value)

    def __str__(self) -> str:
        return f"Assessment: {self.title} ({self.course.course_id}) - Max Score: {self.max_score}"


class SupportTicket:
    """Tracks customer support requests raised by a Learner."""

    VALID_PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    VALID_STATUSES = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]

    def __init__(self, ticket_id: str, learner: 'Learner', description: str, priority: str = "MEDIUM"):
        self.ticket_id = ticket_id
        self.learner = learner
        self.description = description
        self.status = "OPEN"

        # Set priority using validation logic
        self.update_priority(priority)

        # Wire association with learner
        learner.support_tickets.append(self)

    @property
    def priority(self) -> str:
        return self._priority

    def update_priority(self, new_priority: str) -> None:
        """Updates the priority level of the support ticket with validation."""
        formatted_priority = new_priority.upper()
        if formatted_priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority '{new_priority}'. Must be one of: {self.VALID_PRIORITIES}"
            )
        self._priority = formatted_priority

    def update_status(self, new_status: str) -> None:
        """Updates the ticket lifecycle status."""
        formatted_status = new_status.upper()
        if formatted_status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{new_status}'. Must be one of: {self.VALID_STATUSES}"
            )
        self.status = formatted_status

    def __str__(self) -> str:
        return f"Ticket [{self.ticket_id}] - Priority: {self.priority} - Status: {self.status} | {self.description}"


# sample execution block
if __name__ == "__main__":
    print("domain model demo")
    print("=" * 30)
    print("OUTPUT")
    print("-" * 30)

    # Instantiate Learner and Course
    learner = Learner("L001", "Linus", "Torvalds", "linus.torvalds@enterprise.com")
    course = Course("PY701", "Enterprise Python Development", capacity=25)

    print(learner)
    print(course)

    # Perform Registration
    registration = learner.register_course(course)
    print(registration)

    # Instantiate Assessment and SupportTicket
    assessment = Assessment("A101", course, "Midterm Practical", 100.0)
    ticket = SupportTicket(
        "TK-901", learner, "Cannot access portal labs", priority="HIGH"
    )

    print("\nINTERACTION VERIFICATION")
    print("-" * 46)
    print(f"Registered Assessments in {course.course_id}: {len(course.assessments)}")
    print(f"Logged Support Tickets for {learner.name}: {len(learner.support_tickets)}")
    print(f"Is Course Full? {course.is_full()} ({len(course.registrations)}/{course.capacity} enrolled)")