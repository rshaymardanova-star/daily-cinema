from prometheus_client import Counter, Histogram, Gauge

ML_JOB_DURATION = Histogram(
    "dailycinema_ml_job_duration_seconds",
    "Duration of ML jobs in seconds",
    ["status"],
    buckets=[1, 5, 10, 30, 60, 120, 300],
)

RENDER_DURATION = Histogram(
    "dailycinema_render_duration_seconds",
    "Duration of render jobs in seconds",
    ["status"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600],
)

ORCHESTRATOR_LATENCY = Histogram(
    "dailycinema_orchestrator_latency_seconds",
    "End-to-end orchestrator pipeline latency",
    buckets=[5, 10, 30, 60, 120, 300, 600],
)

ERROR_COUNTER = Counter(
    "dailycinema_errors_total",
    "Total error count",
    ["component", "error_type"],
)

JOBS_IN_PROGRESS = Gauge(
    "dailycinema_jobs_in_progress",
    "Number of jobs currently in progress",
    ["job_type"],
)

JOBS_TOTAL = Counter(
    "dailycinema_jobs_total",
    "Total jobs processed",
    ["job_type", "status"],
)

QUEUE_SIZE = Gauge(
    "dailycinema_queue_size",
    "Current queue size",
    ["queue_name"],
)

RETRY_COUNTER = Counter(
    "dailycinema_retries_total",
    "Total retry attempts",
    ["job_type"],
)

ACU_BUDGET_USED = Gauge(
    "dailycinema_acu_budget_used",
    "ACU budget consumed by current task",
    ["project_id"],
)

ACU_BUDGET_WARNINGS = Counter(
    "dailycinema_acu_budget_warnings_total",
    "ACU budget warning events",
)

ACU_FALLBACK_EVENTS = Counter(
    "dailycinema_acu_fallback_total",
    "ACU automatic fallback to light mode events",
)
