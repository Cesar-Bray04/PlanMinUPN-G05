"""IDW² en centro de celda con dominio, soporte y procedencia explícitos."""
from __future__ import annotations

import math
from dataclasses import dataclass
from scipy.spatial import cKDTree


@dataclass(frozen=True)
class Sample:
    id: str
    hole: str
    lith: str
    xyz: tuple[float, float, float]
    values: dict[str, float | None]
    origins: frozenset[str]


class Estimator:
    def __init__(self, samples):
        self.samples = list(samples)
        if len({s.id for s in self.samples}) != len(self.samples):
            raise ValueError("Identidades de muestra duplicadas")
        self.by_lith = {}
        for s in self.samples:
            if not s.id or not s.hole or not s.lith or not all(map(math.isfinite, s.xyz)):
                raise ValueError("Muestra sin identidad, dominio o XYZ finito")
            self.by_lith.setdefault(s.lith, []).append(s)
        self.trees = {k: cKDTree([s.xyz for s in v]) for k, v in self.by_lith.items()}

    def estimate(self, xyz, lith, analyte, *, radius_m, max_samples, min_samples, min_holes=1, power=2):
        if power != 2 or not math.isfinite(radius_m) or radius_m <= 0:
            raise ValueError("PT-01 requiere IDW² y radio positivo")
        if not 1 <= min_samples <= max_samples or not 1 <= min_holes <= max_samples:
            raise ValueError("Mínimos/máximos incompatibles")
        if not all(map(math.isfinite, xyz)):
            raise ValueError("Centro no finito")
        result = dict(value=None, reason="NO_DOMAIN_SAMPLES", n=0, holes=0,
                      independent_origins=0, sample_ids=[], distances_m=[], weights=[])
        if lith not in self.trees:
            return result
        candidates = []
        for i in self.trees[lith].query_ball_point(xyz, radius_m + 1e-9):
            sample = self.by_lith[lith][i]
            value = sample.values.get(analyte)
            distance = math.dist(xyz, sample.xyz)
            if value is not None and math.isfinite(value) and value >= 0 and distance <= radius_m + 1e-9:
                candidates.append((distance, sample.id, sample, value))
        candidates.sort(key=lambda a: (a[0], a[1]))
        exact = [c for c in candidates if c[0] <= 1e-9]
        # Una coincidencia no permite relajar los mínimos ni mezclar puntos alejados.
        selected, origins = [], set()
        for c in (exact if exact else candidates):
            if origins.intersection(c[2].origins):
                continue  # Dos derivados del mismo ensayo no son observaciones independientes.
            selected.append(c)
            origins.update(c[2].origins)
            if len(selected) == max_samples:
                break
        result.update(n=len(selected), holes=len({s[2].hole for s in selected}),
                      independent_origins=len(origins), sample_ids=[s[1] for s in selected],
                      distances_m=[s[0] for s in selected])
        if len(selected) < min_samples or result['holes'] < min_holes:
            result['reason'] = 'EXACT_INSUFFICIENT_SUPPORT' if exact else 'INSUFFICIENT_SUPPORT'
            return result
        if exact and len({s[3] for s in exact}) != 1:
            result['reason'] = 'EXACT_CONFLICTING_VALUES'
            return result
        if exact:
            weights = [1 / len(selected)] * len(selected)
        else:
            raw = [(selected[0][0] / s[0]) ** 2 for s in selected]
            weights = [w / math.fsum(raw) for w in raw]
        result.update(value=math.fsum(w * s[3] for w, s in zip(weights, selected)),
                      weights=weights, reason='ESTIMATED_EXACT' if exact else 'ESTIMATED_IDW2')
        return result
