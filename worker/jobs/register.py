import io
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx

from jobs.base.job import Job
from jobs.convert import Convert

logger = logging.getLogger(__name__)


class Register(Job):
    """
    A job that registers a DOI with a registration agency.

    Currently, the only DOI supported in Crossref, although this could be expand
    to other agencies in the future.

    See https://www.crossref.org/education/member-setup/direct-deposit-xml/https-post/.
    """

    name = "register"

    def __init__(
        self,
        server: str = "https://crossref.org/servlet/deposit",
        credentials: Optional[str] = None,
    ):
        super().__init__()
        self.server = server
        self.credentials = credentials

    def do(self, node: dict, doi: str, url: str) -> dict:  # type: ignore
        credentials = self.credentials or os.getenv("CROSSREF_API_CREDENTIALS")
        if not credentials:
            raise PermissionError("Credentials for DOI registrar are not available")
        username, password = credentials.split(":")

        # Generate Crossref deposit XML
        convert = Convert()
        xml = convert.run(
            json.dumps(node).encode("utf-8"),
            "-",
            {"from": "json", "to": "crossref", "doi": doi, "url": url},
        ).get("result")
        if not xml:
            raise RuntimeError("Failed to convert node to Crossref XML")

        # Deposit to server
        deposited = datetime.utcnow().isoformat()
        response = httpx.post(
            self.server,
            data=dict(login_id=username, login_passwd=password),
            files=dict(fname=io.StringIO(xml)),
        )

        # Crossref returns 200 response with an error message for bad login credentials
        # so we need to check for 'SUCCESS' in the response body
        registered = None
        if response.status_code == 200 and "SUCCESS" in response.text:
            registered = datetime.utcnow().isoformat()
        else:
            logger.error(f"Unexpected response from {self.server}")

        # Return details of this job
        return dict(
            deposited=deposited,
            registered=registered,
            request=dict(body=xml),
            response=dict(
                status=dict(code=response.status_code),
                headers=response.headers,
                body=response.text,
            ),
        )
