# Tracing Order Timeouts With Python

![Cover illustration showing request r08 returning a 504 on the orders endpoint](<screenshots/Tracing order timeouts with Python.png>)

After a simulated deployment at 10:05 UTC, the server-error rate on `/orders` rose from 25% to 50%. `/catalog` recorded zero server errors in both windows. I used Python to compare the two routes, then followed one failed order to see where it spent its time.

## Reproduce the analysis

From the root of this repository, run:

```bash
python3 analyze.py
```

The script uses Python’s standard library and reads the included [sample request log](requests.jsonl). You can compare your output with [my saved results](results.txt).

## What changed after deployment?

| Endpoint | Five minutes before | Five minutes after |
| --- | --- | --- |
| `/orders` | 1 of 4 requests (25%) | 3 of 6 requests (50%) |
| `/catalog` | 0 of 3 requests (0%) | 0 of 3 requests (0%) |

The log contained 18 requests. Sixteen fell inside the comparison windows. Each window included its start and excluded its end, so `r08` at exactly 10:05:00 counted in the after window.

A search across the whole file found four `504` responses. The first, `r00`, arrived at 09:59:59, one second before the comparison began. The single `/orders` error inside the before window was a `500`. All three errors in the after window were `504`s.

[See the four matches in the raw log](<screenshots/01-raw-log-504s.png>)

![Python output showing error counts and rates for both endpoints](<screenshots/02-before-after-error-rates.png>)

## Following request r08

The simulated rollout records showed that the number of ready orders workers fell from four to one. The timing records for `r08` showed 230 ms waiting for a worker and 44 ms processing. That added up to 274 ms, exceeding the gateway’s 250 ms deadline by 24 ms.

I initially read 20 ms as the overrun. It was the time **remaining** when processing began. Most of this request’s time went into waiting for a worker, which made reduced worker capacity my leading explanation.

![Simulated rollout and request timing evidence for r08](<screenshots/03-orders-timeout-evidence.png>)

## How I’d verify recovery

My proposed rollback was to restore four workers. I’d confirm all four were ready, then compare queue times and `/orders` error rates across several windows with similar traffic. The simulation ended before the rollback was tested.

## Medium write-up

[Why Were Orders Timing Out After the Deployment?](https://medium.com/@asowoseyi35/why-were-orders-timing-out-after-the-deployment-a82b2d47d1ae)

