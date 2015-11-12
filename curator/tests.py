import unittest

from curator import Curator

curator = Curator()
curator.store_temporary()
print curator.store


class ComponentTests(unittest.TestCase):

    def test_init(self):
        curator.init('foo', 'stencil')

        meta = curator.meta('foo')
        self.assertEqual(
            meta['type'],
            'stencil'
        )
        self.assertEqual(
            meta['title'],
            ''
        )
        #self.assertEqual(
        #    curator.commits('foo'),
        #    'stencil'
        #)


if __name__ == '__main__':
    unittest.main()
