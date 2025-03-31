from math import log10
import logging
from functools import partial
from dataclasses import dataclass
from typing import Optional, Sequence

from .si_prefix import si_format

logger = logging.getLogger(__name__)


@dataclass
class SensorCalibration:
    valid_resistance_range: tuple[float, float]
    valid_temperature_range: tuple[float, float]
    domain: tuple[float, float]
    coefficients: tuple[float, ...]


def poly(
    value: float, coefficients: Sequence[float], domain: tuple[float, float] = (-1.0, 1.0)
) -> float:
    """
    Apply a polynomial to the value with coefficients given. In order to
    ensure the polynomial has reasonable coefficients, we map the domain
    of the values into the window [-1,1] using the domain argument given
    in the Sensor Calibration.
    """
    domain_size = 2.0
    old_size = domain[1] - domain[0]
    offs = (-domain[1] - domain[0]) / old_size
    scale = domain_size / old_size

    value = offs + (value * scale)

    result = 0.0
    for i, coeff in enumerate(coefficients):
        result += coeff * (value**i)
    return result


def powpolylog_res_to_temp(R: float, cal: SensorCalibration) -> Optional[float]:
    """
    Convert a resistance in Ohms to K
    """
    if not (cal.valid_resistance_range[0] <= R <= cal.valid_resistance_range[1]):
        logger.debug(
            "Resistance out of range. %s not in (%s, %s)",
            si_format(R),
            si_format(cal.valid_resistance_range[0]),
            si_format(cal.valid_resistance_range[1]),
        )
        return None
    T = 10 ** poly(log10(R), cal.coefficients, cal.domain)
    if not (cal.valid_temperature_range[0] <= T <= cal.valid_temperature_range[1]):
        logger.debug(
            "Temperature out of range. %sK not in (%sK, %sK)",
            si_format(T),
            si_format(cal.valid_temperature_range[0]),
            si_format(cal.valid_temperature_range[1]),
        )
        return None
    return T


def polylog_res_to_temp(R: float, cal: SensorCalibration) -> Optional[float]:
    """
    Convert a resistance in Ohms to K
    """
    if not (cal.valid_resistance_range[0] <= R <= cal.valid_resistance_range[1]):
        logger.debug(
            "Resistance out of range. %s not in (%s, %s)",
            si_format(R),
            si_format(cal.valid_resistance_range[0]),
            si_format(cal.valid_resistance_range[1]),
        )
        return None
    T = poly(log10(R), cal.coefficients, cal.domain)
    if not (cal.valid_temperature_range[0] <= T <= cal.valid_temperature_range[1]):
        logger.debug(
            "Temperature out of range. %sK not in (%sK, %sK)",
            si_format(T),
            si_format(cal.valid_temperature_range[0]),
            si_format(cal.valid_temperature_range[1]),
        )
        return None
    return T


COEFFICIENTS = {
    "PT1000": SensorCalibration(
        (25.0, 1100.0),
        (24.0, 324.52),
        (1.3, 3.1),
        (
            66.48063884410483,
            81.201299006011,
            76.61891796543149,
            36.353377601466555,
            13.423806958277735,
            114.25915210254354,
            39.697828860801984,
            -127.09231911775309,
            -16.403245448153086,
            55.35302087512681,
        ),
    ),
    "RuO_10K": SensorCalibration(
        (10000.0, 40000.0),
        (1.5, 50.0),
        (4.0, 4.6),
        (
            0.4805189504998839,
            -0.6224617339056723,
            0.31163444622207714,
            -0.0336253189132367,
            0.028505876678703402,
            -0.20370112846659952,
            0.20267261836996248,
            -0.08695299308478183,
            0.016027422138911247,
        ),
    ),
    "RuO_1K5": SensorCalibration(
        (1750.0, 15000.0),
        (0.20, 10.0),
        (3.0, 4.5),
        (
            -0.8220983762789672,
            -1.9397116437203803,
            0.70485569199871,
            -1.0678586824331462,
            0.9294851350215767,
            6.908008307004435,
            -2.8678900165376553,
            -40.36328479590812,
            3.5653583024991655,
            58.30945333682868,
        ),
    ),
    "S0923": SensorCalibration(
        (500.0, 40000.0),
        (0.015, 10.0),
        (2.6, 4.6),
        (
            -1.0177698830567727,
            -1.2187576202050847,
            0.6682348268110353,
            -0.14814611639034952,
            -0.8268264165842213,
            0.3447246213899655,
            1.3695166867902584,
            -0.9856762170735657,
        ),
    ),
    "TT_1326": SensorCalibration(
        (1250.0, 100000.0),
        (0.012, 10.0),
        (3.1, 5.0),
        (
            -0.9372668187770127,
            -1.2128607616126896,
            0.3933665523493362,
            0.06921398302989855,
            0.076087063758759,
            -0.9989534549077275,
            0.8747052767245405,
            0.5035848662069046,
            -0.6874002578147611,
        ),
    ),
    "U07461": SensorCalibration(
        (950.0, 10000.0),
        (0.006, 310.00),
        (2.9, 4.0),
        (
            -0.7982257929030702,
            -1.7211096406341744,
            0.6145589170200011,
            -3.0450826102493345,
            4.339598381789733,
            4.57559898923046,
            -7.843033830200717,
            -3.0363154287978382,
            4.656024788352065,
        ),
    ),
    "U08337": SensorCalibration(
        (950.0, 10000.0),
        (0.006, 310.00),
        (2.9, 4.0),
        (
            -0.8232643629154656,
            -1.7260355632135242,
            0.6069998760248387,
            -2.961315939838501,
            4.089623845067158,
            4.233669245559866,
            -7.061055754905433,
            -2.7136187415381827,
            4.083346471065906,
        ),
    ),
}
CALIBRATIONS = {
    "PT1000": partial(polylog_res_to_temp, cal=COEFFICIENTS["PT1000"]),
    "RuO_10K": partial(powpolylog_res_to_temp, cal=COEFFICIENTS["RuO_10K"]),
    "RuO_1K5": partial(powpolylog_res_to_temp, cal=COEFFICIENTS["RuO_1K5"]),
    "S0923": partial(powpolylog_res_to_temp, cal=COEFFICIENTS["S0923"]),
    "TT_1326": partial(powpolylog_res_to_temp, cal=COEFFICIENTS["TT_1326"]),
    "U07461": partial(powpolylog_res_to_temp, cal=COEFFICIENTS["U07461"]),
    "U08337": partial(powpolylog_res_to_temp, cal=COEFFICIENTS["U08337"]),
}
VALID_CALS = ", ".join(CALIBRATIONS)
