"""
Motor de procesamiento batch para Dexter.

Componentes:
- storage: Persistencia SQLite (batches, items, audit_log)
- engine: State machine (PENDING → VALIDATED → DRY_RUN → CONFIRMED → EXECUTED)
- disambiguator: Preguntas interactivas al usuario
- deposits: Skill de bank deposits multi-cliente
- recon_tagger: Skill de reconciliation que tagea transactions existentes (BNK-RECON-*)
"""
from dexter.core.batch.storage import BatchStorage, BatchState, ItemState
from dexter.core.batch.engine import BatchEngine, InvalidStateTransition
from dexter.core.batch.disambiguator import Disambiguator
from dexter.core.batch.deposits import DepositBatchSkill, QBOClientProtocol
from dexter.core.batch.recon_tagger import (
    ReconciliationTaggerSkill,
    Match,
    TAG_FIELD_BY_TYPE,
)

__all__ = [
    "BatchStorage",
    "BatchState",
    "ItemState",
    "BatchEngine",
    "InvalidStateTransition",
    "Disambiguator",
    "DepositBatchSkill",
    "QBOClientProtocol",
    "ReconciliationTaggerSkill",
    "Match",
    "TAG_FIELD_BY_TYPE",
]
