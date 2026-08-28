import cProfile
import io
import pstats
from deliverable1_domain_model import Course, Learner
from deliverable2_registration_engine import RegistrationEngine


def profile_registration_workload(workload_size: int = 500):
    """Executes a high-volume batch registration workload to capture performance profiles."""
    course = Course("PY701", "Enterprise Python Development", capacity=600)
    engine = RegistrationEngine(course)

    for i in range(workload_size):
        learner = Learner(
            learner_id=f"L{i:04d}",
            name=f"LearnerName{i}",
            surname=f"LearnerSurname{i}",
            email=f"learner{i}@enterprise.com",
        )
        engine.process_registration(learner)


if __name__ == "__main__":
    print("=" * 70)
    print("Profiling test (cProfile)")
    print("=" * 70)

    # Initialize cProfiler instance
    profiler = cProfile.Profile()

    # Profile execution workload
    profiler.enable()
    profile_registration_workload(workload_size=500)
    profiler.disable()

    # Format profiler statistics by cumulative time
    stream_buffer = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream_buffer)
    stats.strip_dirs()
    stats.sort_stats("cumtime")

    print("\n15 Most resource intensive functions sorted by cumulative time (cumtime):")
    print("-" * 70)
    stats.print_stats(15)
    print(stream_buffer.getvalue())
    print("-" * 45)