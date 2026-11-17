# Scenario B — recovered from `Cloud Resource and Cost Optimization Advisor_2.pdf`

## Page 1/8

Cloud Resource and Cost
Optimization Advisor
Six agents, one scenario, side-by-side. All data is simulated. Agents only
recommend; nothing changes any cloud resource.
Scenario B: CPU and memory utilization
are low, but the instance is expensive.
Instance
m5.2xlarge
Monthly cost
$276
CPU now
18.0%
Response
now
159 ms
Availabilit
y
99.90%
CPU avg 24.3% over last 6h · limit 80.0% · p95 140.0 ms · target 300 ms · availability
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
5
10
15
25
30
35
Response time (ms) over 24 hours (target 300 ms)
Controls
Select scenario
B: CPU and memory ut
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
11/17/26, 10:33 AM
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
scale_down: Simple Reflex, Model-Based Reflex, Utility-Based,
Learning, LLM (tool-evidence fallback) | enable_autoscaling: Goal-
Based
Simple Reflex: SCALE_DOWN - Downsize to t3.medium ($30/mo)
Current state: Over-provisioned expensive instance:
instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms,
cost=$0.384/hr, autoscaling=False (cost>budget)
Reasoning: Simple reflex: IF cpu<=25 AND cost>0.25 THEN
scale_down. Observed cpu=18.0%, p95=140.0ms, cost=$0.384/hr,
11/17/26, 10:33 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
2/8

## Page 3/8

gap=20.0.
Trade-offs: Fast and deterministic, but ignores history, multi-
objective scoring, and candidate instance catalog.
Monitoring plan: Re-evaluate the same threshold rules next
window.
Model-Based Reflex: SCALE_DOWN - Downsize to t3.medium ($30/mo)
Current state: Over-provisioned expensive instance:
instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms,
cost=$0.384/hr, autoscaling=False (cost>budget)
Reasoning: Model-based reflex used internal state: sustained low
util streak=1.
Trade-offs: Uses short memory of unseen trend, but still no explicit
goal search or utility ranking.
Monitoring plan: Track breach/low-util streaks across evaluation
windows.
Goal-Based: ENABLE_AUTOSCALING - Keep m5.2xlarge + autoscaling
Current state: Over-provisioned expensive instance:
instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms,
cost=$0.384/hr, autoscaling=False (cost>budget)
Reasoning: Looked ahead over 5 actions; 4 pass the goal test. Took
first passing plan (enable_autoscaling). Checks: scale_up:fail,
enable_autoscaling:pass, rightsize_compute:pass,
scale_down:pass, keep_current:pass.
Trade-offs: All passing plans treated as equally good (no utility
ranking).
Monitoring plan: Verify predicted p95/cost after the change
window.
Utility-Based: SCALE_DOWN - Downsize to t3.medium ($30/mo)
11/17/26, 10:33 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
3/8

## Page 4/8

Current state: Over-provisioned expensive instance:
instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms,
cost=$0.384/hr, autoscaling=False (cost>budget)
Reasoning: Highest weighted utility (0.828) using cost=0.40,
performance=0.40, availability=0.20. Ranking: [scale_down=0.828,
enable_autoscaling=0.759, rightsize_compute=0.723,
keep_current=0.693].
Trade-offs: Sidebar weights change the ranking; SLO breaches
reduce performance/availability scores.
Monitoring plan: Compare realized utility vs predicted after one
billing day.
Utility ranking
Learning: SCALE_DOWN - Downsize to t3.medium ($30/mo)
Current state: Over-provisioned expensive instance:
instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms,
cost=$0.384/hr, autoscaling=False (cost>budget)
Reasoning: Highest weighted utility (4.161) using cost=0.40,
performance=0.40, availability=0.20. Ranking: [scale_down=4.161,
keep_current=4.026, enable_autoscaling=0.759,
rightsize_compute=0.723]. Experience-adjusted success rates:
scale_down=0.67, keep_current=0.67, enable_autoscaling=0.50,
rightsize_compute=0.50.
Trade-offs: Improves with outcomes, but needs enough episodes
and occasional exploration.
11/17/26, 10:33 AM
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
keyboard_arrow_down
LLM (tool-evidence fallback): SCALE_DOWN - Downsize to t3.medium
($30/mo)
Current state: Over-provisioned expensive instance:
instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms,
cost=$0.384/hr, autoscaling=False (cost>budget)
Reasoning: Ollama/LangChain unavailable; used deterministic tool
evidence fallback. Errors: langchain=model 'qwen3:latest' not found
(status code: 404); ollama=model 'qwen3:latest' not found (status
code: 404). Recommendation=scale_down from tools
['get_resource_metrics', 'get_cost_estimate'].
Trade-offs: Grounded in tool evidence; simulation only; model may
mis-rank soft trade-offs.
11/17/26, 10:33 AM
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
"B"
"result" :
"scenario_id"
"B"
"scenario_name"
"Over-provisioned expensive instance"
"kind"
"normal"
"description"
"CPU and memory utilization are low, but
the instance is expensive."
"metrics" :
"instance_type"
"m5.2xlarge"
"cpu_util_pct"
18
"memory_util_pct"
22
"p95_response_ms"
140
"error_rate_pct"
0.2
"requests_per_min"
95
"peak_cpu_util_pct"
28
"offpeak_cpu_util_pct"
8
"hourly_cost_usd"
0.384
"autoscaling_enabled"
false
"availability_pct"
99.9
1 :
"tool"
"get_cost_estimate"
"args" :
"instance_type"
"m5.2xlarge"
"result" :
11/17/26, 10:33 AM
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
"m5.2xlarge"
"hourly_usd"
0.384
"monthly_usd"
276.48
"hours_per_month"
720
"spec" :
"vcpus"
8
"memory_gb"
32
"hourly_usd"
0.384
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
Feedback for scenario B
11/17/26, 10:33 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
7/8

## Page 8/8

Record learning outcome
{'updated_action': 'keep_current', 'success_rate': 0.75, 'episodes': 4}
Download run JSON
11/17/26, 10:33 AM
Cloud Resource and Cost Optimization Advisor
127.0.0.1:8501
8/8
