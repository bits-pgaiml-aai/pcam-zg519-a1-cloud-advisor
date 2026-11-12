# Learning agent evaluation

## Mechanism

1. **Performance element:** utility-based plan selection.
2. **Critic:** labels an action outcome as success/failure (UI or API feedback).
3. **Learning element:** updates `data/learning_history.json` success/failure counts.
4. **Problem generator:** with small probability explores a non-top feasible action.

Expected utility is adjusted by:

```text
utility' = utility + 20 * (success_rate(action) - 0.5)
```

## How to demonstrate

1. Run scenario A/B/C in Streamlit.
2. Note Learning recommendation and displayed success rates.
3. Record a few outcomes (success/failure) for competing actions.
4. Re-run the same scenario and show that ranking / choice can shift.
5. Acknowledge limitations shown in the UI warning.

## Limitations

- Priors start at 1/1 (50%); early episodes dominate.
- Sparse or biased feedback can lock in a suboptimal action.
- Exploration can temporarily choose a worse plan on purpose.
- Simulated outcomes only — not live cloud verification.
