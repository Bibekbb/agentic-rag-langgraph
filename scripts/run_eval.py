from app.eval.ragas_suite import run_eval
from app.core.logging import setup_logging

setup_logging()

if __name__ == "__main__":
    results = run_eval("app/eval/datasets/sample_qa.json")
    print("\n=== RAGAS RESULTS ===")
    for k, v in results.items():
        print(f"{k}: {v}")