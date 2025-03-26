from math import log10

CALIBRATIONS = {
    "PT1000": (
        -128349.515953672,
        569881.315037663,
        -1110371.16770621,
        1246176.89722544,
        -887917.400767292,
        416637.746192204,
        -128790.025704277,
        25299.624652812,
        -2867.046948082,
        142.875821665,
    ),
    "RuO_10K": (
        6909.149278,
        -38314.10597,
        93795.12172,
        -132881.1907,
        120024.6642,
        -71674.9838,
        28300.34447,
        -7125.7046,
        1038.446473,
        -66.75479913,
    ),
    "RuO_1K5": (
        -109406225.453069,
        264570367.275206,
        -284130767.924156,
        177858095.325872,
        -71516430.0477208,
        19156216.6038666,
        -3418108.54721648,
        391778.170838493,
        -26174.3212975398,
        776.590777082747,
    ),
    "S0923": (
        10379.934115782,
        -19555.766089189,
        15743.547719455,
        -7015.940352528,
        1868.772009588,
        -297.498475028,
        26.208557355,
        -0.985676217,
    ),
    "TT_1326": (
        -81196.2165137754,
        160882.2563326589,
        -138861.5120112078,
        68220.570158686,
        -20871.3114791728,
        4072.7376928084,
        -495.1244851374,
        34.2922425509,
        -1.0361457633,
    ),
}
_VALID_CALS = ", ".join(CALIBRATIONS)


def poly(value, coefficients):
    """
    Apply a polynomial to the value with coefficients given
    """
    result = 0.0
    for i, coeff in enumerate(coefficients):
        result += coeff * (value**i)
    return result


def polylog_res_to_temp(R: float, cal: str):
    """
    Convert a resistance in Ohms to mK
    """
    if cal not in CALIBRATIONS:
        raise KeyError(f"Unknown calibration curve. Valid curves are: {_VALID_CALS}.")

    poly = CALIBRATIONS[cal]
    return 10 ** poly(log10(R)) / 1000
