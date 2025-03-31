import logging
from datetime import datetime, timedelta
from typing import MutableMapping, Optional, cast, TypeVar, Generic
from urllib.parse import quote_plus, urljoin

import httpx

from .. import config as global_config
from ..config import UploaderConfig
from ..utility import retry

logger = logging.getLogger(__name__)


T = TypeVar("T", bound="Uploader")
C = TypeVar("C", bound=UploaderConfig)


class Uploader(Generic[C]):
    fridge: str
    supp: Optional[str]
    _url: str
    latest: datetime

    def __init__(
        self,
        config: C,
        supp=None,
        client: Optional[httpx.AsyncClient] = None,
        factory: bool = False,
    ):
        """
        Initialize an uploader and calculate the URLs.

        In general, this should be created using the create_uploader factory function, if it
        is called directly, raise a RuntimeError.
        """
        if factory is False:
            raise RuntimeError(
                (
                    "Uploaders should be created using the create_uploader "
                    "factory rather than directly."
                )
            )

        self.fridge = global_config.UPLOAD.FRIDGE
        self.supp = supp
        self.supp_str = f"/{supp}" if supp else ""

        fridge_url_safe = quote_plus(self.fridge)
        self._url = urljoin(f"{global_config.UPLOAD.BASE_URL}/", f"{fridge_url_safe}")

        # Are we a supplementary sensor?
        if self.supp is not None:
            supp = quote_plus(self.supp)
            self._url = urljoin(f"{self._url}/", f"supp/{supp}")

        # Create httpx client if not given
        if client is None:
            self.client = httpx.AsyncClient(http2=True)
        else:
            self.client = client

        # Store config
        self.config: C = config

        super().__init__()

    def _mock_upload(self, values: MutableMapping[str, float | datetime | str]) -> str:
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
        self, values: MutableMapping[str, float | datetime]
    ) -> tuple[datetime, MutableMapping[str, float | datetime | str]]:
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
        values_cast = cast(dict[str, float | datetime | str], values)
        values_cast["time"] = latest.isoformat()

        return latest, values_cast

    def _validate_upload_successful(
        self, res: httpx.Response, values: MutableMapping[str, float | datetime | str]
    ) -> bool:
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
        return True

    @property
    def poll_interval(self) -> float:
        """
        Return the polling interval. This is usually every second.
        """
        return 1.0

    @classmethod
    async def create_uploader(
        cls: type[T],
        config: C,
        supp: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
        **kwargs,
    ) -> T:
        new_inst = cls(config, supp=supp, client=client, factory=True, **kwargs)  # type: ignore
        new_inst.latest = await new_inst.get_latest()
        return new_inst

    @retry(exception=(httpx.TimeoutException, httpx.HTTPStatusError))
    async def get_latest(self) -> datetime:
        """
        Return the timestamp of the latest uploaded dataset
        """
        if global_config.UPLOAD.MOCK:
            return datetime.now().astimezone()
        res = await self.client.get(self._url, params={"current": ""})
        data = res.json()
        latest = datetime.fromisoformat(data["time"])
        logger.info("Latest data for fridge %s was %s.", self.fridge, latest.isoformat())
        return latest

    @retry(exception=(httpx.TimeoutException, httpx.HTTPStatusError))
    async def upload(self, raw_values: MutableMapping[str, float | datetime]) -> str:
        """
        Upload the latest dataset to the monitoring server.
        If "time" is not included, set the time to the current time.
        """
        latest, values = self._validate_upload_values(raw_values)

        # If the upload is older than the latest uploaded value, skip the
        # upload
        if latest < self.latest:
            logger.error(
                "Trying to upload an old datapoint: (%s < %s). Skipping",
                latest.isoformat(),
                self.latest.isoformat(),
            )

        # If there is a sufficiently large gap, upload a null value
        if (latest - self.latest).total_seconds() > global_config.UPLOAD.MAX_GAP:
            one_second = timedelta(seconds=1)
            _, blank = self._validate_upload_values({"time": self.latest + one_second})
            if global_config.UPLOAD.MOCK:
                self._mock_upload(blank)
            else:
                await self.client.post(self._url, data=blank)

        # Upload values to server

        if global_config.UPLOAD.MOCK:
            self.latest = latest
            return self._mock_upload(values)
        res = await self.client.post(self._url, data=values)
        self._validate_upload_successful(res, values)

        # Mark successful upload
        self.latest = latest
        return res.text

    async def poll(self) -> bool:
        """
        Check for new values. Return true if new values were uploaded.
        """
        raise NotImplementedError("Uploaders must implement this method to check logs")
