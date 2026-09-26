import unittest
from simulation import Request, allocate, generate_batches, metrics


class MechanismTests(unittest.TestCase):
    def test_no_eligible_returns_reserve(self):
        requests = [Request(i, i*10, 0, 1, i) for i in range(1, 7)]
        self.assertEqual(allocate(requests, 'pure'), allocate(requests, 'hybrid'))

    def test_known_displacement_payments_and_welfare(self):
        requests = [Request(1, 100, .1, 1, 4), Request(2, 90, .2, 1, 3),
                    Request(3, 80, .3, 1, 2), Request(4, 70, .4, 1, 1),
                    Request(5, 10, .9, 1, 0)]
        pure, hybrid = allocate(requests, 'pure'), allocate(requests, 'hybrid')
        self.assertEqual(pure, {1:80, 2:72, 3:64, 4:56})
        self.assertEqual(hybrid, {5:0, 1:80, 2:72, 3:64})
        p, h = metrics(requests, pure), metrics(requests, hybrid)
        self.assertEqual(h['W']-p['W'], -10)
        self.assertEqual(h['utility'], 64)

    def test_already_winner_no_allocation_change(self):
        requests = [Request(i, 100-i*10, 1 if i == 1 else 0, 1, i) for i in range(1, 7)]
        pure, hybrid = allocate(requests, 'pure'), allocate(requests, 'hybrid')
        self.assertEqual(set(pure), set(hybrid))
        self.assertEqual(hybrid[1], 0)
        self.assertLess(sum(hybrid.values()), sum(pure.values()))

    def test_ties_boundary_and_fcfs(self):
        requests = [Request(i, 50, .6, 1, 7-i) for i in range(1, 7)]
        self.assertEqual(allocate(requests, 'hybrid'), {1:0, 2:40, 3:40, 4:40})
        self.assertEqual(set(allocate(requests, 'fcfs')), {3, 4, 5, 6})

    def test_budget_cap_and_invalid_duplicate(self):
        r = Request(1, 100, 1, 1, 0, budget=20)
        self.assertEqual(allocate([r], 'pure'), {1:20})
        with self.assertRaises(ValueError):
            allocate([r,r], 'pure')

    def test_paired_invariants(self):
        for requests in generate_batches(count=100):
            for mechanism in ('pure', 'hybrid', 'fcfs'):
                a = allocate(requests, mechanism)
                m = metrics(requests, a)
                self.assertEqual(len(a), 4)
                self.assertAlmostEqual(m['utility']+m['payment'], m['V'])
                self.assertTrue(0 <= m['efficiency'] <= 1+1e-12)
                for r in requests:
                    self.assertTrue(0 <= a.get(r.pm, 0) <= r.budget)
            self.assertAlmostEqual(metrics(requests, allocate(requests, 'pure'))['efficiency'], 1)


if __name__ == '__main__':
    unittest.main()
