"""
RAG Evaluation Router for RecoverAI.
Runs the dynamic evaluation benchmark over policy documents and returns calculated metrics.
"""
from fastapi import APIRouter
from typing import Dict, Any
from services.rag import evaluate_rag_system

router = APIRouter(tags=["Evaluation"])

@router.get("/rag/evaluation")
def get_rag_evaluation() -> Dict[str, Any]:
    """
    Executes the 15-query RAG evaluation suite against indexed policies.
    Returns:
    - retrieval_accuracy
    - context_relevance
    - answer_grounding
    - faithfulness
    - overall_score
    - total_queries
    - results list
    """
    evaluation_data = evaluate_rag_system()
    return evaluation_data
