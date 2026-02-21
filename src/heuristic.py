import numpy as np

def heuristic_policy(env):
    actions = []
    for _ in range(env.num_slots):
        action = np.array([1.0 / env.num_slots])  # Equal allocation
        state, reward, done, _ = env.step(action)
        actions.append(action)
        if done:
            break
    return actions