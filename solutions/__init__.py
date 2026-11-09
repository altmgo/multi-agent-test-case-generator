"""Reference generation strategies."""

from asyncio import CancelledError

from schemas import GenerationResult


class GenerationCancelled(CancelledError):
    """A cancelled generation with validated partial output for persistence."""

    def __init__(self, cancellation: CancelledError, stage: str, partial_result: GenerationResult):
        super().__init__(*cancellation.args)
        self.stage = stage
        self.error_type = type(cancellation).__name__
        self.partial_result = partial_result
