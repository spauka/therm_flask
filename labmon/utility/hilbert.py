"""
An inefficient pure python implementation of a hilbert transform
using a DFT. Don't use for large N since this is a naive
O(N^2) implementation of the FFT.
"""

from cmath import exp, pi, sqrt
from itertools import product


def dft(in_arr, inverse=False):
    """Compute the Discrete Fourier Transform (DFT) of a signal."""
    size = len(in_arr)
    sq_size = sqrt(size)
    out_arr = [0 + 0j] * size
    phase = 1 if inverse else -1
    for k, n in product(range(size), repeat=2):
        angle = phase * 2j * pi * k * n / size
        out_arr[k] += in_arr[n] * exp(angle)
    for n in range(size):
        out_arr[n] /= sq_size
    return out_arr


def hilbert_transform(in_arr):
    """Compute the analytic signal using the Hilbert transform (DFT method)."""
    size = len(in_arr)
    dft_in = dft(in_arr)

    # Apply Hilbert transform filter
    H = [0] * size
    H[0] = 1  # Keep DC component
    if size % 2 == 0:
        H[size // 2] = 1  # Keep Nyquist frequency for even N
        for i in range(1, size // 2):
            H[i] = 2  # Double positive frequencies
    else:
        for i in range(1, (size + 1) // 2):
            H[i] = 2  # Double positive frequencies

    hilbert = [h * x for h, x in zip(H, dft_in)]
    analytic = dft(hilbert, inverse=True)

    return analytic  # Complex-valued: real part is original signal, imag part is Hilbert transform


def hilbert_amplitude(in_arr):
    """
    Estimate p-p amplitude using the Hilbert Transform
    """
    mean = sum(in_arr) / len(in_arr)
    zero_mean_data = [x - mean for x in in_arr]
    analytic = hilbert_transform(zero_mean_data)
    envelope = [abs(z) for z in analytic]
    return 2 * (sorted(envelope)[len(envelope) // 2])
