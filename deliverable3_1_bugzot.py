from datetime import datetime
import threading
from typing import List, Dict, Any, Optional
from deliverable1_domain_model import Learner, Course
from deliverable2_registration_engine import RegistrationEngine


class BugzotLogger:
    """event logging and diagnostic monitoring subsystem
    uses threading otherwise each thread has to use the same resource!!
    """
    #keep logger optional for registration engine code to still work
    _instance: Optional["BugzotLogger"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "BugzotLogger":
        """Singleton pattern implementation to prevent dupl"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(BugzotLogger, cls).__new__(cls)
                cls._instance._logs = []
            return cls._instance

    def log_event(self, level: str, category: str, message: str) -> None:
        """Formats and records an event log tried to make it look like assignment screenshot"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level.capitalize(),
            "category": category,
            "message": message,
        }
        formatted_line = f"{timestamp} | {level.capitalize()} | {category} | {message}"

        with self._lock:
            self._logs.append(log_entry)
            print(formatted_line)

    def info(self, category: str, message: str) -> None:
        self.log_event("Info", category, message)

    def warning(self, category: str, message: str) -> None:
        self.log_event("Warning", category, message)

    def error(self, category: str, message: str) -> None:
        self.log_event("Error", category, message)

    def display_log_report(self) -> None:
        """log of bugzot reports"""
        print("\n" + "=" * 65)
        print("Bugzot Event Monitoring Log")
        print("=" * 65)
        with self._lock:
            for entry in self._logs:
                print(
                    f"{entry['timestamp']} | {entry['level']} | {entry['category']} | {entry['message']}"
                )
        print("=" * 65)


#demo for assignment purposes
if __name__ == "__main__":
    print("Starting Bugzot Monitoring Subsystem Test\n")

    #inits
    bugzot = BugzotLogger()
    test_course = Course("PY701", "Enterprise Python Development", capacity=2)

    #instantiate engine with dependency injection
    engine = RegistrationEngine(test_course, logger=bugzot)

    #basic validation
    learner1 = Learner("L001", "Anele", "Dlamini", "anele.dlamini@enterprise.com")
    learner2 = Learner("L002", "Sipho", "Mokoena", "sipho.mokoena@enterprise.com")
    engine.process_registration(learner1)
    engine.process_registration(learner2)

    #purposefull validation failure to see if bugzot catches it
    try:
        invalid_email_learner = Learner("L003", "Lerato", "Nkosi", "invalid_email_str")
        engine.process_registration(invalid_email_learner)
    except ValueError as err:
        bugzot.error("Bugzot test#1 Validation Failure", f"Learner L003 creation failed: {err}")

    #purposeful dupl to see if bugzot catches it
    print("Bugzot test #2")
    duplicate_learner = Learner("L001", "Anele", "Dlamini", "anele.dlamini@enterprise.com")
    engine.process_registration(duplicate_learner)

    #bugzot test to see if it catches capacity violation
    print("bugzot test #3")
    overflow_learner = Learner("L004", "Thando", "Maseko", "thando.maseko@enterprise.com")
    engine.process_registration(overflow_learner)

    #full summary
    bugzot.display_log_report()