# utils/reward_functions.py
def budget_constrained_reward(clicks, spend, daily_budget):
    """
    Reward function with budget constraint.
    - clicks: number of clicks (0 or 1 in our env)
    - spend: money spent this step
    - daily_budget: original budget
    """
    base_reward = clicks * 10.0  # reward per click (tune as needed)
    if spend > daily_budget:
        penalty = (spend - daily_budget) * 0.5
        total_reward = base_reward - penalty
    else:
        total_reward = base_reward - (spend * 0.01)  # small cost penalty per spend
    return total_reward
