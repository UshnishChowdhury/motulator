"""Open Loop control method for Current-Source Converters."""

from cmath import exp
from dataclasses import dataclass
from math import pi, sqrt

from motulator.common.control._base import TimeSeries
from motulator.common.utils._utils import wrap
from motulator.grid.control._base import Measurements


# %%
@dataclass
class PLLStates:
    """State estimates."""

    w_g: float = 0.0
    theta_c: float = 0.0
    u_g: float = 0.0


@dataclass
class PLLOutputSignals:
    """Feedback signals for the control system."""

    i_c: complex = 0j
    u_c: complex = 0j
    u_g: float = 0.0  # Filtered
    u_g_meas: complex = 0j  # Measured
    theta_c: float = 0.0
    w_g: float = 0.0
    w_c: float = 0.0
    p_g: float = 0.0
    q_g: float = 0.0
    eps: float = 0.0


class PLL:
    """
    Phase-locked loop including the voltage-magnitude filtering.

    This class provides a simple frequency-tracking phase-locked loop. The magnitude of
    the measured PCC voltage is also filtered.

    Parameters
    ----------
    u_nom : float
        Nominal grid voltage (V), line-to-neutral peak value.
    w_nom : float
        Nominal grid angular frequency (rad/s).
    alpha_pll : float
        PLL frequency-tracking bandwidth (rad/s).

    """

    def __init__(self, u_nom: float, w_nom: float, alpha_pll: float) -> None:
        self.k_p = 2 * alpha_pll
        self.k_i = alpha_pll**2
        self.state = PLLStates(w_g=w_nom, u_g=u_nom)

    def compute_output(
        self, u_c_ab: complex, i_c_ab: complex, u_g_meas_ab: complex
    ) -> PLLOutputSignals:
        """Output estimates and coordinate transformed quantities."""
        out = PLLOutputSignals(theta_c=self.state.theta_c, w_g=self.state.w_g)

        # Coordinate transformations
        out.i_c = exp(-1j * out.theta_c) * i_c_ab
        out.u_c = exp(-1j * out.theta_c) * u_c_ab
        out.u_g_meas = exp(-1j * out.theta_c) * u_g_meas_ab
        # Filtered voltage magnitude
        out.u_g = self.state.u_g

        # Error signal
        out.eps = out.u_g_meas.imag / self.state.u_g if self.state.u_g > 0.0 else 0.0

        # Angular speed of the coordinate system
        out.w_c = out.w_g + self.k_p * out.eps

        # Powers
        s_g = 1.5 * out.u_g * out.i_c.conjugate()
        out.p_g = s_g.real
        out.q_g = s_g.imag

        return out

    def update(self, T_s: float, out: PLLOutputSignals) -> None:
        """Update integral states."""
        self.state.theta_c += T_s * out.w_c
        self.state.theta_c = wrap(self.state.theta_c)
        self.state.w_g += T_s * self.k_i * out.eps
        self.state.u_g += T_s * self.k_p * (out.u_g_meas.real - self.state.u_g)


# %%
@dataclass
class References:
    """Reference signals for grid-following control."""

    T_s: float = 0.0
    u_c: complex = 0j
    i_c: complex = 0j
    p_g: float = 0.0
    q_g: float = 0.0
    u_dc: float | None = None


class OpenLoopController:
    """
    Open-loop controller.

    Parameters

        ----------
    u_nom : float, optional
        Nominal grid voltage (V), line-to-neutral peak value, defaults to
        `sqrt(2/3)*400`.
    w_nom : float, optional
        Nominal grid angular frequency (rad/s), defaults to 2*pi*50.
    alpha_pll : float, optional
        PLL frequency-tracking bandwidth (rad/s), defaults to 2*pi*20.
    T_s : float, optional
        Sampling period (s), defaults to 125e-6.

    """

    def __init__(
        self,
        i_max: float,
        L: float,
        alpha_c: float = 2 * pi * 400,
        alpha_i: float | None = None,
        u_nom: float = sqrt(2 / 3) * 400,
        w_nom: float = 2 * pi * 50,
        alpha_pll: float = 2 * pi * 20,
        T_s: float = 125e-6,
    ) -> None:
        # self.current_ctrl = CurrentController(L, alpha_c, alpha_i)
        self.pll = PLL(u_nom, w_nom, alpha_pll)
        # self.current_limiter = CurrentLimiter(i_max)
        self.T_s = T_s

    def get_feedback(self, u_c_ab: complex, meas: Measurements) -> PLLOutputSignals:
        """Get feedback signals."""
        fbk = self.pll.compute_output(u_c_ab, meas.i_c_ab, meas.u_g_ab)
        return fbk

    def compute_output(
        self, p_g_ref: float, q_g_ref: float, fbk: PLLOutputSignals
    ) -> References:
        """Compute references."""
        ref = References(T_s=self.T_s, p_g=p_g_ref, q_g=q_g_ref)

        # Compute the reference current
        ref.i_c = (ref.p_g - 1j * ref.q_g) / (1.5 * fbk.u_g)
        # ref.i_c = self.current_limiter(ref.i_c)

        # Compute the reference voltage
        # ref.u_c = self.current_ctrl.compute_output(ref.i_c, fbk.i_c, fbk.u_g)
        return ref

    def update(self, ref: References, fbk: PLLOutputSignals) -> None:
        """Update states."""
        # self.current_ctrl.update(ref.T_s, fbk.u_c, fbk.w_c)
        self.pll.update(ref.T_s, fbk)

    def post_process(self, ts: TimeSeries) -> None:
        """Post-process controller signals."""
