import numpy as np
import yaml
import time

def simulate_attention_scores(seq_len, head_dim=64):
    # Simulate realistic attention: high weight on sinks (start), local context (end), and random "heavy hitters"
    scores = np.random.randn(seq_len) * 0.1
    # Attention Sinks (first 4 tokens)
    scores[:4] += 5.0
    # Local Context (last 32 tokens)
    scores[-32:] += 2.0
    # Heavy Hitters (random 5% of tokens)
    hh_indices = np.random.choice(range(4, seq_len - 32), int(seq_len * 0.05), replace=False)
    scores[hh_indices] += 4.0
    # Softmax
    exp_scores = np.exp(scores - np.max(scores))
    return exp_scores / exp_scores.sum()

def run_experiment():
    seq_len = 4096
    pruning_ratios = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    results = []

    # Target token (the "needle") is one of the heavy hitters
    for ratio in pruning_ratios:
        budget = int(seq_len * (1 - ratio))
        
        # Strategies
        acc_h2o = []
        acc_streaming = []
        acc_random = []
        
        for _ in range(100):
            weights = simulate_attention_scores(seq_len)
            needle_idx = np.random.choice(np.where(weights > weights.mean() * 2)[0])
            
            # H2O: Keep sinks + top-K remaining
            indices_h2o = np.zeros(seq_len, dtype=bool)
            indices_h2o[:4] = True
            remaining_budget = budget - 4
            top_k_indices = np.argsort(weights[4:])[-remaining_budget:] + 4
            indices_h2o[top_k_indices] = True
            acc_h2o.append(1.0 if indices_h2o[needle_idx] else 0.0)
            
            # StreamingLLM: Keep sinks + sliding window
            indices_streaming = np.zeros(seq_len, dtype=bool)
            indices_streaming[:4] = True
            indices_streaming[-(budget-4):] = True
            acc_streaming.append(1.0 if indices_streaming[needle_idx] else 0.0)
            
            # Random
            indices_random = np.random.choice(range(seq_len), budget, replace=False)
            acc_random.append(1.0 if needle_idx in indices_random else 0.0)
            
        results.append({
            "ratio": ratio,
            "h2o": np.mean(acc_h2o),
            "streaming": np.mean(acc_streaming),
            "random": np.mean(acc_random)
        })
    
    print("Pruning Ratio | H2O Accuracy | StreamingLLM | Random")
    print("-" * 55)
    for r in results:
        print(f"{r['ratio']:13.1f} | {r['h2o']:12.3f} | {r['streaming']:12.3f} | {r['random']:12.3f}")

if __name__ == "__main__":
    run_experiment()
