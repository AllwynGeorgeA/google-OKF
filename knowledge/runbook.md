---
type: Runbook
title: Investigating a Sales Drop
description: Step-by-step process for comparing today vs yesterday and finding likely causes.
tags: [runbook, investigation]
status: stable
---

# Runbook: investigating a sales drop (DEMO DATA)

1. Compare revenue and successful orders for matching time windows, today vs yesterday.
2. Compare payment failure rate for the same windows.
3. If failures rose, break them down by failure reason and by payment method.
4. Check whether the change is concentrated in one reason or method.
5. Report numbers first, then **possible** causes. Correlation is not proof: say what to check next (e.g. payment provider status, recent deploys). Do not claim a proven cause.

See also: [Metrics](metrics.md), [Tables](tables.md).
