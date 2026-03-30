try:
    from AI_GO.EXTERNAL_MEMORY.retrieval.retrieval_runtime import (
        run_external_memory_retrieval,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.retrieval.retrieval_runtime import (
        run_external_memory_retrieval,
    )

__all__ = [
    "run_external_memory_retrieval",
]