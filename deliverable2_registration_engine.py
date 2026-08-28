import threading
from typing import List, Dict, Any, Set, Optional
from deliverable1_domain_model import Learner, Course, Registration


class RegistrationEngine:
    """registration processing engine
    NB!!optional!! bugzot logger dependency injection
    """

    def __init__(self, course: Course, logger: Optional[Any] = None):
        self.course = course
        self.logger = logger
        self._lock = threading.Lock()
        self._registered_learner_ids: Set[str] = set()

        self.successful_registrations: List[Dict[str, Any]] = []
        self.unsuccessful_registrations: List[Dict[str, Any]] = []

    def process_registration(self, learner: Learner) -> bool:
        """Processes registrations, forwards events to logger"""
        with self._lock:
            full_name = f"{learner.name} {learner.surname}".strip()

            #basic validation (fields)
            if not learner.learner_id or not learner.name or not learner.surname:
                reason = "Validation failure: missing ID, name, or surname"
                self.unsuccessful_registrations.append(
                    {"learner_id": getattr(learner, "learner_id", "N/A"), "name": full_name, "reason": reason}
                )
                if self.logger:
                    self.logger.error("Validation Failure", f"Learner {getattr(learner, 'learner_id', 'Unknown')} missing required attributes")
                else:
                    print(f"[Rejected] Validation failed for learner ID: {learner.learner_id}")
                return False

            #validatiojn for email
            if "@" not in learner.email or "." not in learner.email:
                reason = "Validation failure: invalid email format"
                self.unsuccessful_registrations.append(
                    {"learner_id": learner.learner_id, "name": full_name, "reason": reason}
                )
                if self.logger:
                    self.logger.error("Validation Failure", f"Learner {learner.learner_id} ({full_name}) has invalid email format: '{learner.email}'")
                else:
                    print(f"[Rejected] {full_name} has invalid email format.")
                return False

            #dupl check
            if learner.learner_id in self._registered_learner_ids:
                reason = "Duplicate registration attempt"
                self.unsuccessful_registrations.append(
                    {"learner_id": learner.learner_id, "name": full_name, "reason": reason}
                )
                if self.logger:
                    self.logger.warning("Duplicate Registration", f"Learner {learner.learner_id} ({full_name}) is already registered")
                else:
                    print(f"[Duplicate] Learner {full_name} is already registered.")
                return False

            #capacity check
            if self.course.is_full():
                reason = "Course capacity reached"
                self.unsuccessful_registrations.append(
                    {"learner_id": learner.learner_id, "name": full_name, "reason": reason}
                )
                if self.logger:
                    self.logger.warning("Capacity Violation", f"Registration rejected for {full_name}. Course '{self.course.title}' is full.")
                else:
                    print(f"[Course full] Learner {full_name} rejected. Course full.")
                return False

            # 5. Successful Execution
            try:
                registration = learner.register_course(self.course)
                self._registered_learner_ids.add(learner.learner_id)
                self.successful_registrations.append(
                    {"learner_id": learner.learner_id, "name": full_name, "registration_id": registration.registration_id}
                )
                if self.logger:
                    self.logger.info("Registration Success", f"{full_name} registered successfully")
                else:
                    print(f"[Success] {full_name} registered")
                return True

            except ValueError as e:
                self.unsuccessful_registrations.append(
                    {"learner_id": learner.learner_id, "name": full_name, "reason": str(e)}
                )
                if self.logger:
                    self.logger.error("Registration Exception", f"Failed to register {full_name}: {e}")
                else:
                    print(f"[Failed] {full_name} error: {e}")
                return False

    def generate_summary(self) -> None:
        """Generates an operational summary report."""
        print("\n" + "=" * 45)
        print("Registration Summary")
        print("=" * 45)
        print(f"Target Course       : {self.course.title} ({self.course.course_id})")
        print(f"Course Capacity     : {self.course.capacity}")
        print(f"Total Registrations : {len(self.successful_registrations)}")
        print(f"Total Rejected      : {len(self.unsuccessful_registrations)}")
        print("-" * 45)

        print("Successful Transactions:")
        if self.successful_registrations:
            for rec in self.successful_registrations:
                print(f" - ID: {rec['learner_id']} | Name: {rec['name']} | Reg ID: {rec['registration_id']}")
        else:
            print(" None")

        if self.unsuccessful_registrations:
            print("-" * 45)
            print("Failed Transactions:")
            for rec in self.unsuccessful_registrations:
                print(f" - ID: {rec['learner_id']} | Name: {rec['name']} | Reason: {rec['reason']}")
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