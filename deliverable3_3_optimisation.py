import time
from deliverable1_domain_model import Learner, Course, Registration


def legacy_is_full_check(course: Course) -> bool:
    """Simulates the commented-out O(N) solution for is_full() in deliverable1_domain_model"""
    active_registrations = [
        r for r in course.registrations if r.status == "ACTIVE"
    ]
    return len(active_registrations) >= course.capacity


def run_optimization_benchmark(num_requests: int = 1000):
    print("=" * 65)
    print(f"Bugzot optimisation benchmark no of requests: ({num_requests} transactions)")
    print("=" * 65)

    course_legacy = Course("PY701", "Enterprise Python", capacity=2000)
    course_optimized = Course("PY701", "Enterprise Python", capacity=2000)
    learner = Learner("L001", "Test", "User", "test@enterprise.com")

    #test registrations
    for i in range(num_requests):
        Registration(f"REG-{i}", learner, course_legacy)
        Registration(f"REG-{i}", learner, course_optimized)

    #becnhmark for old version
    start_legacy = time.perf_counter()
    for _ in range(num_requests):
        legacy_is_full_check(course_legacy)
    duration_legacy = (time.perf_counter() - start_legacy) * 1000

    #benchmark optimised ver
    start_opt = time.perf_counter()
    for _ in range(num_requests):
        course_optimized.is_full()
    duration_opt = (time.perf_counter() - start_opt) * 1000

    #summary
    improvement = (
        (duration_legacy - duration_opt) / duration_legacy
    ) * 100

    print("Performance Comparison")
    print("-" * 65)
    print(f"Old O(N) Algorithm Duration  : {duration_legacy:.3f} ms")
    print(f"Optimized O(1) Algorithm Duration: {duration_opt:.3f} ms")
    print(f"Latency Reduction in ms          : {duration_legacy - duration_opt:.3f} ms")
    print(f"Percentage improvement         : {improvement:.2f}% faster")
    print("=" * 65)


if __name__ == "__main__":
    run_optimization_benchmark()