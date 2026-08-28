import unittest
from deliverable1_domain_model import (
    Learner,
    Course,
    Registration,
    Assessment,
    SupportTicket,
)
from deliverable1_patterns import (
    AssessmentContext,
    PercentageResultStrategy,
    ClassificationResultStrategy,
)
from deliverable2_registration_engine import RegistrationEngine


class TestDomainValidationLogic(unittest.TestCase):
    """Tests validation logic and property constraints for q1 domain models."""

    def test_valid_learner_email(self):
        """Verifies that valid emails are correctly stored."""
        learner = Learner("L101", "Linus", "Torvalds", "linus@linux.org")
        self.assertEqual(learner.email, "linus@linux.org")

    def test_invalid_learner_email_raises_value_error(self):
        """Verifies that invalid email formats raise a ValueError"""
        with self.assertRaises(ValueError):
            Learner("L102", "Invalid", "User", "invalid_email_format")

    def test_invalid_course_capacity_raises_value_error(self):
        """Verifies that zero or negative course capacity raises a ValueError"""
        with self.assertRaises(ValueError):
            Course("C101", "Python Enterprise", capacity=0)


class TestRegistrationEngineBusinessRules(unittest.TestCase):
    """Tests registration processing and business rules"""

    def setUp(self):
        """sets up test fixtures"""
        self.course = Course("PY701", "Enterprise Python", capacity=2)
        self.engine = RegistrationEngine(self.course)
        self.learner1 = Learner("L001", "Anele", "Dlamini", "anele@enterprise.com")
        self.learner2 = Learner("L002", "Sipho", "Mokoena", "sipho@enterprise.com")
        self.learner3 = Learner("L003", "Lerato", "Nkosi", "lerato@enterprise.com")

    def test_successful_registration_processing(self):
        """normal condition verification"""
        result = self.engine.process_registration(self.learner1)
        self.assertTrue(result)
        self.assertEqual(len(self.engine.successful_registrations), 1)

    def test_duplicate_registration_prevention(self):
        """verifies duplicate behaviour"""
        self.engine.process_registration(self.learner1)
        duplicate_result = self.engine.process_registration(self.learner1)

        self.assertFalse(duplicate_result)
        self.assertEqual(len(self.engine.unsuccessful_registrations), 1)
        self.assertEqual(
            self.engine.unsuccessful_registrations[0]["reason"],
            "Duplicate registration attempt",
        )

    def test_course_capacity_limit_enforcement(self):
        """verifies course capacity"""
        self.engine.process_registration(self.learner1)
        self.engine.process_registration(self.learner2)

        # Third registration should exceed capacity of 2
        overflow_result = self.engine.process_registration(self.learner3)
        self.assertFalse(overflow_result)
        self.assertTrue(self.course.is_full())
        self.assertEqual(
            self.engine.unsuccessful_registrations[0]["reason"],
            "Course capacity reached",
        )


class TestAssessmentCalculationStrategies(unittest.TestCase):
    """Tests assessment calculation strategies via AssessmentContext."""

    def test_percentage_strategy_calculation(self):
        """verifies percentage strat"""
        context = AssessmentContext(PercentageResultStrategy())
        result = context.execute_calculation(score=82.0, max_score=100.0)
        self.assertEqual(result, "82")

    def test_classification_strategy_distinction(self):
        """verifies grade classification strategy for Distinction (>= 75%)"""
        context = AssessmentContext(ClassificationResultStrategy())
        result = context.execute_calculation(score=85.0, max_score=100.0)
        self.assertEqual(result, "Distinction")

    def test_classification_strategy_pass(self):
        """verifies grade classification strategy for Pass (50% - 74%)"""
        context = AssessmentContext(ClassificationResultStrategy())
        result = context.execute_calculation(score=60.0, max_score=100.0)
        self.assertEqual(result, "Pass")

    def test_classification_strategy_fail(self):
        """verifies grade classification strategy for Fail (< 50%)"""
        context = AssessmentContext(ClassificationResultStrategy())
        result = context.execute_calculation(score=40.0, max_score=100.0)
        self.assertEqual(result, "Fail")


class TestSupportTicketLifecycle(unittest.TestCase):
    """Tests support ticket validation and lifecycle updates."""

    def setUp(self):
        self.learner = Learner("L001", "Linus", "Torvalds", "linus@enterprise.com")
        self.ticket = SupportTicket("TK-01", self.learner, "Portal issue", priority="MEDIUM")

    def test_priority_update_validation(self):
        """Verifies valid and invalid priority updates."""
        self.ticket.update_priority("HIGH")
        self.assertEqual(self.ticket.priority, "HIGH")

        with self.assertRaises(ValueError):
            self.ticket.update_priority("INVALID_PRIORITY")

    def test_status_transition_validation(self):
        """Verifies valid status updates."""
        self.ticket.update_status("RESOLVED")
        self.assertEqual(self.ticket.status, "RESOLVED")


if __name__ == "__main__":
    unittest.main(verbosity=2)