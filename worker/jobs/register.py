import io
import json
import logging
import os
import re
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
        self, server: Optional[str] = None, credentials: Optional[str] = None,
    ):
        super().__init__()
        self.server = server
        self.credentials = credentials

    def do(self, node: dict, doi: str, url: str, batch: str, *args, **kwargs) -> dict:  # type: ignore
        assert node is not None
        assert "type" in node and node["type"] in ("Article", "Review")

        # Generate Crossref deposit XML
        json_str = json.dumps(node).encode("utf-8")
        xml = Convert().do(
            json_str, "-", {"from": "json", "to": "crossref", "doi": doi, "url": url},  # type: ignore
        )
        if not xml:
            raise RuntimeError("Failed to convert node to Crossref XML")

        # Replace batch id and email
        xml = re.sub(
            r"<doi_batch_id>[^<]*</doi_batch_id>",
            f"<doi_batch_id>{batch}</doi_batch_id>",
            xml,
        )
        xml = re.sub(
            r"<email_address>[^<]*</email_address>",
            r"<email_address>doi@hub.stenci.la</email_address>",
            xml,
        )

        server = self.server or os.getenv("CROSSREF_DEPOSIT_SERVER")
        if not server:
            # If no server explicitly defined then use test server.
            # Do not fallback to production server to avoid inadvertent
            # use during testing.
            server = "https://test.crossref.org/servlet/deposit"

        credentials = self.credentials or os.getenv("CROSSREF_DEPOSIT_CREDENTIALS")
        if not credentials:
            # If no credentials were available for the registration agency
            # then log a warning and return an empty dictionary.
            # This allows testing during development without having to have
            # credentials
            logger.warning("Credentials for DOI registrar are not available")
            return dict()

        # Deposit XML
        username, password = credentials.split(":")
        deposited = datetime.utcnow().isoformat()
        response = httpx.post(
            server,
            data=dict(login_id=username, login_passwd=password),
            files=dict(fname=io.BytesIO(xml.encode())),
        )

        # Crossref returns 200 response with an error message for bad login credentials
        # so we need to check for 'SUCCESS' in the response body
        deposit_success = response.status_code == 200 and "SUCCESS" in response.text
        if not deposit_success:
            logger.error("Unexpected response from Crossref")

        # Return details of this job
        return dict(
            deposited=deposited,
            deposit_request=dict(body=xml),
            deposit_response=dict(
                status=dict(code=response.status_code),
                headers=dict(response.headers),
                body=response.text,
            ),
            deposit_success=deposit_success,
        )
