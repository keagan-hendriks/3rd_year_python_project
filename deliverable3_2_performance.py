from datetime import datetime
import threading
import time
from typing import List, Dict, Any
from deliverable1_domain_model import Learner, Course
from deliverable2_registration_engine import RegistrationEngine
from deliverable3_1_bugzot import BugzotLogger


class BugzotPerformanceMonitor(BugzotLogger):
    """Extends BugzotLogger with application performance monitoring (APM) metrics,

    tracking execution timestamps, latency in milliseconds, and transaction statistics.
    """

    def __init__(self):
        super().__init__()
        self._performance_metrics: List[Dict[str, Any]] = []
        self._perf_lock = threading.Lock()

    def record_performance_metric(
        self,
        operation: str,
        start_time: float,
        end_time: float,
        status: str,
        details: str,
    ) -> None:
        """Records granular timing information for a single transaction."""
        duration_ms = (end_time - start_time) * 1000
        start_timestamp = datetime.fromtimestamp(start_time).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]
        end_timestamp = datetime.fromtimestamp(end_time).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]

        metric_entry = {
            "operation": operation,
            "start_time": start_timestamp,
            "end_time": end_timestamp,
            "duration_ms": round(duration_ms, 3),
            "status": status,
            "details": details,
        }

        with self._perf_lock:
            self._performance_metrics.append(metric_entry)

    def generate_performance_report(self) -> None:
        """Generates a summary report of operational efficiency and latency statistics."""
        print("\n" + "=" * 70)
        print("Bugzot Application Performance Monitoring (APM) Report")
        print("=" * 70)

        with self._perf_lock:
            total_transactions = len(self._performance_metrics)
            if total_transactions == 0:
                print("No performance metrics captured.")
                print("=" * 70)
                return

            successful_tx = [
                m
                for m in self._performance_metrics
                if m["status"] == "Success"
            ]
            failed_tx = [
                m for m in self._performance_metrics if m["status"] != "Success"
            ]

            durations = [m["duration_ms"] for m in self._performance_metrics]
            avg_duration = sum(durations) / total_transactions
            min_duration = min(durations)
            max_duration = max(durations)
            success_rate = (len(successful_tx) / total_transactions) * 100

            print("System Efficiency Summary")
            print("-" * 35)
            print(f"Total Transactions Processed : {total_transactions}")
            print(f"Successful Transactions      : {len(successful_tx)}")
            print(f"Failed Transactions          : {len(failed_tx)}")
            print(f"Transaction Success Rate     : {success_rate:.1f}%")
            print(f"Average Execution Speed      : {avg_duration:.3f} ms")
            print(f"Minimum Latency              : {min_duration:.3f} ms")
            print(f"Maximum Latency              : {max_duration:.3f} ms")

            print("-" * 70)
            print("Transaction Activity Audit Log")
            print("-" * 70)
            for m in self._performance_metrics:
                print(
                    f"[{m['start_time']}] {m['operation']} | Latency: {m['duration_ms']} ms | Status: {m['status']} | {m['details']}"
                )
            print("=" * 70)


class PerformanceMonitoredEngine:
    """Wrapper that times registration engine transactions using high-precision timestamps."""

    def __init__(self, course: Course, monitor: BugzotPerformanceMonitor):
        self.engine = RegistrationEngine(course, logger=monitor)
        self.monitor = monitor

    def process_registration_with_timing(self, learner: Learner) -> bool:
        """Executes process_registration while recording exact start/end timestamps and latency."""
        start_time = time.time()
        start_perf = time.perf_counter()

        full_name = (
            f"{learner.name} {learner.surname}".strip()
            if hasattr(learner, "name")
            else "Unknown"
        )

        try:
            success = self.engine.process_registration(learner)
            end_time = start_time + (time.perf_counter() - start_perf)

            status_str = "Success" if success else "Rejected"
            details = f"Learner {learner.learner_id} ({full_name}) registration request"

            self.monitor.record_performance_metric(
                operation="Registration Processing",
                start_time=start_time,
                end_time=end_time,
                status=status_str,
                details=details,
            )
            return success

        except Exception as ex:
            end_time = start_time + (time.perf_counter() - start_perf)
            self.monitor.record_performance_metric(
                operation="Registration Processing",
                start_time=start_time,
                end_time=end_time,
                status="Error",
                details=f"Exception encountered for {full_name}: {ex}",
            )
            return False


# =====================================================================
# TEST SCRIPT FOR SECTION 3.2
# =====================================================================
if __name__ == "__main__":
    print("Starting Bugzot Application Performance Monitoring Test\n")

    monitor = BugzotPerformanceMonitor()
    course = Course("PY701", "Enterprise Python Development", capacity=3)
    monitored_engine = PerformanceMonitoredEngine(course, monitor)

    # Simulated Workload (5 requests against a capacity limit of 3)
    test_learners = [
        Learner("L001", "Anele", "Dlamini", "anele.dlamini@enterprise.com"),
        Learner("L002", "Sipho", "Mokoena", "sipho.mokoena@enterprise.com"),
        Learner("L003", "Lerato", "Nkosi", "lerato.nkosi@enterprise.com"),
        Learner(
            "L001", "Anele", "Dlamini", "anele.dlamini@enterprise.com"
        ),  # Duplicate
        Learner(
            "L004", "Thando", "Maseko", "thando.maseko@enterprise.com"
        ),  # Overflow
    ]

    # Process transactions with timing tracking
    for learner in test_learners:
        monitored_engine.process_registration_with_timing(learner)
        time.sleep(0.01)  # Brief delay to distinguish timestamps

    # Generate the performance report
    monitor.generate_performance_report()exit()