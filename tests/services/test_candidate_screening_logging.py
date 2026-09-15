from app.core.logging import logger
from app.schemas.screening import CandidateScreeningRequest
from app.services.candidate_screening_service import CandidateScreeningService


class EmptyQuery:
    def order_by(self, *args):
        return self

    def all(self):
        return []


class EmptyDB:
    def query(self, model):
        return EmptyQuery()


def test_completion_log_contains_counts_not_element_values():
    messages = []
    sink_id = logger.add(messages.append, format="{message}")
    service = CandidateScreeningService(EmptyDB())
    symbols = [
        "H", "He", "Li", "Be", "B", "C", "N", "O",
        "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S",
        "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr",
        "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge",
    ]

    try:
        service.screen_candidates(
            CandidateScreeningRequest(
                scarce_elements=symbols,
                avoid_elements=symbols,
                require_stable=False,
            )
        )
    finally:
        logger.remove(sink_id)

    completion = next(
        message for message in messages
        if "candidate_screening_completed" in message
    )
    assert "outcome=success" in completion
    assert "screened_count=0" in completion
    assert "scarce_element_count=32" in completion
    assert "avoid_element_count=32" in completion
    assert "['" not in completion
    assert len(completion.encode()) < 256
