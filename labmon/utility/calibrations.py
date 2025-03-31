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
    coefficients: tuple[float, ...]


def poly(value: float, coefficients: Sequence[float]) -> float:
    """
    Apply a polynomial to the value with coefficients given
    """
    result = 0.0
    for i, coeff in enumerate(coefficients):
        result += coeff * (value**i)
    return result


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
    T = 10 ** poly(log10(R), cal.coefficients)
    if not (cal.valid_temperature_range[0] <= T <= cal.valid_temperature_range[1]):
        logger.debug(
            "Temperature out of range. %sK not in (%sK, %sK)",
            si_format(T),
            si_format(cal.valid_temperature_range[0]),
            si_format(cal.valid_temperature_range[1]),
        )
        return None
    return T


def poly_res_to_temp(R: float, cal: SensorCalibration):
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
    T = poly(R, cal.coefficients)
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
        (
            70.10329098692411,
            82.16896119814967,
            71.12750504674811,
            33.244489786828986,
            29.409211935698128,
            84.95996565044273,
            0.7326105461269541,
            -80.03560110991899,
            2.8621672362292774,
            29.947397402226592,
        ),
    ),
    "RuO_10K": SensorCalibration(
        (10000.0, 40000.0),
        (1.5, 50.0),
        (
            0.43706203238170005,
            -0.5399767944388554,
            0.26590442728624925,
            -0.027925413247050484,
            -0.02317078920837366,
            -0.09010325134446752,
            0.10712030716983773,
            -0.0467519952874548,
            0.009320432246085766,
            -0.0007137726369595544,
        ),
    ),
    "RuO_1K5": SensorCalibration(
        (1700.0, 1500.0),
        (0.20, 10.0),
        (
            -0.7528436274939896,
            -1.277250247617485,
            0.33727590218394626,
            -0.292701112505275,
            -0.046978729624973986,
            0.6980966288658188,
            0.48393097328169654,
            -1.7183241691259399,
            -0.42379276537732813,
            1.0611141049035564,
        ),
    ),
    "S0923": SensorCalibration(
        (500.0, 40000.0),
        (0.015, 10.0),
        (
            -1.077654588308761,
            -1.0969339022761835,
            0.5737724845878533,
            -0.26115069686369846,
            -0.5671370356507759,
            0.5515197810399867,
            0.7578648883494862,
            -0.6962089113316896,
        ),
    ),
    "TT_1326": SensorCalibration(
        (1250.0, 100000.0),
        (0.012, 10.0),
        (
            -0.935293292363173,
            -1.2161142510803213,
            0.39430952919126094,
            0.06902821362471284,
            0.0847940948132107,
            -1.015679465187239,
            0.877434834528599,
            0.5183915172243648,
            -0.6963947317941702,
        ),
    ),
    "U07461": SensorCalibration(
        (950.0, 10000.0),
        (0.006, 310.00),
        (
            -0.9515788745978372,
            -1.518697812463814,
            0.02089917439784794,
            -0.9108864460475615,
            3.681140110114769,
            -0.02079237839616522,
            -4.909685719878941,
            0.1795456623828366,
            2.1720700698012942,
        ),
    ),
    "U08337": SensorCalibration(
        (950.0, 10000.0),
        (0.006, 310.00),
        (
            -0.9770835272916927,
            -1.523298991321712,
            0.021854498635399695,
            -0.9282184165042838,
            3.474386065785106,
            0.05155323554186139,
            -4.427169378002716,
            0.13141343240039943,
            1.9049121427000089,
        ),
    ),
}
CALIBRATIONS = {
    "PT1000": partial(poly_res_to_temp, cal=COEFFICIENTS["PT1000"]),
    "RuO_10K": partial(polylog_res_to_temp, cal=COEFFICIENTS["RuO_10K"]),
    "RuO_1K5": partial(polylog_res_to_temp, cal=COEFFICIENTS["RuO_1K5"]),
    "S0923": partial(polylog_res_to_temp, cal=COEFFICIENTS["S0923"]),
    "TT_1326": partial(polylog_res_to_temp, cal=COEFFICIENTS["TT_1326"]),
    "U07461": partial(polylog_res_to_temp, cal=COEFFICIENTS["U07461"]),
    "U08337": partial(polylog_res_to_temp, cal=COEFFICIENTS["U08337"]),
}
VALID_CALS = ", ".join(CALIBRATIONS)
