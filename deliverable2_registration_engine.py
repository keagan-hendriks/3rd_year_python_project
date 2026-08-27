import threading
from typing import List, Dict, Any, Set
from deliverable1_domain_model import Learner, Course, Registration


class RegistrationEngine:
    """registration processing engine supporting concurrent registrations,
    business rules, validation, a duplicate check and mutex lock used
    """

    def __init__(self, course: Course):
        self.course = course
        #Mutex lock to prebvent deadlocks
        self._lock = threading.Lock()
        #Hash set for O(1) duplicate ID verification, uses learner id
        self._registered_learner_ids: Set[str] = set()

        #desk check, remove when done
        self.successful_registrations: List[Dict[str, Any]] = []
        self.unsuccessful_registrations: List[Dict[str, Any]] = []

    def process_registration(self, learner: Learner) -> bool:
        """process for a single learner registration thread
        Enforces validation, duplicate prevention, and capacity limits.
        """
        with self._lock:
            full_name = f"{learner.name} {learner.surname}"

            #basic validation(fields)
            if not learner.learner_id or not learner.name or not learner.surname:
                self.unsuccessful_registrations.append(
                    {
                        "learner_id": getattr(learner, "learner_id", "N/A"),
                        "name": full_name,
                        "reason": "Validation Failure: Missing Learner ID, Name, or Surname",
                    }
                )
                print(
                    f"[Rejected request] Validation failed for Learner ID: {learner.learner_id}"
                )
                return False

            #business rule for duplicates
            if learner.learner_id in self._registered_learner_ids:
                self.unsuccessful_registrations.append(
                    {
                        "learner_id": learner.learner_id,
                        "name": full_name,
                        "reason": "Duplicate registration attempt",
                    }
                )
                print(
                    f"[Duplicate] Learner {full_name} is already registered."
                )
                return False

            #secondary business rule for course capacity, remember that both have to run
            if self.course.is_full():
                self.unsuccessful_registrations.append(
                    {
                        "learner_id": learner.learner_id,
                        "name": full_name,
                        "reason": "Course capacity reached",
                    }
                )
                print(
                    f"[course full] Learner {full_name} rejected. Course full."
                )
                return False

            #use factory method from deliverable 1 to commit changes
            try:
                registration = learner.register_course(self.course)
                self._registered_learner_ids.add(learner.learner_id)
                self.successful_registrations.append(
                    {
                        "learner_id": learner.learner_id,
                        "name": full_name,
                        "registration_id": registration.registration_id,
                    }
                )
                print(f"[succesgull registration] {full_name} registered")
                return True

            except ValueError as e:
                self.unsuccessful_registrations.append(
                    {
                        "learner_id": learner.learner_id,
                        "name": full_name,
                        "reason": str(e),
                    }
                )
                print(f"[error: couldn't register] {full_name} error: {e}")
                return False

    def generate_summary(self) -> None:
        """desk check summary showing successful and failed transactions"""
        print("\n" + "=" * 45)
        print("Registration results:")
        print("=" * 45)
        print(
            f"Target Course       : {self.course.title} ({self.course.course_id})"
        )
        print(f"Course Capacity     : {self.course.capacity}")
        print(f"Total Registrations : {len(self.successful_registrations)}")
        print(f"Total Rejected      : {len(self.unsuccessful_registrations)}")
        print("-" * 45)

        print("Successfukl registstrations:")
        if self.successful_registrations:
            for rec in self.successful_registrations:
                print(
                    f" - ID: {rec['learner_id']} | Name: {rec['name']} | Reg ID: {rec['registration_id']}"
                )
        else:
            print(" None")

        if self.unsuccessful_registrations:
            print("-" * 45)
            print("failed registrations:")
            for rec in self.unsuccessful_registrations:
                print(
                    f" - ID: {rec['learner_id']} | Name: {rec['name']} | Reason: {rec['reason']}"
                )
        print("=" * 45)


#desk check and screenshots
if __name__ == "__main__":
    print("demo for registrations")
    print("=" * 45)

    # Instantiate course with capacity set to 10
    test_course = Course("PY701", "Enterprise Python Development", capacity=10)
    engine = RegistrationEngine(test_course)

    # Generate 10 valid learners
    simulated_learners = [
        Learner(
            f"L{i:03d}", "Learner", f"{i}", f"learner{i}@enterprise.com"
        )
        for i in range(1, 11)
    ]

    # Add edge cases to test duplicate checks and capacity overflow
    simulated_learners.append(
        Learner(
            "L001",
            "Learner",
            "1 Duplicate",
            "learner1@enterprise.com",
        )
    )
    simulated_learners.append(
        Learner(
            "L011",
            "Learner",
            "11 Overflow",
            "learner11@enterprise.com",
        )
    )

    # Dispatch requests concurrently using threads
    threads: List[threading.Thread] = []
    for learner in simulated_learners:
        t = threading.Thread(
            target=engine.process_registration, args=(learner,)
        )
        threads.append(t)
        t.start()

    # Synchronize all threads
    for t in threads:
        t.join()

    # Display execution summary report
    engine.generate_summary()