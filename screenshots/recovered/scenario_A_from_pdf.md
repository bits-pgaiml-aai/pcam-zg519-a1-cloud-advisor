# Scenario A — recovered from `Cloud Resource and Cost Optimization Advisor.pdf`

## Page 1/7

Cloud Resource and Cost
Optimization Advisor
Six agents, one scenario, side-by-side. All data is simulated. Agents only
recommend; nothing changes any cloud resource.
Scenario A: CPU utilization is
consistently high and response time
exceeds target.
Instance
m5.large
Monthly cost
$69
CPU now
92.0%
Response
now
598 ms
Availabilit
y
99.20%
CPU avg 94.0% over last 6h · limit 80.0% · p95 520.0 ms · target 300 ms · availability
target 99.5%
CPU % over 24 hours
20
18
22
24
16
14
12
10
8
0
2
4
6
20
0
40
60
80
100
Response time (ms) over 24 hours (target 300 ms)
Controls
Select scenario
A: CPU utilization is co
Utility agent weights
Cost
0.40
Performance
0.40
Availability
0.20
LLM agent (Ollama)
Model
qwen3:latest
Host
http://127.0.0.1:11434
Include LLM agent
Run all agents
11/17/26, 10:35 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
1/7

## Page 2/7

0
2
4
6
8
10
12
14
16
18
20
22
24
0
200
400
600
Response ms
Target
Agent decisions
Agents differ because each uses a different decision mechanism
(rules vs state vs goal test vs utility vs learned rates vs LLM+tools).
scale_up: Simple Reflex, Model-Based Reflex, Goal-Based, Utility-
Based, Learning, LLM (tool-evidence fallback)
Simple Reflex: SCALE_UP - Upsize to c5.xlarge ($122/mo)
Current state: High CPU / slow responses: instance=m5.large,
cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr,
autoscaling=False (latency>SLA, availability<SLA)
Reasoning: Simple reflex: IF cpu>=85 OR p95>300 THEN scale_up.
Observed cpu=92.0%, p95=520.0ms, cost=$0.096/hr, gap=8.0.
11/17/26, 10:35 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
2/7

## Page 3/7

Trade-offs: Fast and deterministic, but ignores history, multi-
objective scoring, and candidate instance catalog.
Monitoring plan: Re-evaluate the same threshold rules next
window.
Model-Based Reflex: SCALE_UP - Upsize to c5.xlarge ($122/mo)
Current state: High CPU / slow responses: instance=m5.large,
cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr,
autoscaling=False (latency>SLA, availability<SLA)
Reasoning: Model-based reflex used internal state: believed
breach_streak=1, avg_cpu=92.0, avg_p95=520.0.
Trade-offs: Uses short memory of unseen trend, but still no explicit
goal search or utility ranking.
Monitoring plan: Track breach/low-util streaks across evaluation
windows.
Goal-Based: SCALE_UP - Upsize to c5.xlarge ($122/mo)
Current state: High CPU / slow responses: instance=m5.large,
cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr,
autoscaling=False (latency>SLA, availability<SLA)
Reasoning: Looked ahead over 5 actions; 1 pass the goal test. Took
first passing plan (scale_up). Checks: scale_up:pass,
enable_autoscaling:fail, rightsize_compute:fail, scale_down:fail,
keep_current:fail.
Trade-offs: All passing plans treated as equally good (no utility
ranking).
Monitoring plan: Verify predicted p95/cost after the change
window.
Utility-Based: SCALE_UP - Upsize to c5.xlarge ($122/mo)
Current state: High CPU / slow responses: instance=m5.large,
cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr,
11/17/26, 10:35 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
3/7

## Page 4/7

autoscaling=False (latency>SLA, availability<SLA)
Reasoning: Highest weighted utility (0.681) using cost=0.40,
performance=0.40, availability=0.20. Ranking: [scale_up=0.681].
Trade-offs: Sidebar weights change the ranking; SLO breaches
reduce performance/availability scores.
Monitoring plan: Compare realized utility vs predicted after one
billing day.
Utility ranking
Learning: SCALE_UP - Upsize to c5.xlarge ($122/mo)
Current state: High CPU / slow responses: instance=m5.large,
cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr,
autoscaling=False (latency>SLA, availability<SLA)
Reasoning: Highest weighted utility (4.014) using cost=0.40,
performance=0.40, availability=0.20. Ranking: [scale_up=4.014].
Experience-adjusted success rates: scale_up=0.67.
Trade-offs: Improves with outcomes, but needs enough episodes
and occasional exploration.
Monitoring plan: Compare realized utility vs predicted after one
billing day.
Utility ranking
Learning stats
11/17/26, 10:35 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
4/7

## Page 5/7

Early counts are priors; sparse feedback can bias preferences.
Exploration may temporarily pick a suboptimal plan.
LLM (tool-evidence fallback): SCALE_UP - Upsize to c5.xlarge ($122/mo)
Current state: High CPU / slow responses: instance=m5.large,
cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr,
autoscaling=False (latency>SLA, availability<SLA)
Reasoning: Ollama/LangChain unavailable; used deterministic tool
evidence fallback. Errors: langchain=model 'qwen3:latest' not found
(status code: 404); ollama=model 'qwen3:latest' not found (status
code: 404). Recommendation=scale_up from tools
['get_resource_metrics', 'get_cost_estimate'].
Trade-offs: Grounded in tool evidence; simulation only; model may
mis-rank soft trade-offs.
Monitoring plan: Track p95 latency, CPU, and hourly cost for 24h
after any change.
Tool evidence
[
{
:
{
:
}
{
:
0 :
"tool"
"get_resource_metrics"
"args" :
"scenario_id"
"A"
"result" :
"scenario_id"
"A"
11/17/26, 10:35 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
5/7

## Page 6/7

:
:
:
{
:
:
:
:
:
:
:
:
:
:
:
}
}
}
{
:
{
:
}
{
:
:
:
:
{
:
:
:
:
}
[
"scenario_name"
"High CPU / slow responses"
"kind"
"critical"
"description"
"CPU utilization is consistently high and
response time exceeds target."
"metrics" :
"instance_type"
"m5.large"
"cpu_util_pct"
92
"memory_util_pct"
68
"p95_response_ms"
520
"error_rate_pct"
1.8
"requests_per_min"
420
"peak_cpu_util_pct"
96
"offpeak_cpu_util_pct"
88
"hourly_cost_usd"
0.096
"autoscaling_enabled"
false
"availability_pct"
99.2
1 :
"tool"
"get_cost_estimate"
"args" :
"instance_type"
"m5.large"
"result" :
"instance_type"
"m5.large"
"hourly_usd"
0.096
"monthly_usd"
69.12
"hours_per_month"
720
"spec" :
"vcpus"
2
"memory_gb"
8
"hourly_usd"
0.096
"burst"
false
"cheaper_alternatives" :
11/17/26, 10:35 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
6/7

## Page 7/7

{
:
:
:
}
{
:
:
:
}
]
}
}
]
0 :
"instance_type"
"t3.medium"
"hourly_usd"
0.0416
"monthly_usd"
29.95
1 :
"instance_type"
"t3.large"
"hourly_usd"
0.0832
"monthly_usd"
59.9
Update Learning Agent experience
Action outcome to record
keep_current
Mark as …
Notes
Feedback for scenario A
Record learning outcome
{'updated_action': 'keep_current', 'success_rate': 0.8, 'episodes': 5}
Download run JSON
11/17/26, 10:35 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
7/7
