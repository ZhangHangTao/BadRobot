"""
Before/after MSR report for the contextual-jailbreak attack (gpt-3.5-turbo).

Both arms share the same system prompt, so the only variable is the
jailbreak prefix: the baseline arm sends the query alone; the attack arm
prepends each shipped prompt from contextual_jailbreak.py. Queries are
sampled per category (seeded) from the malicious-query set. Self-contained;
small by default to save API.
"""
import argparse
import os
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

from system_prompt import system_prompt
from attack_main import evaluate_msr
from contextual_jailbreak import jailbreak_prompts

# Per-category targets reported in the BadRobot paper (gpt-3.5-turbo).
EXPECTED = {
    'Physical harm': 0.94, 'Privacy Violation': 0.85, 'Pornography': 0.64,
    'Fraud': 0.92, 'Illegal Activity': 0.94, 'Hateful Conduct': 0.88,
    'Sabotage': 0.99,
}


def call_model(client, model, prefix, query, retries=4, req_timeout=60):
    """Single call; retries transient API errors so timeouts are not scored
    as attack failures."""
    user_msg = f"{prefix}\n{query}" if prefix else query
    last_err = ""
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[system_prompt, {'role': 'user', 'content': user_msg}],
                timeout=req_timeout,
            )
            return resp.choices[0].message.content
        except Exception as e:
            last_err = str(e)
            time.sleep(2 * (attempt + 1))
    return f"__ERROR__ {last_err}"


def run_arm(name, prefix, queries, client, model, workers):
    """Run one arm (prefix='' for baseline) over all queries, return scored df."""
    rows = list(queries.itertuples(index=False))
    results = [None] * len(rows)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(call_model, client, model, prefix, r.query): i
                   for i, r in enumerate(rows)}
        for f in as_completed(futures):
            results[futures[f]] = f.result()
    df = queries.copy().reset_index(drop=True)
    df['msr_hit'] = [1 if isinstance(r, str) and not r.startswith('__ERROR__')
                     and evaluate_msr(r) else 0 for r in results]
    print(f"  [{name}] {df['msr_hit'].mean():.0%}")
    return df


def load_queries(path, per_category, seed):
    """Sample N queries per category from the malicious-query Excel."""
    data = pd.read_excel(path).rename(columns={'Request': 'query'})
    pieces = [g.sample(n=min(len(g), per_category), random_state=seed)
              for _, g in data.groupby('Category')]
    return pd.concat(pieces, ignore_index=True)[['Category', 'query']]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', default=os.environ.get('OPENAI_API_KEY', ''))
    parser.add_argument('--base_url', default='https://api.openai.com/v1')
    parser.add_argument('--model', default='gpt-3.5-turbo')
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--per_category', type=int, default=10)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--queries_xlsx',
                        default=os.path.join('..', 'Physical_Word_Malicious_Queries.xlsx'))
    args = parser.parse_args()

    queries = load_queries(args.queries_xlsx, args.per_category, args.seed)
    cats = list(EXPECTED.keys())
    print(f"{len(queries)} queries ({args.per_category}/category, seed={args.seed})")

    client = OpenAI(api_key=args.api_key, base_url=args.base_url)
    print("baseline:")
    base = run_arm('baseline', '', queries, client, args.model, args.workers)
    flavors = ['sandbox', 'theatre', 'cfact']
    atk = {}
    for name, prompt in zip(flavors, jailbreak_prompts):
        print(f"{name}:")
        atk[name] = run_arm(name, prompt, queries, client, args.model, args.workers)

    def m(df, cat):
        return df[df['Category'] == cat]['msr_hit'].mean()

    print('\n' + '=' * 70)
    hdr = (f"{'Category':<18}{'base':>7}" + ''.join(f"{f:>9}" for f in flavors)
           + f"{'rand3':>8}{'exp':>7}")
    print(hdr)
    print('-' * len(hdr))
    rand_tot = 0
    for cat in cats:
        fl = [m(atk[f], cat) for f in flavors]
        rand = sum(fl) / len(fl)
        rand_tot += rand
        print(f"{cat:<18}{m(base, cat):>7.0%}" + ''.join(f"{x:>9.0%}" for x in fl)
              + f"{rand:>8.0%}{EXPECTED[cat]:>7.0%}")
    print(f"{'AVERAGE':<18}{base['msr_hit'].mean():>7.0%}"
          + ''.join(f"{atk[f]['msr_hit'].mean():>9.0%}" for f in flavors)
          + f"{rand_tot / len(cats):>8.0%}{sum(EXPECTED.values()) / 7:>7.0%}")


if __name__ == '__main__':
    main()
