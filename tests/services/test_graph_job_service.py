from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.models.graph_job import GraphJob, JobStatus
from app.schemas.graph_job import GraphJobCreate
from app.services.graph_job_service import GraphJobService


def create_job(service: GraphJobService, job_type: str = "SIMILARITY_SEARCH") -> GraphJob:
    return service.create_job(
        GraphJobCreate(
            job_type=job_type,
            input_json={"material_id": 1},
        )
    )


def claim_job(service: GraphJobService) -> GraphJob:
    claimed = service.claim_next_pending_job()
    assert claimed is not None
    assert claimed.status == JobStatus.RUNNING
    return claimed


def test_create_job(db_session):
    service = GraphJobService(db_session)

    job = create_job(service)

    assert job.id is not None
    assert job.job_type == "SIMILARITY_SEARCH"
    assert job.status == JobStatus.PENDING
    assert job.input_json == {"material_id": 1}


def test_claim_next_pending_job(db_session):
    service = GraphJobService(db_session)
    create_job(service)

    claimed = claim_job(service)

    assert claimed.started_at is not None


def test_complete_running_job(db_session):
    service = GraphJobService(db_session)
    job = create_job(service)
    claimed = claim_job(service)
    assert claimed.id == job.id

    completed = service.complete_job(
        job_id=job.id,
        result_json={"neighbors": [1, 2, 3]},
    )

    assert completed is not None
    assert completed.status == JobStatus.COMPLETED
    assert completed.result_json == {"neighbors": [1, 2, 3]}
    assert completed.completed_at is not None
    assert completed.updated_at == completed.completed_at


def test_fail_running_job(db_session):
    service = GraphJobService(db_session)
    job = create_job(service)
    claimed = claim_job(service)
    assert claimed.id == job.id

    failed = service.fail_job(job.id, "Computation failed")

    assert failed is not None
    assert failed.status == JobStatus.FAILED
    assert failed.error_message == "Computation failed"
    assert failed.completed_at is not None
    assert failed.updated_at == failed.completed_at


@pytest.mark.parametrize("transition", ["complete", "fail"])
def test_terminal_transition_rejects_pending_job(db_session, transition):
    service = GraphJobService(db_session)
    job = create_job(service)

    if transition == "complete":
        result = service.complete_job(job.id, {"neighbors": []})
    else:
        result = service.fail_job(job.id, "Computation failed")

    assert result is None
    db_session.refresh(job)
    assert job.status == JobStatus.PENDING
    assert job.completed_at is None


def test_completed_job_rejects_further_terminal_transitions(db_session):
    service = GraphJobService(db_session)
    job = create_job(service)
    claim_job(service)
    completed = service.complete_job(job.id, {"neighbors": []})
    assert completed is not None

    assert service.complete_job(job.id, {"replacement": True}) is None
    assert service.fail_job(job.id, "late failure") is None

    db_session.refresh(job)
    assert job.status == JobStatus.COMPLETED
    assert job.result_json == {"neighbors": []}
    assert job.error_message is None


def test_failed_job_rejects_further_terminal_transitions(db_session):
    service = GraphJobService(db_session)
    job = create_job(service)
    claim_job(service)
    failed = service.fail_job(job.id, "original failure")
    assert failed is not None

    assert service.fail_job(job.id, "replacement failure") is None
    assert service.complete_job(job.id, {"neighbors": []}) is None

    db_session.refresh(job)
    assert job.status == JobStatus.FAILED
    assert job.error_message == "original failure"
    assert job.result_json is None


@pytest.mark.parametrize("transition", ["complete", "fail"])
def test_terminal_transition_returns_none_for_unknown_job(db_session, transition):
    service = GraphJobService(db_session)

    if transition == "complete":
        result = service.complete_job(uuid4(), {"neighbors": []})
    else:
        result = service.fail_job(uuid4(), "Computation failed")

    assert result is None


def test_claim_returns_none_when_no_pending_job_exists(db_session):
    assert GraphJobService(db_session).claim_next_pending_job() is None


def test_claim_does_not_select_running_job(db_session):
    service = GraphJobService(db_session)
    first = create_job(service)
    claimed = claim_job(service)

    assert claimed.id == first.id
    assert service.claim_next_pending_job() is None


def test_claims_pending_jobs_in_creation_order(db_session):
    service = GraphJobService(db_session)
    first = create_job(service, "FIRST")
    second = create_job(service, "SECOND")

    first_claim = claim_job(service)
    second_claim = claim_job(service)

    assert first_claim.id == first.id
    assert second_claim.id == second.id


def test_claim_skips_job_locked_by_another_session():
    if engine.dialect.name != "postgresql":
        pytest.skip("SKIP LOCKED behavior requires PostgreSQL")

    marker = uuid4().hex
    setup_session = Session(bind=engine)
    locking_session = Session(bind=engine)
    claiming_session = Session(bind=engine)
    created_ids = []

    try:
        setup_service = GraphJobService(setup_session)
        first = create_job(setup_service, f"TEST_FIRST_{marker}")
        second = create_job(setup_service, f"TEST_SECOND_{marker}")
        created_ids = [first.id, second.id]

        locking_session.scalars(
            select(GraphJob).where(GraphJob.id == first.id).with_for_update()
        ).one()

        claimed = GraphJobService(claiming_session).claim_next_pending_job()

        assert claimed is not None
        assert claimed.id == second.id
        assert claimed.status == JobStatus.RUNNING
    finally:
        locking_session.rollback()
        claiming_session.rollback()
        locking_session.close()
        claiming_session.close()
        setup_session.close()

        if created_ids:
            with Session(bind=engine) as cleanup_session:
                cleanup_session.execute(
                    delete(GraphJob).where(GraphJob.id.in_(created_ids))
                )
                cleanup_session.commit()


def test_claim_returns_none_when_only_pending_job_is_locked():
    if engine.dialect.name != "postgresql":
        pytest.skip("SKIP LOCKED behavior requires PostgreSQL")

    marker = uuid4().hex
    setup_session = Session(bind=engine)
    locking_session = Session(bind=engine)
    claiming_session = Session(bind=engine)

    try:
        job = create_job(GraphJobService(setup_session), f"TEST_ONLY_{marker}")
        locked_job = locking_session.scalars(
            select(GraphJob).where(GraphJob.id == job.id).with_for_update()
        ).one()

        assert locked_job.status == JobStatus.PENDING
        assert GraphJobService(claiming_session).claim_next_pending_job() is None
    finally:
        locking_session.rollback()
        claiming_session.rollback()
        setup_session.rollback()
        locking_session.close()
        claiming_session.close()
        setup_session.close()


def test_competing_terminal_transitions_allow_exactly_one_success():
    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrent transition behavior requires PostgreSQL")

    marker = uuid4().hex
    setup_session = Session(bind=engine)
    job_id = None

    try:
        setup_service = GraphJobService(setup_session)
        job = create_job(setup_service, f"TEST_TERMINAL_{marker}")
        claimed = setup_service.claim_next_pending_job()
        assert claimed is not None
        assert claimed.id == job.id
        job_id = job.id
    finally:
        setup_session.close()

    barrier = Barrier(2)

    def complete() -> bool:
        with Session(bind=engine) as session:
            barrier.wait()
            return GraphJobService(session).complete_job(
                job_id, {"winner": "complete"}
            ) is not None

    def fail() -> bool:
        with Session(bind=engine) as session:
            barrier.wait()
            return GraphJobService(session).fail_job(
                job_id, "winner: fail"
            ) is not None

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = [executor.submit(complete), executor.submit(fail)]
            assert sum(future.result(timeout=10) for future in outcomes) == 1

        with Session(bind=engine) as verification_session:
            persisted = verification_session.get(GraphJob, job_id)
            assert persisted is not None
            assert persisted.status in {JobStatus.COMPLETED, JobStatus.FAILED}
    finally:
        if job_id is not None:
            with Session(bind=engine) as cleanup_session:
                cleanup_session.execute(delete(GraphJob).where(GraphJob.id == job_id))
                cleanup_session.commit()