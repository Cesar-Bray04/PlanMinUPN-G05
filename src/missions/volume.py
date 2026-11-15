"""Volumen bajo TIN lineal, integrado por triángulos recortados a cada celda.

La integración es exacta para la superficie lineal adoptada, no acredita su CRS
ni convierte la litología preliminar en un sólido validado.
"""
from __future__ import annotations

import math
import numpy as np
from src.mod1.topography import read_topography_points, triangulate_topography


def clip(poly, axis, bound, above=True):
    """Recorta un polígono plano XYZ por un semiespacio cerrado."""
    if not poly:
        return []
    out = []
    previous = poly[-1]
    pv = (previous[axis] - bound) * (1 if above else -1)
    for current in poly:
        cv = (current[axis] - bound) * (1 if above else -1)
        if (cv >= 0) != (pv >= 0):
            fraction = pv / (pv - cv)
            out.append(tuple(a + fraction * (b - a) for a, b in zip(previous, current)))
        if cv >= 0:
            out.append(current)
        previous, pv = current, cv
    return out


def area_integral(poly):
    """Área XY e integral de Z mediante abanico triangular (coordenadas locales)."""
    if len(poly) < 3:
        return 0., 0.
    a = poly[0]
    areas, integrals = [], []
    for b, c in zip(poly[1:-1], poly[2:]):
        area = abs((b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1])) / 2
        areas.append(area)
        integrals.append(area * (a[2]+b[2]+c[2]) / 3)
    return math.fsum(areas), math.fsum(integrals)


def volume_piece(poly, low, high):
    """Integra clamp(Z-low, 0, high-low) sobre la huella del polígono."""
    def positive(level):
        clipped = clip(poly, 2, level)
        area, integral = area_integral(clipped)
        return integral - level * area
    return max(0., positive(low) - positive(high))


def tin_volumes(blocks, topography_path):
    points = read_topography_points(topography_path)
    # Restar origen evita cancelación numérica en coordenadas del orden de millones.
    origin = points[:, :2].min(axis=0)
    points[:, :2] -= origin
    # Qhull también debe recibir XY trasladadas. Trasladar solo al integrar
    # deja la triangulación expuesta al mal condicionamiento de coordenadas grandes.
    surface = triangulate_topography(points)
    points = surface.points
    triangles = points[surface.simplices]
    mins, maxs = triangles[:, :, :2].min(axis=1), triangles[:, :, :2].max(axis=1)
    columns = {}
    for n, b in enumerate(blocks):
        columns.setdefault((b['i'], b['j']), []).append((n, b))
    results = [None] * len(blocks)
    max_area_error = 0.
    max_center_delta = 0.
    center_class_changes = 0
    for column in columns.values():
        column.sort(key=lambda p: p[1]['z_min'])
        b = column[0][1]
        center_elevation=float(surface.interpolate(np.array([[b['x_center']-origin[0],b['y_center']-origin[1]]]))[0])
        x0, x1 = b['x_min']-origin[0], b['x_max']-origin[0]
        y0, y1 = b['y_min']-origin[1], b['y_max']-origin[1]
        indices = np.flatnonzero((maxs[:, 0] > x0) & (mins[:, 0] < x1) &
                                 (maxs[:, 1] > y0) & (mins[:, 1] < y1))
        lows = np.array([v['z_min'] for _, v in column])
        highs = np.array([v['z_max'] for _, v in column])
        volumes = np.zeros(len(column))
        areas = []
        for t in indices:
            poly = [tuple(p) for p in triangles[t]]
            for axis, bound, above in [(0,x0,True),(0,x1,False),(1,y0,True),(1,y1,False)]:
                poly = clip(poly, axis, bound, above)
            area, _ = area_integral(poly)
            if area < 1e-12:
                continue
            areas.append(area)
            low_z, high_z = min(p[2] for p in poly), max(p[2] for p in poly)
            full = highs <= low_z
            volumes[full] += area * (highs[full] - lows[full])
            boundary = np.flatnonzero((highs > low_z) & (lows < high_z))
            for k in boundary:
                volumes[k] += volume_piece(poly, float(lows[k]), float(highs[k]))
        expected_area = (x1-x0)*(y1-y0)
        error = abs(math.fsum(areas)-expected_area)
        max_area_error = max(max_area_error, error)
        covered = error <= max(1e-6, expected_area*1e-8)
        for (n, b), vol in zip(column, volumes):
            full_volume = expected_area * (b['z_max']-b['z_min'])
            if covered and not -1e-5 <= vol <= full_volume+1e-5:
                raise ValueError('Volumen fuera de límites geométricos')
            value = min(full_volume, max(0., float(vol))) if covered else None
            if value is not None and value < 1e-5:
                value = 0.
            if value is not None and full_volume-value < 1e-5:
                value = full_volume
            center_status='ROCK' if center_elevation>=b['z_max'] else 'AIR' if center_elevation<=b['z_min'] else 'PARTIAL'
            max_center_delta=max(max_center_delta,abs(center_elevation-float(b['topo_z_m'])))
            center_class_changes+=center_status!=b['topo_status']
            results[n] = dict(cell_volume_m3=full_volume, rock_volume_m3=value,
                              rock_fraction=value/full_volume if value is not None else None,
                              tin_z_center_m=center_elevation,tin_center_topo_status=center_status,
                              footprint_area_covered_m2=math.fsum(areas),
                              volume_status='NO_TIN_COVERAGE' if not covered else
                              'AIR_TIN' if value == 0 else 'FULL_ROCK_TIN' if value == full_volume
                              else 'PARTIAL_ROCK_TIN')
    return results, dict(method='EXACT_CLIPPED_LINEAR_TIN_LOCAL_XY', columns=len(columns),
                          max_footprint_area_error_m2=max_area_error,
                          triangulation_points=len(points),triangulation_triangles=len(surface.simplices),
                          xy_translation_m=origin.tolist(),inherited_center_max_delta_m=max_center_delta,
                          inherited_center_classification_changes=center_class_changes,
                          topography_crs='NOT_DOCUMENTED', vertical_datum='NOT_DOCUMENTED',
                          coordinate_compatibility='ACADEMIC_INHERITED_LOCAL_COORDINATES_ASSUMPTION')
