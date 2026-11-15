import csv
import tempfile
import unittest
from pathlib import Path

from src.mod1.compositing import (
    composite_assays,
    split_assays_at_lithology_contacts,
    write_positioned_composites,
)


def assay(sample_id, start, end, cu_pct, hole_id="H-01"):
    return {
        "sample_id": sample_id,
        "hole_id": hole_id,
        "from_m": str(start),
        "to_m": str(end),
        "length_m": str(end - start),
        "cu_pct": str(cu_pct),
    }


def lithology(start, end, lith_code, hole_id="H-01"):
    return {
        "hole_id": hole_id,
        "from_m": str(start),
        "to_m": str(end),
        "length_m": str(end - start),
        "lith_code": lith_code,
    }


class M01BCompositingTests(unittest.TestCase):
    def test_two_one_m_assays_form_one_two_m_composite(self):
        composites = composite_assays(
            [
                {
                    **assay("A-01", 0, 1, 0.1),
                    "lith_code": "POR",
                    "source_sample_id": "A-01",
                },
                {
                    **assay("A-02", 1, 2, 0.3),
                    "lith_code": "POR",
                    "source_sample_id": "A-02",
                },
            ]
        )

        self.assertEqual(len(composites), 1)
        self.assertEqual(composites[0]["from_m"], 0)
        self.assertEqual(composites[0]["to_m"], 2)
        self.assertEqual(composites[0]["length_m"], 2)
        self.assertAlmostEqual(composites[0]["cu_pct"], 0.2)
        self.assertFalse(composites[0]["residual_flag"])

    def test_cu_is_weighted_by_segment_length(self):
        composites = composite_assays(
            [
                {
                    **assay("A-01", 0, 0.5, 0.1),
                    "lith_code": "VOL",
                    "source_sample_id": "A-01",
                },
                {
                    **assay("A-02", 0.5, 2, 0.5),
                    "lith_code": "VOL",
                    "source_sample_id": "A-02",
                },
            ]
        )

        self.assertAlmostEqual(composites[0]["cu_pct"], 0.4)

    def test_two_m_assay_is_retained_as_full_composite(self):
        composites = composite_assays(
            [
                {
                    **assay("A-01", 0, 2, 0.25),
                    "lith_code": "POR",
                    "source_sample_id": "A-01",
                }
            ]
        )

        self.assertEqual(len(composites), 1)
        self.assertEqual(composites[0]["length_m"], 2)
        self.assertEqual(composites[0]["cu_pct"], 0.25)
        self.assertFalse(composites[0]["residual_flag"])

    def test_terminal_residual_is_preserved_and_flagged(self):
        composites = composite_assays(
            [
                {
                    **assay("A-01", 0, 2, 0.25),
                    "lith_code": "POR",
                    "source_sample_id": "A-01",
                },
                {
                    **assay("A-02", 2, 2.5, 0.4),
                    "lith_code": "POR",
                    "source_sample_id": "A-02",
                },
            ]
        )

        self.assertEqual(len(composites), 2)
        self.assertEqual(composites[1]["length_m"], 0.5)
        self.assertTrue(composites[1]["residual_flag"])

    def test_assay_is_split_exactly_at_lithology_contact(self):
        split = split_assays_at_lithology_contacts(
            [assay("A-01", 0, 2, 0.4)],
            [lithology(0, 1.25, "OVB"), lithology(1.25, 3, "POR")],
        )

        self.assertEqual(len(split), 2)
        self.assertEqual(
            [(row["from_m"], row["to_m"], row["lith_code"]) for row in split],
            [("0", "1.25", "OVB"), ("1.25", "2", "POR")],
        )
        self.assertAlmostEqual(sum(float(row["length_m"]) for row in split), 2)

    def test_composites_never_cross_lithology_contacts(self):
        split = split_assays_at_lithology_contacts(
            [assay("A-01", 0, 2, 0.4)],
            [lithology(0, 1, "OVB"), lithology(1, 2, "POR")],
        )

        composites = composite_assays(split)

        self.assertEqual(len(composites), 2)
        self.assertEqual([row["lith_code"] for row in composites], ["OVB", "POR"])
        self.assertEqual([row["length_m"] for row in composites], [1, 1])
        self.assertTrue(all(row["residual_flag"] for row in composites))
        self.assertEqual(composites[0]["to_m"], composites[1]["from_m"])

    def test_meters_are_conserved_across_splitting_and_compositing(self):
        source_assays = [
            assay("A-01", 0, 1.5, 0.1),
            assay("A-02", 1.5, 4.25, 0.3),
        ]
        split = split_assays_at_lithology_contacts(
            source_assays,
            [lithology(0, 2.25, "POR"), lithology(2.25, 5, "VOL")],
        )
        composites = composite_assays(split)

        original_meters = sum(float(row["length_m"]) for row in source_assays)
        split_meters = sum(float(row["length_m"]) for row in split)
        composite_meters = sum(row["length_m"] for row in composites)
        self.assertAlmostEqual(original_meters, split_meters, places=8)
        self.assertAlmostEqual(original_meters, composite_meters, places=8)

    def test_invalid_intervals_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "from_m must be less than to_m"):
            split_assays_at_lithology_contacts(
                [assay("A-01", 2, 1, 0.1)], [lithology(0, 3, "POR")]
            )

    def test_positioning_fields_are_written_to_output(self):
        composites = composite_assays(
            [
                {
                    **assay("A-01", 0, 2, 0.25),
                    "lith_code": "POR",
                    "source_sample_id": "A-01",
                }
            ]
        )
        trajectory = {
            "H-01": [
                {"hole_id": "H-01", "md_m": 0.0, "x": 10.0, "y": 20.0, "z": 30.0},
                {"hole_id": "H-01", "md_m": 2.0, "x": 12.0, "y": 24.0, "z": 28.0},
            ]
        }

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "composites.csv"
            write_positioned_composites(composites, trajectory, output)
            with output.open(encoding="utf-8-sig", newline="") as csv_file:
                rows = list(csv.DictReader(csv_file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["hole_id"], "H-01")
        self.assertEqual(rows[0]["lith_code"], "POR")
        self.assertEqual(rows[0]["residual_flag"], "false")
        self.assertAlmostEqual(float(rows[0]["mid_m"]), 1)
        self.assertAlmostEqual(float(rows[0]["x_mid"]), 11)
        self.assertAlmostEqual(float(rows[0]["y_mid"]), 22)
        self.assertAlmostEqual(float(rows[0]["z_mid"]), 29)


if __name__ == "__main__":
    unittest.main()
