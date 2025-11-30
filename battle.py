import json
from typing import Optional, Tuple, DefaultDict
import os



with open('evaluated_moves.json', 'r') as f:
    total_results = json.load(f)
    res={k:2 for k in total_results.keys()}
    for k,v in total_results.items():
       res[k] += sum(v['evaluation']['overall_score'] for v in total_results[k])


print("Average Scores:")
for model,score in res.items():
    avg_score=score/len(total_results[model])
    print(f"Model: {model} - Average Score: {avg_score:.2f}")