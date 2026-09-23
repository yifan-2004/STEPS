import unittest
import numpy as np
from steps import method


class ProtocolTests(unittest.TestCase):
    def test_current_suffix_is_not_read_by_local_correction(self):
        rng = np.random.default_rng(3)
        prediction = rng.normal(size=(4, 16, 2))
        target = rng.normal(size=prediction.shape)
        prior = method.empirical_prior(rng.normal(size=(24, 16, 2)), modes=8)
        gain = method.empirical_gain(prior, 8, 10.0)
        first = method.local_correction(prediction, target, 8, gain, prior['scale'])
        changed = target.copy()
        changed[:, 8:] += 1000
        second = method.local_correction(prediction, changed, 8, gain, prior['scale'])
        np.testing.assert_array_equal(first, second)
        np.testing.assert_array_equal(first[:, :8], np.zeros_like(first[:, :8]))

    def test_unmatured_records_do_not_change_global_bank(self):
        rng = np.random.default_rng(4)
        records = rng.normal(size=(14, 2, 4))
        carry = rng.normal(size=(3, 2, 4))
        bank, lengths = method.causal_multiscale(records, carry, horizon=5)
        altered = records.copy()
        altered[-4:] += 1000
        other_bank, other_lengths = method.causal_multiscale(altered, carry, horizon=5)
        np.testing.assert_array_equal(bank, other_bank)
        np.testing.assert_array_equal(lengths, other_lengths)


if __name__ == '__main__':
    unittest.main()
