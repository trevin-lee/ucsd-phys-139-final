
# ------------------------------------------------------------
# Helper: Compute 8th-order Fourier coefficients
# ------------------------------------------------------------
def fourier_fit(phi, f, order=8):
    """
    Fit an nth-order Fourier series to flux values.
    Returns the full coefficient vector [a0, a1..aN, b1..bN].
    """
    # design matrix: [1, cos1..cosN, sin1..sinN]
    X = [np.ones_like(phi)]
    for k in range(1, order+1):
        X.append(np.cos(2*np.pi*k*phi))
    for k in range(1, order+1):
        X.append(np.sin(2*np.pi*k*phi))
    X = np.column_stack(X)

    coeffs, *_ = np.linalg.lstsq(X, f, rcond=None)
    return coeffs


# ------------------------------------------------------------
# Helper: Compute Fourier-based features
# ------------------------------------------------------------
def fourier_features(period, t, f):
    phi = (t / period) % 1
    coeffs = fourier_fit(phi, f, order=8)

    # unpack coefficients
    a = coeffs[1:9]      # a1..a8
    b = coeffs[9:17]     # b1..b8

    # Fourier amplitude for each harmonic
    A = np.sqrt(a**2 + b**2)

    # avoid divide-by-zero
    if A[0] == 0:
        R21 = R31 = np.nan
    else:
        R21 = A[1] / A[0]
        R31 = A[2] / A[0]

    # Fourier phases
    phi_k = np.arctan2(-b, a)

    phi21 = phi_k[1] - 2*phi_k[0]
    phi31 = phi_k[2] - 3*phi_k[0]

    # compute model amplitude (peak-to-peak)
    phi_grid = np.linspace(0, 1, 2000)
    Xg = np.column_stack(
        [np.ones_like(phi_grid)] +
        [np.cos(2*np.pi*k*phi_grid) for k in range(1, 9)] +
        [np.sin(2*np.pi*k*phi_grid) for k in range(1, 9)]
    )
    model = Xg.dot(coeffs)
    Amp = model.max() - model.min()

    return R21, R31, phi21, phi31, Amp


# ------------------------------------------------------------
# Helper: Stetson K index
# ------------------------------------------------------------
def stetson_K(f):
    # Use normalized residuals (errors unknown; use std)
    delta = (f - np.mean(f)) / np.std(f)
    return (np.sum(np.abs(delta)) / np.sqrt(len(f))) / np.sqrt(np.sum(delta**2))

