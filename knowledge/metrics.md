---
type: Metric Definitions
title: Sales Metrics
description: Definitions of revenue, successful orders, payment attempts and payment failure rate.
tags: [metrics, sales, payments]
status: stable
---

# Metrics (DEMO DATA)

- **Revenue** = sum of `orders.amount` where `orders.status = 'paid'`.
- **Successful orders** = count of `orders` where `status = 'paid'`.
- **Payment attempts** = count of rows in `payment_attempts`.
- **Payment failure rate** = failed attempts / all attempts (`payment_attempts.status = 'failed'`), as a percentage.
- Always compare **matching time windows** (same start and end time of day on both days). Never compare a partial day to a full day.

See also: [Tables](tables.md) for the columns used, [Runbook](runbook.md) for how to use these.
