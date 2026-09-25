from fastapi import APIRouter, HTTPException
from app.eval.rags_suite import run_eval

router = APIRouter(prefix="/eval", tags=["eval"])

@router.post("/run")
def eval_run(dataset_path: str = "app/eval/datasets/sample_qa.json"):
    try:
        return run_eval(dataset_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))