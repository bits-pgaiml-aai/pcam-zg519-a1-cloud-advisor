# Scenario C — recovered from `Cloud Resource and Cost Optimization Advisor_3.pdf`

## Page 1/8

Cloud Resource and Cost
Optimization Advisor
Six agents, one scenario, side-by-side. All data is simulated. Agents only
recommend; nothing changes any cloud resource.
Scenario C: Workload varies sharply
during peak and off-peak hours.
Instance
m5.xlarge
Monthly cost
$138
CPU now
55.0%
Response
now
314 ms
Availabilit
y
99.60%
CPU avg 78.9% over last 6h · limit 80.0% · p95 280.0 ms · target 300 ms · availability
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
Response time (ms) over 24 hours (target 300 ms)
Controls
Select scenario
C: Workload varies sha
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
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
1/8

## Page 2/8

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
100
300
Response ms
Target
Agent decisions
Agents differ because each uses a different decision mechanism
(rules vs state vs goal test vs utility vs learned rates vs LLM+tools).
enable_autoscaling: Simple Reflex, Model-Based Reflex, Utility-
Based | scale_up: Goal-Based | keep_current: Learning, LLM (tool-
evidence fallback)
Simple Reflex: ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling
Current state: Sharp peak / off-peak variation: instance=m5.xlarge,
cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr,
autoscaling=False (no hard SLA breach)
Reasoning: Simple reflex: IF peak-offpeak gap>=50 THEN
enable_autoscaling. Observed cpu=55.0%, p95=280.0ms,
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
2/8

## Page 3/8

cost=$0.192/hr, gap=79.0.
Trade-offs: Fast and deterministic, but ignores history, multi-
objective scoring, and candidate instance catalog.
Monitoring plan: Re-evaluate the same threshold rules next
window.
keyboard_arrow_down
Model-Based Reflex: ENABLE_AUTOSCALING - Keep m5.xlarge +
autoscaling
Current state: Sharp peak / off-peak variation: instance=m5.xlarge,
cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr,
autoscaling=False (no hard SLA breach)
Reasoning: Model-based reflex used internal state: modelled
workload swing peak-offpeak=79.0.
Trade-offs: Uses short memory of unseen trend, but still no explicit
goal search or utility ranking.
Monitoring plan: Track breach/low-util streaks across evaluation
windows.
Goal-Based: SCALE_UP - Upsize to m5.2xlarge ($276/mo)
Current state: Sharp peak / off-peak variation: instance=m5.xlarge,
cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr,
autoscaling=False (no hard SLA breach)
Reasoning: Looked ahead over 5 actions; 4 pass the goal test. Took
first passing plan (scale_up). Checks: scale_up:pass,
enable_autoscaling:pass, rightsize_compute:pass, scale_down:fail,
keep_current:pass.
Trade-offs: All passing plans treated as equally good (no utility
ranking).
Monitoring plan: Verify predicted p95/cost after the change
window.
Utility-Based: ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
3/8

## Page 4/8

Current state: Sharp peak / off-peak variation: instance=m5.xlarge,
cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr,
autoscaling=False (no hard SLA breach)
Reasoning: Highest weighted utility (0.820) using cost=0.40,
performance=0.40, availability=0.20. Ranking:
[enable_autoscaling=0.820, rightsize_compute=0.762,
scale_up=0.718, keep_current=0.672].
Trade-offs: Sidebar weights change the ranking; SLO breaches
reduce performance/availability scores.
Monitoring plan: Compare realized utility vs predicted after one
billing day.
Utility ranking
Learning: KEEP_CURRENT - Keep m5.xlarge
Current state: Sharp peak / off-peak variation: instance=m5.xlarge,
cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr,
autoscaling=False (no hard SLA breach)
Reasoning: Highest weighted utility (6.672) using cost=0.40,
performance=0.40, availability=0.20. Ranking: [keep_current=6.672,
scale_up=4.051, enable_autoscaling=0.820,
rightsize_compute=0.762]. Experience-adjusted success rates:
keep_current=0.80, scale_up=0.67, enable_autoscaling=0.50,
rightsize_compute=0.50.
Trade-offs: Improves with outcomes, but needs enough episodes
and occasional exploration.
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
4/8

## Page 5/8

Monitoring plan: Compare realized utility vs predicted after one
billing day.
Utility ranking
Learning stats
Early counts are priors; sparse feedback can bias preferences.
Exploration may temporarily pick a suboptimal plan.
LLM (tool-evidence fallback): KEEP_CURRENT - Keep m5.xlarge
Current state: Sharp peak / off-peak variation: instance=m5.xlarge,
cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr,
autoscaling=False (no hard SLA breach)
Reasoning: Ollama/LangChain unavailable; used deterministic tool
evidence fallback. Errors: langchain=model 'qwen3:latest' not found
(status code: 404); ollama=model 'qwen3:latest' not found (status
code: 404). Recommendation=keep_current from tools
['get_resource_metrics', 'get_cost_estimate'].
Trade-offs: Grounded in tool evidence; simulation only; model may
mis-rank soft trade-offs.
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
5/8

## Page 6/8

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
0 :
"tool"
"get_resource_metrics"
"args" :
"scenario_id"
"C"
"result" :
"scenario_id"
"C"
"scenario_name"
"Sharp peak / off-peak variation"
"kind"
"normal"
"description"
"Workload varies sharply during peak and
off-peak hours."
"metrics" :
"instance_type"
"m5.xlarge"
"cpu_util_pct"
55
"memory_util_pct"
48
"p95_response_ms"
280
"error_rate_pct"
0.6
"requests_per_min"
260
"peak_cpu_util_pct"
91
"offpeak_cpu_util_pct"
12
"hourly_cost_usd"
0.192
"autoscaling_enabled"
false
"availability_pct"
99.6
1 :
"tool"
"get_cost_estimate"
"args" :
"instance_type"
"m5.xlarge"
"result" :
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
6/8

## Page 7/8

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
{
:
:
:
}
]
}
}
]
"instance_type"
"m5.xlarge"
"hourly_usd"
0.192
"monthly_usd"
138.24
"hours_per_month"
720
"spec" :
"vcpus"
4
"memory_gb"
16
"hourly_usd"
0.192
"burst"
false
"cheaper_alternatives" :
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
2 :
"instance_type"
"m5.large"
"hourly_usd"
0.096
"monthly_usd"
69.12
Update Learning Agent experience
Action outcome to record
keep_current
Mark as …
Notes
Feedback for scenario C
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
7/8

## Page 8/8

Record learning outcome
{'updated_action': 'keep_current', 'success_rate': 0.833, 'episodes':
6}
Download run JSON
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
8/8
