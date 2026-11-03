"""Fixtures match the omarhamdy.com calculator (10,000 tonnes, default only, results rounded as the site shows them)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cbam_egypt as C


class Certificates(unittest.TestCase):
    def test_aluminium_7601(self):
        self.assertEqual(round(C.for_code("7601", 10_000, 2026)), 6_696)
        self.assertEqual(round(C.for_code("7601", 10_000, 2034)), 24_310)

    def test_urea_3102_10_19(self):
        self.assertAlmostEqual(C.for_code("3102 10 19", 10_000, 2026), 5_244.5, places=1)
        self.assertAlmostEqual(C.for_code("3102 10 19", 10_000, 2034), 14_039.0, places=1)

    def test_path_rises_as_free_allocation_falls(self):
        p = C.path(10_000, 1.87, 1.423, "Aluminium")
        years = sorted(p)
        self.assertEqual(years, list(range(2026, 2035)))
        self.assertTrue(all(p[a] <= p[b] for a, b in zip(years, years[1:])))

    def test_never_below_zero(self):
        self.assertEqual(C.certificates(10_000, 0.1, 2.0, 2026, "Aluminium"), 0.0)

    def test_markups(self):
        self.assertEqual(C.markup("Fertilisers", 2030), 0.01)
        self.assertEqual([C.markup("Cement", y) for y in (2026, 2027, 2028, 2034)], [0.1, 0.2, 0.3, 0.3])

    def test_dataset_defaults_match_benchmarked_lines(self):
        rows = C.load()
        for code in C.BENCHMARK_B:
            self.assertIn(code, rows, code)
            self.assertIsNotNone(rows[code]["default_values"]["total_tco2e_per_t"], code)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            C.certificates(-1, 1, 1, 2026, "Cement")
        with self.assertRaises(ValueError):
            C.certificates(1, 1, 1, 2035, "Cement")


if __name__ == "__main__":
    unittest.main()
