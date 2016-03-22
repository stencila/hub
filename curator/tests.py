#  This file is part of Stencila Hub.
#  
#  Copyright (C) 2015-2016 Stencila Ltd.
#  
#  Stencila Hub is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  Stencila Hub is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  
#  You should have received a copy of the GNU Affero General Public License
#  along with Stencila Hub.  If not, see <http://www.gnu.org/licenses/>.

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
