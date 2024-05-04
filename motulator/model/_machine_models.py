"""Continuous-time models for machines."""

from dataclasses import dataclass

class InductionMachine:
    """
    Γ-equivalent model of an induction machine.

    An induction machine is modeled using the Γ-equivalent model [#Sle1989]_. 
    The model is implemented in stator coordinates. The flux linkages are used 
    as state variables.

    Parameters
    ----------
    n_p : int
        Number of pole pairs.
    R_s : float
        Stator resistance (Ω).
    R_r : float
        Rotor resistance (Ω).
    L_ell : float
        Leakage inductance (H).
    L_s : float
        Stator inductance (H).

    Notes
    -----
    The Γ model is chosen here since it can be extended with the magnetic
    saturation model in a straightforward manner. If the magnetic saturation is
    omitted, the Γ model is mathematically identical to the inverse-Γ and T
    models [#Sle1989]_.

    References
    ----------
    .. [#Sle1989] Slemon, "Modelling of induction machines for electric 
       drives," IEEE Trans. Ind. Appl., 1989, https://doi.org/10.1109/28.44251

    """
    n_p : int
    R_s : float
    R_r: float
    L_ell: float
    L_s: float
    psi_ss0: float
    psi_rs0: float

    def __init__(self, n_p, R_s, R_r, L_ell, L_s, psi_ss = 0j, psi_rs0 = 0j):
        self.n_p = n_p
        self.R_s, self.R_r = R_s, R_r
        self.L_ell, self.L_s = L_ell, L_s
        self.psi_ss0, self.psi_rs0 = psi_ss, psi_rs0

class InductionMachineInvGamma:
    """
    Inverse-Γ model of an induction machine.

    This extends the InductionMachine class (based on the Γ model) by providing
    an interface for the inverse-Γ model parameters. Linear magnetics are 
    assumed. If magnetic saturation is to be modeled, the Γ model is preferred.

    Parameters
    ----------
    n_p : int
        Number of pole pairs.
    R_s : float
        Stator resistance (Ω).
    R_R : float
        Rotor resistance (Ω).
    L_sgm : float
        Leakage inductance (H).
    L_M : float
        Magnetizing inductance (H).

    """
    n_p : int
    R_s : float
    R_R: float
    L_sgm: float
    L_M: float
    psi_ss0: float
    psi_rs0: float

    def __init__(self, n_p, R_s, R_R, L_sgm, L_M, psi_ss0 = 0j, psi_rs0 = 0j):
        self.n_p = n_p
        self.R_s, self.R_R = R_s, R_R
        self.L_sgm, self.L_M = L_sgm, L_M
        self.psi_ss0, self.psi_rs0 = psi_ss0, psi_rs0


class SynchronousMachine:
    """
    Synchronous machine model.

    This models a synchronous machine in rotor coordinates. The stator flux 
    linkage and the electrical angle of the rotor are the state variables. 

    Parameters
    ----------
    n_p : int
        Number of pole pairs.
    R_s : float
        Stator resistance (Ω).
    L_d : float
        d-axis inductance (H).
    L_q : float
        q-axis inductance (H).
    psi_f : float
        PM-flux linkage (Vs).

    """

    n_p : int
    R_s : float
    L_d: float
    L_q: float
    psi_f: float
    psi_s0: float
    theta_m0: float

    def __init__(self, n_p, R_s, L_d, L_q, psi_f, theta_m0 = 0):
        self.n_p, self.R_s = n_p, R_s
        self.L_d, self.L_q, self.psi_f = L_d, L_q, psi_f
        self.psi_s0 = complex(psi_f)
        self.theta_m0 = theta_m0