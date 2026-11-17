# Learning agent — before / after feedback

Demonstration that the Learning agent **uses and updates** outcome history.
Uses a disposable history file (does not overwrite production `data/learning_history.json`).

**Scenario D:** Ambiguous mixed signals

## Before feedback

- Recommendation: `scale_up` — SCALE_UP - Upsize to m5.xlarge ($138/mo)
- Success rates: `{'keep_current': 0.5, 'scale_up': 0.5, 'scale_down': 0.5, 'enable_autoscaling': 0.5, 'rightsize_compute': 0.5}`
- Reasoning: Highest weighted utility (0.713) using cost=0.40, performance=0.40, availability=0.20. Ranking: [scale_up=0.713, enable_autoscaling=0.685, rightsize_compute=0.665]. Experience-adjusted success rates: scale_up=0.50, enable_autoscaling=0.50, rightsize_compute=0.50.

## Feedback applied

1. Mark `scale_up` as **failure** (1×).
2. Mark `rightsize_compute` as **success** (4×).

## After feedback

- Recommendation: `rightsize_compute` — RIGHTSIZE_COMPUTE - Move toward m5.large
- Success rates: `{'keep_current': 0.5, 'scale_up': 0.333, 'scale_down': 0.5, 'enable_autoscaling': 0.5, 'rightsize_compute': 0.833}`
- Reasoning: Highest weighted utility (7.331) using cost=0.40, performance=0.40, availability=0.20. Ranking: [rightsize_compute=7.331, enable_autoscaling=0.685, scale_up=-2.621]. Experience-adjusted success rates: rightsize_compute=0.83, enable_autoscaling=0.50, scale_up=0.33.
- Changed vs before: **True**

## Limitations

Early counts are priors; sparse feedback can bias preferences. Exploration may temporarily pick a suboptimal plan.

Machine-readable: [`../evidence/learning_before_after.json`](../evidence/learning_before_after.json).
