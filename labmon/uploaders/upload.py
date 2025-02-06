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

    def __init__(self, supp=None, client: httpx.Client = None):
        self.fridge = config.UPLOAD.FRIDGE
        self.supp = supp

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
            self._url = urljoin(self._url, f"data/{supp}")

        # Store the time of the latest upload
        self.latest = self.get_latest()

    @retry(exception=httpx.TimeoutException)
    def get_latest(self):
        """
        Return the timestamp of the latest uploaded dataset
        """
        res = self.client.get(self._url, params={"current": ""})
        data = res.json()
        latest = datetime.fromisoformat(data["time"])
        logger.info(
            "Latest data for fridge %s was %s.", self.fridge, latest.isoformat()
        )
        return latest

    @retry(exception=httpx.TimeoutException)
    def upload(self, values: dict[str, float | datetime]):
        """
        Upload the latest dataset to the monitoring server.
        If "time" is not included, set the time to the current time.
        """
        if "time" not in values:
            values["time"] = datetime.now().isoformat()
        elif isinstance(values["time"], datetime):
            values["time"] = values["time"].isoformat()
        else:
            raise ValueError(
                f"Invalid format for time. Expecting datetime, got {values['time']:r}."
            )

        if config.UPLOAD.MOCK:
            logger.info(
                "Mock upload data for fridge %s at time %s. Data was: %r",
                self.fridge,
                values["time"],
                values,
            )
            return "OK"

        # Upload to server
        res = self.client.post(self._url, data=values).raise_for_status()
        logger.info(
            "Uploaded data for fridge %s at time %s. Status: %d.",
            self.fridge,
            values["time"],
            res.status_code,
        )
        logger.debug("Response: %s", res.text)
        return res.text
