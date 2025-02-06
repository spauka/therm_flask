# %%
from cmath import exp, pi, sqrt
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import scipy
from numpy import random
from numpy.fft import rfft

rng = random.default_rng()
npts = 40

signal = np.ones(npts).cumsum() + rng.normal(scale=0.3, size=npts)
signal = 10 * np.sin(2 * signal) + rng.normal(scale=0.5, size=npts)
signal += 40

plt.plot(signal)


# %%
def hilbert_amplitude_scipy(data):
    """Estimate amplitude using Hilbert transform over the last n samples."""
    analytic_signal = scipy.signal.hilbert(data)
    envelope = np.abs(analytic_signal)  # Instantaneous amplitude
    return sorted(envelope)[len(envelope) // 2]


# %%
window_size = 10
scipy_amplitude = np.zeros(npts - window_size)
for i in range(npts - window_size):
    scipy_amplitude[i] = hilbert_amplitude_scipy(signal[i : i + window_size])

plt.plot(signal)
plt.plot(scipy_amplitude)
# %%
from labmon.utility.hilbert import hilbert_amplitude

window_size = 10
amplitude = np.zeros(npts - window_size)
for i in range(npts - window_size):
    amplitude[i] = hilbert_amplitude(signal[i : i + window_size])

plt.plot(signal)
plt.plot(scipy_amplitude)
plt.plot(amplitude)

# %%
# Compare FFT implementations

fft_np = rfft(signal, norm="ortho")
fft_py = dft(signal)
plt.plot(np.abs(fft_np))
plt.plot(np.abs(fft_py))

# %% Check that original signal is restored with iFFT
plt.plot(signal)
plt.plot(np.real(dft(dft(signal), inverse=True)))

# %% Compare Hilbert Transform implementations
hil_scipy = np.abs(scipy.signal.hilbert(signal))
hil_py = np.abs(hilbert_transform(signal))

plt.plot(signal)
plt.plot(hil_scipy)
plt.plot(hil_py)

# %%
