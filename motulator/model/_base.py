from dataclasses import dataclass

@dataclass
class NominalValues:
    """
    Base values.

    Base values are computed from the nominal values and the number of pole
    pairs. They can be used, e.g., for scaling the plotted waveforms.

    Parameters
    ----------
    U_nom : float
        Voltage (V, rms, line-line).
    I_nom : float
        Current (A, rms).
    f_nom : float
        Frequency (Hz).
    tau_nom : float
        Torque (Nm).
    P_nom : float
        Power (W).
    n_p : int
        Number of pole pairs.
    """
    U_nom: float
    I_nom: float
    f_nom: float
    P_nom: float
    tau_nom: float
    n_p: int

@dataclass
class BaseValues:
    """
    Parameters
    ----------
    u : float
        Base voltage (V, peak, line-neutral).
    i : float
        Base current (A, peak).
    w : float
        Base angular frequency (rad/s).
    psi : float
        Base flux linkage (Vs).
    p : float
        Base power (W).
    Z : float
        Base impedance (Ω).
    L : float
        Base inductance (H).
    tau : float
        Base torque (Nm).

    """
    u : float
    i : float
    w : float
    psi: float
    p : float
    Z: float
    L: float
    tau : float