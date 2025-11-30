import json
import time
from typing import Optional, Tuple,DefaultDict
import os
with open('total_comparison_results2.json', 'r') as f:
    total_results = json.load(f)
    res={}
    for k,v in total_results.items():
        for k2,v2 in v.items():
            if k2 in res:
                res[k2]+=v2['avg_balance_score']
            else:
                res[k2]=v2['avg_balance_score']

    for k,v in res.items():
        res[k]=v/30.0


EVAL_SYSTEM_PROMPT = """
You are an expert Pokémon game designer and competitive balance analyst.

You will evaluate a custom Pokémon move with the EXACT schema:
{{
  "name": "string",
  "power": number,
  "accuracy": number,
  "type": "string",
  "category": "Physical" | "Special" | "Status",
  "PP": number,
  "effect": ["effect_name", chance] | null
}}

You must score the move in 2 areas:

1. Creativity (0–10)
   - How imaginative, thematic, and interesting the move concept is.
   - Does it feel like a real Pokémon move but still creative?

2. Originality (0–10)
   - How distinct it is from existing official Pokémon moves.
   - Judge similarity in: name, mechanic, theme, effect.

Overall Score = average of (creativity + originality).

Score interpretation:
0-2 = Very poor / broken / unusable
3-4 = Weak / unoriginal / unbalanced
5 = Average, nothing special
6-7 = Good but not excellent
8-9 = Very strong / creative / well-balanced
10 = Exceptional, near-perfect Pokémon move design
 
Do NOT cluster scores around the middle. 
A score of 5 is not “safe” — it means the move is only average.

Evaluation categories:
1. Creativity (0–10)
2. Originality (0–10)
3. Overall Score (0–10)

 Examples:
- Tackle → Creativity 1, Originality 1
- Flamethrower → Creativity 4, Originality 4,
- A highly inventive fan-made move → Creativity 8–9, Originality 8–9
Verdict:
- "approve" (good)
- "revise" (needs small fixes)
- "reject" (broken or unbalanced)

Return STRICT JSON ONLY:
{{
  "creativity": <0-10>,
  "originality": <0-10>,
  "overall_score": <0-10>,
  "verdict": "approve" | "revise" | "reject",
}}
"""
EVAL_USER_TEMPLATE = """
Evaluate the following custom Pokémon move:

{move_json}

Return JSON only.
"""
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
import json

def evaluate_move_claude_haiku(move: dict):
    eval_llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        temperature=0.0,
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", EVAL_SYSTEM_PROMPT),
        ("user", EVAL_USER_TEMPLATE)
    ])

    chain = prompt | eval_llm

    response = chain.invoke({
        "move_json": json.dumps(move)
    })
    return json.loads(response.content.replace('`','').replace('json',''))
if __name__ == '__main__':
    move_dict=json.load(open('aggregated_generated_moves.json','r'))
    evals=DefaultDict(list)
    for model,moves in move_dict.items():
            print(f"Evaluating move from model: {model}")
            for move_data in moves:
                evaluation = evaluate_move_claude_haiku(move_data)
                print(f"Move: {move_data['name']} - Evaluation: {evaluation['overall_score']} - Verdict: {evaluation['verdict']}")
                evals[model].append({
                    "move": move_data,
                    "evaluation": evaluation
                })
                time.sleep(1.5)  # To avoid hitting rate limits

        

    with open('evaluated_moves.json','w') as f:
        json.dump(evals,f,indent=3)