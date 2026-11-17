# Scenario D — recovered from `Cloud Resource and Cost Optimization Advisor_4.pdf`

## Page 1/8

Cloud Resource and Cost
Optimization Advisor
Six agents, one scenario, side-by-side. All data is simulated. Agents only
recommend; nothing changes any cloud resource.
Scenario D: Latency is slightly high, cost
is near budget, and CPU is moderate with
intermittent spikes.
Instance
c5.xlarge
Monthly cost
$122
CPU now
64.0%
Response
now
364 ms
Availabilit
y
99.40%
CPU avg 78.0% over last 6h · limit 80.0% · p95 330.0 ms · target 300 ms · availability
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
D: Latency is slightly hi
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
400
Response ms
Target
Agent decisions
Agents differ because each uses a different decision mechanism
(rules vs state vs goal test vs utility vs learned rates vs LLM+tools).
scale_up: Simple Reflex, Model-Based Reflex, Goal-Based, Utility-
Based, Learning, LLM (tool-evidence fallback)
Simple Reflex: SCALE_UP - Upsize to m5.xlarge ($138/mo)
Current state: Ambiguous mixed signals: instance=c5.xlarge,
cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr,
autoscaling=True (latency>SLA, availability<SLA)
Reasoning: Simple reflex: IF cpu>=85 OR p95>300 THEN scale_up.
Observed cpu=64.0%, p95=330.0ms, cost=$0.17/hr, gap=49.0.
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
2/8

## Page 3/8

Trade-offs: Fast and deterministic, but ignores history, multi-
objective scoring, and candidate instance catalog.
Monitoring plan: Re-evaluate the same threshold rules next
window.
Model-Based Reflex: SCALE_UP - Upsize to m5.xlarge ($138/mo)
Current state: Ambiguous mixed signals: instance=c5.xlarge,
cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr,
autoscaling=True (latency>SLA, availability<SLA)
Reasoning: Model-based reflex used internal state: believed
breach_streak=1, avg_cpu=64.0, avg_p95=330.0.
Trade-offs: Uses short memory of unseen trend, but still no explicit
goal search or utility ranking.
Monitoring plan: Track breach/low-util streaks across evaluation
windows.
Goal-Based: SCALE_UP - Upsize to m5.xlarge ($138/mo)
Current state: Ambiguous mixed signals: instance=c5.xlarge,
cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr,
autoscaling=True (latency>SLA, availability<SLA)
Reasoning: Looked ahead over 5 actions; 3 pass the goal test. Took
first passing plan (scale_up). Checks: scale_up:pass,
enable_autoscaling:pass, rightsize_compute:pass, scale_down:fail,
keep_current:fail.
Trade-offs: All passing plans treated as equally good (no utility
ranking).
Monitoring plan: Verify predicted p95/cost after the change
window.
Utility-Based: SCALE_UP - Upsize to m5.xlarge ($138/mo)
Current state: Ambiguous mixed signals: instance=c5.xlarge,
cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr,
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
3/8

## Page 4/8

autoscaling=True (latency>SLA, availability<SLA)
Reasoning: Highest weighted utility (0.713) using cost=0.40,
performance=0.40, availability=0.20. Ranking: [scale_up=0.713,
enable_autoscaling=0.685, rightsize_compute=0.665].
Trade-offs: Sidebar weights change the ranking; SLO breaches
reduce performance/availability scores.
Monitoring plan: Compare realized utility vs predicted after one
billing day.
Utility ranking
Learning: SCALE_UP - Upsize to m5.xlarge ($138/mo)
Current state: Ambiguous mixed signals: instance=c5.xlarge,
cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr,
autoscaling=True (latency>SLA, availability<SLA)
Reasoning: Highest weighted utility (4.046) using cost=0.40,
performance=0.40, availability=0.20. Ranking: [scale_up=4.046,
enable_autoscaling=0.685, rightsize_compute=0.665]. Experience-
adjusted success rates: scale_up=0.67, enable_autoscaling=0.50,
rightsize_compute=0.50.
Trade-offs: Improves with outcomes, but needs enough episodes
and occasional exploration.
Monitoring plan: Compare realized utility vs predicted after one
billing day.
Utility ranking
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
4/8

## Page 5/8

Learning stats
Early counts are priors; sparse feedback can bias preferences.
Exploration may temporarily pick a suboptimal plan.
LLM (tool-evidence fallback): SCALE_UP - Upsize to m5.xlarge ($138/mo)
Current state: Ambiguous mixed signals: instance=c5.xlarge,
cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr,
autoscaling=True (latency>SLA, availability<SLA)
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
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
5/8

## Page 6/8

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
:
:
:
:
0 :
"tool"
"get_resource_metrics"
"args" :
"scenario_id"
"D"
"result" :
"scenario_id"
"D"
"scenario_name"
"Ambiguous mixed signals"
"kind"
"edge"
"description"
"Latency is slightly high, cost is near b
udget, and CPU is moderate with intermitt
ent spikes."
"metrics" :
"instance_type"
"c5.xlarge"
"cpu_util_pct"
64
"memory_util_pct"
71
"p95_response_ms"
330
"error_rate_pct"
0.9
"requests_per_min"
310
"peak_cpu_util_pct"
84
"offpeak_cpu_util_pct"
35
"hourly_cost_usd"
0.17
"autoscaling_enabled"
true
"availability_pct"
99.4
1 :
"tool"
"get_cost_estimate"
"args" :
"instance_type"
"c5.xlarge"
"result" :
"instance_type"
"c5.xlarge"
"hourly_usd"
0.17
"monthly_usd"
122.4
"hours_per_month"
720
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
6/8

## Page 7/8

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
"spec" :
"vcpus"
4
"memory_gb"
8
"hourly_usd"
0.17
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
Feedback for scenario D
Record learning outcome
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
7/8

## Page 8/8

{'updated_action': 'keep_current', 'success_rate': 0.857, 'episodes':
7}
Download run JSON
11/17/26, 10:36 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
8/8
