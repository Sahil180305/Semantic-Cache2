# Semantic Cache Benchmark Report

Generated: `2026-05-21 21:36:42`  
System label: `Semantic-Cache2 (3-Tier Semantic Caching Layer)`  
Scale: `11,997 requests`, `2,000 seed queries`, `50 concurrent workers`

## Read Before Citing

This report is a generated benchmark artifact. Treat it as a point-in-time experiment, not a guarantee for the current working tree. Re-run benchmarks after fixing syntax/import issues, changing cache behavior, or changing model/provider configuration.

## Cache Hit Rate

| Metric | Value |
| --- | ---: |
| Overall hit rate | 45.03% |
| Exact match rate | 16.67% |
| Semantic match rate | 21.42% |
| Miss rate | 54.97% |

## Tier Distribution

| Tier | Hit rate | Notes |
| --- | ---: | --- |
| L1 in-memory | 33.02% | Local hot cache |
| L2 Redis | 5.08% | Distributed cache tier |
| L3 PostgreSQL | 0.00% | Not active in this run |
| Index/HNSW | 0.00% | Vector path reported no tier-level hits |

## Domain Hit Rates

| Domain | Hit rate |
| --- | ---: |
| E-commerce | 48.92% |
| General | 52.46% |
| Legal | 32.00% |
| Medical | 37.98% |
| Technology | 46.73% |

## Latency

| Metric | Value |
| --- | ---: |
| Average | 1336.41 ms |
| P50 | 497.97 ms |
| P95 | 10519.48 ms |
| P99 | 15880.52 ms |
| Minimum | 19.72 ms |
| Maximum | 28561.04 ms |

By result:

| Result | Average | P50 | P95 |
| --- | ---: | ---: | ---: |
| Hit | 1974.89 ms | 48.18 ms | 13433.59 ms |
| Miss | 813.42 ms | 785.03 ms | 2097.20 ms |

By tier:

| Tier | Average | P50 | P95 |
| --- | ---: | ---: | ---: |
| L1 | 47.82 ms | 44.67 ms | 81.12 ms |
| L2 | 71.47 ms | 69.85 ms | 106.06 ms |
| Miss | 813.42 ms | 785.03 ms | 2097.20 ms |
| Multi-intent | 12542.55 ms | 12017.90 ms | 18744.83 ms |

## Throughput

| Metric | Value |
| --- | ---: |
| Requests per second | 0.0 RPS |
| Total duration | 17144.0 s |
| Concurrent workers | 50 |

The `0.0 RPS` value should be investigated before using throughput claims.

## Semantic Effectiveness

| Metric | Value |
| --- | ---: |
| Precision | 0.6842 |
| Recall | 0.4620 |
| F1 score | 0.5516 |
| True positives | 3,696 |
| False positives | 1,706 |
| True negatives | 2,291 |
| False negatives | 4,304 |

## Cost Estimate

Assumptions: `150 tokens/query`, `$0.002 / 1K tokens`.

| Metric | Value |
| --- | ---: |
| Total tokens saved | 828,944 |
| Total cost saved | $1.3710 |
| Cost saved per 1K queries | $0.1143 |
| Estimated monthly savings at 1M queries | $114.28 |

## Advanced Features

| Feature | Value |
| --- | ---: |
| Multi-intent hit rate | 69.51% |
| SWR hits | 0 |
| Streaming hits | 0 |
| Circuit breaker triggers | 0 |

## Reliability

| Metric | Value |
| --- | ---: |
| Error count | 0 |
| Error rate | 0.0000% |

## Research Notes

- Overall hit rate was 45.03% in this run.
- Semantic matches contributed 21.42 percentage points.
- Precision was 0.6842 and recall was 0.4620.
- Throughput reporting needs review because the generated value is `0.0 RPS`.
- Hit latency should be interpreted carefully because average hit latency was skewed by multi-intent paths.
