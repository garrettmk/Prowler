import unittest

from responseparser import read_quantity


class ReadQuantityTest(unittest.TestCase):
    """Test the output of the read_quantity() method.

    There are a few main forms to handle:

        (container) [consist/s] of (quantity)
            As in: pack of 6
        (quantity) (per) (container)
            As in: 12/dz, 6-pk, 12/case, 1dz per set

        (quantity)(multiplier)
            As in: 12dz, 1 pair, 6 each

    'quantity' can take several forms:

        12
        (12)
        1dz
        1 dozen
        1,000


    'per' can take several forms as well:

        per
        -
        /

    'per' can also be blank, as in '12pk'

    Sometimes the name of the item is inserted as well, such as:

        (quantity) widgets (per) (container)

    """

    group_1 = [('Pack of 12', 12),
               ('packs of (12)', 12),
               ('pk of 1dz', 12),
               ('cases of 1 dozen', 12),
               ('cs of 1,000', 1000),
               ('case (12) dozen', 144),
               #('box 12', 12),

               ('sets consist of 12', 12),
               ('box consists of (12)', 12),
               ('boxes consist of 1 dozen', 12),
               ('bags consist of (1) dz', 12),
               ('case consists of 1,000 pieces', 1000),

               ('12pk', 12),
               ('12 pack', 12),
               ('12-pack', 12),
               ('12/pack', 12),
               ('12 / set', 12),
               ('12 per carton', 12),

               ('(12)pk', 12),
               ('(12) pack', 12),
               ('(12)-pack', 12),
               ('(12)/set', 12),
               ('(12) per carton', 12),

               ('1dz pack', 12),
               ('1 dozen - pack', 12),
               ('1dz / set', 12),
               ('1 dozen per box', 12),

               ('1,000 pk', 1000),
               ('1,000-pack', 1000),
               ('1,000/set', 1000),
               ('1,000 per case', 1000),

               ('12 pieces / set', 12),
               ('12 bloops/set', 12),
               ('12ears/set', 12),
               ('1dz bloops / set', 12),
               ('12pc per case', 12),
               ('(12) pieces / box', 12),
               ('(12) bloops per carton', 12),
               ('(1,000) pieces / case', 1000),
               ('1dz bloops per box', 12),
               ('(1) dz pieces/set', 12),

               ('1dz', 12),
               ('1-dozen', 12),
               ('(6) each', 6),
               ('2 pair', 4),
               ('12-piece', 12),
               ('12 piece', 12),
               ('(12)/piece', 12),
               ('1,000 pcs', 1000),

               ('doesn\'t look like anything to me', None),
               ('12345 castor wheels', None),
               ('12345 stand', None),
               ('15/2016 by Steve', None),
               ('st990', None),
               ('1 fact', None),
               ('blasts of 10 meters', None)]

    def test_strings(self):
        for pair in self.group_1:
            with self.subTest(string=pair[0]):
                self.assertEqual(read_quantity(pair[0]), pair[1])

if __name__ == '__main__':
    unittest.main()