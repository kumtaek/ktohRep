# Daily Monitoring Runbook

Operators should run the following commands each day to catch regressions early.

## Silent Failure Detector

```bash
python phase1/monitoring/silent_failure_detector.py --project-name <project_name>
```

Generates an alert report and exits with a non‑zero status if silent failures are detected.

## Completeness Reporter

```bash
python phase1/metrics/completeness_reporter.py --project-name <project_name>
```

Produces a detailed completeness assessment and recommendations for improvement.

## Comprehensive System Tests

```bash
pytest tests/comprehensive_system_tests.py -q
```

Runs end‑to‑end health checks covering database connectivity, analysis quality, and visualization integrity.
