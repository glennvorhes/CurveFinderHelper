from unittest import TestCase
from scripts.classes.CalibScore import CalibScore


class TestCalibScore(TestCase):

    def test_gt_outside(self):
        gt_outside = CalibScore()

        gt_outside.add_id('1', 0.25, 0.75)
        gt_outside.add_gt('1', 0, 1)

        self.assertEquals(gt_outside.total_gt_len, 1)
        self.assertEquals(gt_outside.missed_pcnt, 0.5)
        self.assertEquals(gt_outside.matched_pcnt, 0.5)
        self.assertEquals(gt_outside.over_pcnt, 0)

    def test_id_outside(self):
        id_outside = CalibScore()

        id_outside.add_id('1', 0, 4)
        id_outside.add_gt('1', 1, 3)
        self.assertEquals(id_outside.missed_pcnt, 0)

        self.assertEquals(id_outside.matched_pcnt, 1)
        self.assertEquals(id_outside.over_pcnt, 1)

    def test_start_id_over_pcntlap(self):
        id_start_over_pcntlap = CalibScore()

        id_start_over_pcntlap.add_id('1', 0, 2)
        id_start_over_pcntlap.add_gt('1', 1, 3)

        self.assertEquals(id_start_over_pcntlap.missed_pcnt, 0.5)
        self.assertEquals(id_start_over_pcntlap.matched_pcnt, 0.5)
        self.assertEquals(id_start_over_pcntlap.over_pcnt, 0.5)

    def test_end_id_over_pcntlap(self):
        id_end_over_pcntlap = CalibScore()

        id_end_over_pcntlap.add_id('1', 1, 3)
        id_end_over_pcntlap.add_gt('1', 0, 2)

        self.assertEquals(id_end_over_pcntlap.missed_pcnt, 0.5)
        self.assertEquals(id_end_over_pcntlap.matched_pcnt, 0.5)
        self.assertEquals(id_end_over_pcntlap.over_pcnt, 0.5)

    def test_two_id_internal(self):
        two_internal = CalibScore()

        two_internal.add_id('1', 1, 2)
        two_internal.add_id('1', 5, 6)
        two_internal.add_gt('1', 0, 10)

        self.assertEquals(two_internal.missed_pcnt, 0.8)
        self.assertEquals(two_internal.matched_pcnt, 0.2)
        self.assertEquals(two_internal.over_pcnt, 0)

    def test_two_id_internal_good_match(self):
        two_internal = CalibScore()

        two_internal.add_id('1', 1, 5)
        two_internal.add_id('1', 6, 11)
        two_internal.add_gt('1', 0, 10)

        self.assertEquals(two_internal.missed_pcnt, 0.2)
        self.assertEquals(two_internal.matched_pcnt, 0.8)
        self.assertEquals(two_internal.over_pcnt, 0.1)
        self.assertEquals(two_internal.id_count, 2)
        self.assertEquals(two_internal.id_match_count, 2)

    def test_two_id_internal_routes(self):
        two_internal = CalibScore()

        two_internal.add_id('1', 1, 2)
        two_internal.add_id('1', 5, 6)
        two_internal.add_gt('1', 0, 10)

        two_internal.add_id('2', 1, 2)
        two_internal.add_id('2', 5, 6)
        two_internal.add_gt('2', 0, 10)

        self.assertEquals(two_internal.missed_pcnt, 0.8)
        self.assertEquals(two_internal.matched_pcnt, 0.2)
        self.assertEquals(two_internal.over_pcnt, 0)

    def test_three_id_internal_routes(self):
        three_internal = CalibScore()

        three_internal.add_id('1', 1, 2)
        three_internal.add_id('1', 5, 6)
        three_internal.add_gt('1', 0, 10)

        three_internal.add_id('2', 1, 2)
        three_internal.add_id('2', 5, 6)
        three_internal.add_gt('2', 0, 10)

        three_internal.add_id('3', 1, 2)
        three_internal.add_id('3', 5, 6)
        three_internal.add_gt('3', 0, 10)

        self.assertEquals(three_internal.missed_pcnt, 0.8)
        self.assertEquals(three_internal.matched_pcnt, 0.2)
        self.assertEquals(three_internal.over_pcnt, 0)


    def test_none(self):
        three_internal = CalibScore()

        self.assertEquals(three_internal.missed_pcnt, 0)
        self.assertEquals(three_internal.matched_pcnt, 0)
        self.assertEquals(three_internal.over_pcnt, 0)


    def test_one_over_pcnt(self):
        three_internal = CalibScore()
        three_internal.add_gt('3', 4, 5)
        three_internal.add_id('3', 0, 1)

        self.assertEquals(three_internal.missed_pcnt, 1)
        self.assertEquals(three_internal.matched_pcnt, 0)
        self.assertEquals(three_internal.over_pcnt, 1)

    def test_reset(self):
        two_internal = CalibScore()

        two_internal.add_id('1', 1, 5)
        two_internal.add_id('1', 6, 11)
        two_internal.add_gt('1', 0, 10)

        two_internal.reset()

        two_internal.add_id('1', 1, 5)
        two_internal.add_id('1', 6, 11)

        self.assertEquals(two_internal.missed_pcnt, 0.2)
        self.assertEquals(two_internal.matched_pcnt, 0.8)
        self.assertEquals(two_internal.over_pcnt, 0.1)
        self.assertEquals(two_internal.gt_count, 1)
        self.assertEquals(two_internal.gt_found_count, 1)

    def test_gt_missed_pcnt(self):
        two_internal = CalibScore()

        two_internal.add_gt('1', 0, 2)
        two_internal.add_gt('1', 4, 6)

        two_internal.add_id('1', 0, 1)

        self.assertEquals(two_internal.missed_pcnt, 0.75)
        self.assertEquals(two_internal.matched_pcnt, 0.25)
        self.assertEquals(two_internal.over_pcnt, 0.0)
        self.assertEquals(two_internal.gt_count, 2)
        self.assertEquals(two_internal.gt_found_count, 1)

        two_internal.reset()

        two_internal.add_id('1', 0, 1)
        two_internal.add_id('1', 4, 5)

        # self.assertEquals(two_internal.missed_pcnt, 0.5)
        # self.assertEquals(two_internal.matched_pcnt, 0.5)
        self.assertEquals(two_internal.over_pcnt, 0.0)
        self.assertEquals(two_internal.gt_count, 2)
        self.assertEquals(two_internal.gt_found_count, 2)

    def test_id_no_gt(self):
        two_internal = CalibScore()

        two_internal.add_gt('1', 0, 10)

        two_internal.add_id('1', 0, 8)
        two_internal.add_id('1', 11, 12)

        self.assertEquals(two_internal.missed_pcnt, .2)
        self.assertEquals(two_internal.matched_pcnt, .8)
        self.assertEquals(two_internal.over_pcnt, 0.1)

        self.assertEquals(two_internal.id_count, 2)
        self.assertEquals(two_internal.id_match_count, 1)
        self.assertEquals(two_internal.id_no_gt_count, 1)
        self.assertIsNotNone(two_internal.score)


