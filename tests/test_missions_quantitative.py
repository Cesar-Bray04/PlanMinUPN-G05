"""Casos manuales independientes de PT-01 y límites de soporte."""
import unittest
from src.missions.estimation import Estimator, Sample
from src.missions.volume import volume_piece, area_integral


def sample(n, x, value, hole=None, lith='VOL', origin=None):
    return Sample(str(n), hole or str(n), lith, (x,0.,0.), {'cu_pct':value},
                  frozenset([origin or str(n)]))


class IDWTests(unittest.TestCase):
    def estimate(self, samples, **kwargs):
        return Estimator(samples).estimate((0.,0.,0.),'VOL','cu_pct',radius_m=75,
                 max_samples=12,min_samples=3,min_holes=2,**kwargs)

    def test_manual_grade(self):
        result=self.estimate([sample(1,1,.4,'A'),sample(2,-1,.8,'A'),sample(3,1,.6,'B')])
        self.assertAlmostEqual(result['value'],.6)
        self.assertAlmostEqual(sum(result['weights']),1)

    def test_manual_density_weights(self):
        result=Estimator([sample(1,1,2.6),sample(2,2,2.8)]).estimate(
            (0,0,0),'VOL','cu_pct',radius_m=100,max_samples=8,min_samples=2)
        self.assertAlmostEqual(result['value'],2.64)

    def test_different_holes_required(self):
        self.assertIsNone(self.estimate([sample(i,i,.5,'A') for i in range(1,5)])['value'])

    def test_boundary_and_outside(self):
        result=self.estimate([sample(1,1,.6),sample(2,2,.6),sample(3,75,.6),sample(4,75.1,90)])
        self.assertEqual(result['n'],3)
        self.assertAlmostEqual(result['value'],.6)

    def test_domain_and_missing(self):
        result=self.estimate([sample(1,1,.5),sample(2,2,None),sample(3,3,.5,lith='POR')])
        self.assertIsNone(result['value'])

    def test_zero_is_valid(self):
        self.assertEqual(self.estimate([sample(i,i,0) for i in range(1,4)])['value'],0)

    def test_coincident_minima_and_conflict(self):
        self.assertIsNone(self.estimate([sample(1,0,.6),sample(2,1,.6),sample(3,2,.6)])['value'])
        self.assertEqual(self.estimate([sample(i,0,.6) for i in range(1,4)])['value'],.6)
        result=self.estimate([sample(i,0,.4+i/10) for i in range(1,4)])
        self.assertEqual(result['reason'],'EXACT_CONFLICTING_VALUES')

    def test_derivatives_not_counted_twice(self):
        r=self.estimate([sample(1,1,.6,origin='same'),sample(2,2,.6,origin='same'),sample(3,3,.6)])
        self.assertIsNone(r['value'])
        self.assertEqual(r['n'],2)


class VolumeTests(unittest.TestCase):
    def test_full_air_and_half_slope(self):
        square=[(0,0,0),(10,0,10),(10,10,10),(0,10,0)]
        self.assertEqual(area_integral(square)[0],100)
        self.assertAlmostEqual(volume_piece(square,0,10),500)
        self.assertAlmostEqual(volume_piece(square,-10,0),1000)
        self.assertAlmostEqual(volume_piece(square,10,20),0)
        self.assertAlmostEqual(volume_piece(square,0,5)+volume_piece(square,5,10),500)


if __name__=='__main__':
    unittest.main()
