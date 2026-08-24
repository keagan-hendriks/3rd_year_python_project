from abc import ABC, abstractmethod


#singleton to manage application configuration settings
class Singleton(type):
    """Metaclass single instance enforcement
     src: https://stackoverflow.com/questions/6760685/what-is-the-best-way-of-implementing-a-singleton-in-python"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


class AppConfig(metaclass=Singleton):
    """singleton configuration settings manager, is global"""

    def __init__(self):
        #prevents re-init on duplicate instance calls
        if not hasattr(self, "_initialized"):
            self.app_name = "Enterprise Learning Management Platform"
            self.max_course_capacity = 30
            self.default_priority = "MEDIUM"
            self._initialized = True


#factory for support tickets, think assignment means like ticket types
class SupportTicket(ABC):
    """abstr base class for support tickets"""

    def __init__(self, ticket_id: str, learner_name: str, description: str):
        self.ticket_id = ticket_id
        self.learner_name = learner_name
        self.description = description

    @abstractmethod
    def get_category(self) -> str:
        pass


class AcademicTicket(SupportTicket):

    def get_category(self) -> str:
        return "AcademicTicket"


class TechnicalTicket(SupportTicket):

    def get_category(self) -> str:
        return "TechnicalTicket"


class RegistrationTicket(SupportTicket):

    def get_category(self) -> str:
        return "RegistrationTicket"


class SupportTicketFactory:
    """factory cls responsible for instantiating different ticket types"""

    @staticmethod
    def create_ticket(
        ticket_type: str, ticket_id: str, learner_name: str, description: str
    ) -> SupportTicket:
        type_mapping = {
            "academic": AcademicTicket,
            "technical": TechnicalTicket,
            "registration": RegistrationTicket,
        }

        ticket_class = type_mapping.get(ticket_type.lower())
        if not ticket_class:
            raise ValueError(
                f"Incorrect ticket type: '{ticket_type}'.\n Valid types are {list(type_mapping.keys())}"
            )

        #debugging, remove when done
        #print(ticket_class(ticket_id, learner_name, description))
        return ticket_class(ticket_id, learner_name, description)


#strategy pattern for result calculations
class ResultCalculationStrategy(ABC):
    """abstr cls for strategy to calculating assessment grades/scores"""

    @abstractmethod
    def calculate(self, score: float, max_score: float) -> str:
        pass


class PercentageResultStrategy(ResultCalculationStrategy):
    """Strategy: calc raw percentage score."""

    def calculate(self, score: float, max_score: float) -> str:
        percentage_calculated = (score / max_score) * 100
        return f"{int(percentage_calculated)}"


class ClassificationResultStrategy(ResultCalculationStrategy):
    """Strategy to classify scores into academic distinctions/grades."""

    def calculate(self, score: float, max_score: float) -> str:
        percentage_calculated = (score / max_score) * 100
        if percentage_calculated >= 75:
            return "Distinction"
        elif percentage_calculated >= 50:
            return "Pass"
        else:
            return "Fail"


class AssessmentContext:
    """Context class that executes result calculations using a configured strategy."""

    def __init__(self, strategy: ResultCalculationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ResultCalculationStrategy):
        self._strategy = strategy

    def execute_calculation(self, score: float, max_score: float) -> str:
        return self._strategy.calculate(score, max_score)


#sample output, validation that patterns work correctly
if __name__ == "__main__":
    print("singleton test, prints object id of mutliple attempted instances /nif both are identical they're the same object")
    config1 = AppConfig()
    config2 = AppConfig()
    print(f"Config 1 ID: {id(config1)}")
    print(f"Config 2 ID: {id(config2)}")
    if id(config1) == id(config2):
        print("if they have same obj id = success")

    print("\nfactory tickets")
    t1 = SupportTicketFactory.create_ticket(
        "academic", "1", "Thabo", "Grade enquiry"
    )
    t2 = SupportTicketFactory.create_ticket(
        "technical", "2", "Sipho", "Login issue"
    )
    t3 = SupportTicketFactory.create_ticket(
        "registration", "3", "Lerato", "Course addition"
    )

    print(f"Created: {t1.get_category()}")
    print(f"Created: {t2.get_category()}")
    print(f"Created: {t3.get_category()}")

    print("\nstrategy pattern")
    calc = AssessmentContext(PercentageResultStrategy())
    percentage = calc.execute_calculation(82, 100)
    print(f"Percentage Result: {percentage}")

    calc.set_strategy(ClassificationResultStrategy())
    classification = calc.execute_calculation(82, 100)
    print(f"Classification Result: {classification}")