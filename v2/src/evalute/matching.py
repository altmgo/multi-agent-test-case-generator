"""One-to-one assignment of eligible similarities."""

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

SIMILARITY_THRESHOLD = 0.70


def _minimum_assignment(costs: list[list[int | None]]) -> list[tuple[int, int]]:
    """Assign every row by shortest augmenting paths with integer costs.

    Row and column potentials track reduced costs. The minimum slack for each
    unused column records how cheaply the current alternating path can reach
    it. Column order and preference for a free column break exact ties.
    """
    column_count = len(costs[0])
    row_potential = [0] * (len(costs) + 1)
    column_potential = [0] * (column_count + 1)
    column_owner = [0] * (column_count + 1)
    for row in range(1, len(costs) + 1):
        # Column zero is the search root and represents the new unassigned row.
        column_owner[0] = row
        column = 0
        used = [False] * (column_count + 1)
        slack: list[int | None] = [None] * (column_count + 1)
        predecessor = [0] * (column_count + 1)

        while True:
            used[column] = True
            owner = column_owner[column]
            best: tuple[int, bool, int] | None = None
            for candidate, cost in enumerate(costs[owner - 1], start=1):
                if used[candidate]:
                    continue
                if cost is not None:
                    reduced_cost = cost - row_potential[owner] - column_potential[candidate]
                    if slack[candidate] is None or reduced_cost < slack[candidate]:
                        slack[candidate] = reduced_cost
                        predecessor[candidate] = column
                distance = slack[candidate]
                if distance is not None:
                    option = (distance, bool(column_owner[candidate]), candidate)
                    if best is None or option < best:
                        best = option

            if best is None:
                raise ValueError("No feasible assignment")
            distance, occupied, next_column = best
            for visited in range(column_count + 1):
                if used[visited]:
                    row_potential[column_owner[visited]] += distance
                    column_potential[visited] -= distance
                elif slack[visited] is not None:
                    slack[visited] -= distance
            column = next_column
            if not occupied:
                break

        while column:
            previous = predecessor[column]
            column_owner[column] = column_owner[previous]
            column = previous

    return [(owner - 1, column - 1) for column, owner in enumerate(column_owner[1:], 1) if owner]


def match(
    similarities: NDArray[np.float64], threshold: float = SIMILARITY_THRESHOLD
) -> list[tuple[int, int, float]]:
    """Maximize pair count, then total similarity, in stable input order."""
    scores = np.asarray(similarities, dtype=np.float64)
    if scores.ndim != 2 or not np.isfinite(scores).all() or not np.isfinite(threshold):
        raise ValueError("Matching requires a finite similarity matrix and threshold")

    transposed = scores.shape[0] > scores.shape[1]
    assignment_scores = scores.T if transposed else scores
    eligible = assignment_scores >= threshold
    cardinality = np.count_nonzero(maximum_bipartite_matching(csr_matrix(eligible)) >= 0)
    if not cardinality:
        return []

    row_count, column_count = assignment_scores.shape
    # Float scores are exact binary fractions. A common power-of-two
    # denominator lets assignment compare their sums without rounding.
    fractions = {
        (row, column): float(assignment_scores[row, column]).as_integer_ratio()
        for row, column in zip(*np.nonzero(eligible), strict=True)
    }
    scale = max(denominator for _, denominator in fractions.values())
    # All rows must be assigned. With exactly enough dummy columns for the
    # unmatched rows, every feasible assignment uses cardinality real edges.
    costs: list[list[int | None]] = [
        [None] * column_count + [0] * (row_count - cardinality) for _ in range(row_count)
    ]
    for (row, column), (numerator, denominator) in fractions.items():
        costs[row][column] = -numerator * (scale // denominator)

    pairs = [
        (column, row) if transposed else (row, column)
        for row, column in _minimum_assignment(costs)
        if column < column_count
    ]
    return [(row, column, float(scores[row, column])) for row, column in sorted(pairs)]
