# coding: utf-8

"""
    Stencila Hub API

    # Authentication  Many endpoints in the Stencila Hub API require an authentication token. These tokens carry many privileges, so be sure to keep them secure. Do not place your tokens in publicly accessible areas such as client-side code. The API is only served over HTTPS to avoid exposing tokens and other data on the network.  To obtain a token, [`POST /api/tokens`](#operations-tokens-tokens_create) with either a `username` and `password` pair, or an [OpenID Connect](https://openid.net/connect/) token. Then use the token in the `Authorization` header of subsequent requests with the prefix `Token` e.g.      curl -H \"Authorization: Token 48866b1e38a2e9db0baada2140b2327937f4a3636dd5f2dfd8c212341c88d34\" https://hub.stenci.la/api/projects/  Alternatively, you can use `Basic` authentication with the token used as the username and no password. This can be more convenient when using command line tools such as [cURL](https://curl.haxx.se/) e.g.      curl -u 48866b1e38a2e9db0baada2140b2327937f4a3636dd5f2dfd8c212341c88d34: https://hub.stenci.la/api/projects/  Or, the less ubiquitous, but more accessible [httpie](https://httpie.org/):      http --auth 48866b1e38a2e9db0baada2140b2327937f4a3636dd5f2dfd8c212341c88d34: https://hub.stenci.la/api/projects/  In both examples above, the trailing colon is not required but avoids being asked for a password.  # Versioning  The Stencila Hub is released using semantic versioning. The current version is available from the [`GET /api/status`](/api/status) endpoint. Please see the [Github release page](https://github.com/stencila/hub/releases) and the [changelog](https://github.com/stencila/hub/blob/master/CHANGELOG.md) for details on each release. We currently do not provide versioning of the API but plan to do so soon (probably by using a `Accept: application/vnd.stencila.hub+json;version=1.0` request header). If you are using, or interested in using, the API please contact us and we may be able to expedite this.   # noqa: E501

    The version of the OpenAPI document: v1
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import stencila.hub
from stencila.hub.models.job import Job  # noqa: E501
from stencila.hub.rest import ApiException

class TestJob(unittest.TestCase):
    """Job unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Job
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = stencila.hub.models.job.Job()  # noqa: E501
        if include_optional :
            return Job(
                id = 56, 
                status_message = '0', 
                summary_string = '0', 
                runtime_formatted = '0', 
                url = '0', 
                position = 56, 
                children = [
                    56
                    ], 
                key = '0', 
                description = '0', 
                created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                updated = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                began = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                ended = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                status = 'WAITING', 
                is_active = True, 
                method = 'parallel', 
                params = '0', 
                result = '0', 
                error = '0', 
                log = '0', 
                runtime = 1.337, 
                worker = '0', 
                retries = 56, 
                callback_id = '0', 
                callback_method = '0', 
                project = 56, 
                snapshot = '0', 
                creator = 56, 
                queue = 56, 
                parent = 56, 
                callback_type = 56, 
                users = [
                    56
                    ], 
                anon_users = [
                    '0'
                    ]
            )
        else :
            return Job(
                method = 'parallel',
        )

    def testJob(self):
        """Test Job"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
