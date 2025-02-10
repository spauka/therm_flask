import logging
from datetime import datetime
from typing import Optional
from urllib.parse import quote_plus, urljoin

import httpx

from .. import config
from ..utility import retry

logger = logging.getLogger(__name__)


class Uploader:
    fridge: str
    supp: Optional[str]
    _url: str
    latest: datetime

    def __init__(self, supp=None, client: Optional[httpx.Client] = None):
        self.fridge = config.UPLOAD.FRIDGE
        self.supp = supp
        self.supp_str = f"/{supp}" if supp else ""

        fridge_url_safe = quote_plus(self.fridge)
        self._url = urljoin(f"{config.UPLOAD.BASE_URL}/", f"{fridge_url_safe}")

        # Create httpx client
        if client is None:
            self.client = httpx.Client(http2=True)
        else:
            self.client = client

        # Are we a supplementary sensor?
        if self.supp is not None:
            supp = quote_plus(self.supp)
            self._url = urljoin(f"{self._url}/", f"supp/{supp}")

        # Store the time of the latest upload
        self.latest = self.get_latest()

    @retry(exception=(httpx.TimeoutException, httpx.HTTPStatusError))
    def get_latest(self):
        """
        Return the timestamp of the latest uploaded dataset
        """
        res = self.client.get(self._url, params={"current": ""})
        data = res.json()
        latest = datetime.fromisoformat(data["time"])
        logger.info("Latest data for fridge %s was %s.", self.fridge, latest.isoformat())
        return latest

    @retry(exception=(httpx.TimeoutException, httpx.HTTPStatusError))
    def upload(self, values: dict[str, float | datetime | str]) -> str:
        """
        Upload the latest dataset to the monitoring server.
        If "time" is not included, set the time to the current time.
        """
        if "time" not in values:
            self.latest = datetime.now().astimezone()
        elif isinstance(values["time"], datetime):
            self.latest = values["time"]
        elif isinstance(values["time"], str):
            # Check that the format is valid
            try:
                self.latest = datetime.fromisoformat(values["time"]).astimezone()
            except ValueError as e:
                raise ValueError(
                    f"Invalid format for time. Expecting datetime, got {values['time']}."
                ) from e
        else:
            raise ValueError(
                f"Invalid format for time. Expecting datetime, got {values['time']!r}."
            )
        values["time"] = self.latest.isoformat()

        if config.UPLOAD.MOCK:
            logger.info(
                "Mock upload data for fridge %s%s at time %s. Data was: %r",
                self.fridge,
                self.supp_str,
                values["time"],
                values,
            )
            return "OK"

        # Upload to server
        res = self.client.post(self._url, data=values)
        if not 200 <= res.status_code < 300:
            logger.error(
                "Request for fridge %s%s failed with status %d. Response was: %s",
                self.fridge,
                self.supp_str,
                res.status_code,
                res.text,
            )
            res.raise_for_status()
        logger.info(
            "Uploaded data for fridge %s%s at time %s. Status: %d.",
            self.fridge,
            self.supp_str,
            values["time"],
            res.status_code,
        )
        logger.debug("Response: %s", res.text)
        return res.text

    def poll(self):
        """
        Check for new values
        """
        raise NotImplementedError("Uploaders must implement this method to check logs")
