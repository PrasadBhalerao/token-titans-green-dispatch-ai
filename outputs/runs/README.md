# Run Artifacts

Store generated run outputs here, grouped by run ID.

Expected structure:

```text
outputs/runs/<run_id>/
  baseline_plan.json
  optimized_plan.json
  metrics_summary.json
  agent_trace.json
  approval_audit.json
  disruption_reoptimized_plan.json
```

Do not store confidential, customer, personal, or client-branded data in this folder.
