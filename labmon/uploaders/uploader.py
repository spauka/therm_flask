import logging
from datetime import datetime
from typing import Optional
from urllib.parse import quote_plus, urljoin

import httpx

from .. import config
from ..utility import retry

logger = logging.getLogger(__name__)


class BaseUploader:
    fridge: str
    supp: Optional[str]
    _url: str
    latest: datetime

    def __init__(self, supp: Optional[str] = None):
        self.fridge = config.UPLOAD.FRIDGE
        self.supp = supp
        self.supp_str = f"/{supp}" if supp else ""

        fridge_url_safe = quote_plus(self.fridge)
        self._url = urljoin(f"{config.UPLOAD.BASE_URL}/", f"{fridge_url_safe}")

        # Are we a supplementary sensor?
        if self.supp is not None:
            supp = quote_plus(self.supp)
            self._url = urljoin(f"{self._url}/", f"supp/{supp}")

    def _mock_upload(self, values: dict[str, float | datetime | str]):
        """
        Mock upload - log but don't actually send data
        """
        logger.info(
            "Mock upload data for fridge %s%s at time %s. Data was: %r",
            self.fridge,
            self.supp_str,
            values["time"],
            values,
        )
        return "OK"

    def _validate_upload_values(
        self, values: dict[str, float | datetime | str]
    ) -> tuple[datetime, dict[str, float | datetime | str]]:
        """
        If "time" is not included, set the time to the current time, and ensure
        that a timezone is always attached to the upload info.
        """

        if "time" not in values:
            latest = datetime.now().astimezone()
        elif isinstance(values["time"], datetime):
            # Ensure that the time has a timezone attached
            if values["time"].tzinfo is None:
                values["time"] = values["time"].astimezone()
            latest = values["time"]
        elif isinstance(values["time"], str):
            # Check that the format is valid
            try:
                latest = datetime.fromisoformat(values["time"])
                if latest.tzinfo is None:
                    latest = latest.astimezone()
                values["time"] = latest
            except ValueError as e:
                raise ValueError(
                    f"Invalid format for time. Expecting datetime, got {values['time']}."
                ) from e
        else:
            raise ValueError(
                f"Invalid format for time. Expecting datetime, got {values['time']!r}."
            )
        values["time"] = latest.isoformat()

        return latest, values

    def _validate_upload_successful(
        self, res: httpx.Response, values: dict[str, float | datetime | str]
    ):
        """
        Validate that the upload was successful
        """
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
        logger.debug("Response was: %s", res.text)


class AsyncUploader(BaseUploader):
    def __init__(self, supp=None, client: Optional[httpx.AsyncClient] = None):
        # Create httpx client
        if client is None:
            self.client = httpx.AsyncClient(http2=True)
        else:
            self.client = client

        super().__init__(supp)

    @classmethod
    async def create_uploader(
        cls, *args, supp=None, client: Optional[httpx.AsyncClient] = None, **kwargs
    ):
        new_inst = cls(*args, supp=supp, client=client, **kwargs)
        new_inst.latest = await new_inst.get_latest()
        return new_inst

    @retry(exception=(httpx.TimeoutException, httpx.HTTPStatusError))
    async def get_latest(self) -> datetime:
        """
        Return the timestamp of the latest uploaded dataset
        """
        res = await self.client.get(self._url, params={"current": ""})
        data = res.json()
        latest = datetime.fromisoformat(data["time"])
        logger.info("Latest data for fridge %s was %s.", self.fridge, latest.isoformat())
        return latest

    @retry(exception=(httpx.TimeoutException, httpx.HTTPStatusError))
    async def upload(self, values: dict[str, float | datetime | str]) -> str:
        """
        Upload the latest dataset to the monitoring server.
        If "time" is not included, set the time to the current time.
        """
        latest, values = self._validate_upload_values(values)

        if config.UPLOAD.MOCK:
            self.latest = latest
            return self._mock_upload(values)

        # Upload to server
        res = await self.client.post(self._url, data=values)
        self._validate_upload_successful(res, values)

        # Mark successful upload
        self.latest = latest
        return res.text

    def poll(self):
        """
        Check for new values
        """
        raise NotImplementedError("Uploaders must implement this method to check logs")


class Uploader(BaseUploader):
    def __init__(self, supp=None, client: Optional[httpx.Client] = None):
        # Create httpx client
        if client is None:
            self.client = httpx.Client(http2=True)
        else:
            self.client = client

        super().__init__(supp)

    @classmethod
    def create_uploader(cls, *args, supp=None, client: Optional[httpx.Client] = None, **kwargs):
        new_inst = cls(*args, supp=supp, client=client, **kwargs)
        new_inst.latest = new_inst.get_latest()
        return new_inst

    @retry(exception=(httpx.TimeoutException, httpx.HTTPStatusError))
    def get_latest(self) -> datetime:
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
        latest, values = self._validate_upload_values(values)

        if config.UPLOAD.MOCK:
            self.latest = latest
            return self._mock_upload(values)

        # Upload to server
        res = self.client.post(self._url, data=values)
        self._validate_upload_successful(res, values)

        # Mark successful upload
        self.latest = latest
        return res.text

    def poll(self):
        """
        Check for new values
        """
        raise NotImplementedError("Uploaders must implement this method to check logs")
