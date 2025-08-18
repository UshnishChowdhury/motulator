"""
LC filter model.

This module contains a continuous-time model for subsystems comprising a LC filter.
The model is implemented with space vectors in stationary coordinates.

"""

from dataclasses import InitVar, dataclass, field
from typing import Any

import numpy as np

from motulator.common.model import Subsystem, SubsystemTimeSeries
from motulator.common.utils._utils import complex2abc, empty_array


# %%
@dataclass
class Inputs:
    """AC filter inputs."""

    i_c_ab: complex = 0j
    e_g_ab: complex = 0j


# %%


@dataclass
class LCFilterStates:
    """LC filter states."""

    u_c_ab: complex = 0j
    i_g_ab: complex = 0j


@dataclass
class LCFilterOutputs:
    """Base class for outputs."""

    u_c_ab: complex
    i_g_ab: complex


@dataclass
class LCFilterStateHistory:
    """LC filter state history."""

    u_c_ab: list[complex] = field(default_factory=list)
    i_g_ab: list[complex] = field(default_factory=list)


class LCFilter(Subsystem):
    """
    Model of an LC filter and an inductive-resistive grid.

    An LC filter and an inductive-resistive grid impedance, between the converter and
    grid voltage sources, are modeled.

    Parameters
    ----------
    C_f : float
        Filter capacitance (F).
    L_g : float, optional
        Grid inductance (H), defaults to 0.
    R_g : float, optional
        Grid resistance (Ω), defaults to 0.
    u_f0_ab : complex, optional
        Initial value of the filter capacitor voltage (V), defaults to 0.
    """

    def __init__(
        self, C: float, L: float = 0.0, R_g: float = 0.0, u_f0_ab: complex = 0j
    ) -> None:
        self.C = C
        self.L = L
        self.R_g = R_g
        self.state: LCFilterStates = LCFilterStates(u_f0_ab, 0j)
        self.inp: Inputs = Inputs(0j, u_f0_ab)
        self.out: LCFilterOutputs = LCFilterOutputs(
            self.state.u_c_ab, self.state.i_g_ab
        )
        self._history: LCFilterStateHistory = LCFilterStateHistory()

    def pcc_voltage(self, state: Any, inp: Any) -> Any:
        """Compute the voltage at the point of common coupling (PCC)."""
        u_g_ab = inp.e_g_ab - self.R_g * state.i_g_ab
        return u_g_ab

    def set_outputs(self, t: float) -> None:
        """Set output variables."""
        state, out = self.state, self.out
        out.u_c_ab = state.u_c_ab
        out.i_g_ab = state.i_g_ab

    def rhs(self, t: float) -> list[complex]:
        """Compute the state derivatives."""
        state = self.state
        inp = self.inp

        # State equations
        d_u_c_ab = (inp.i_c_ab - state.i_g_ab) / self.C
        d_i_g_ab = (state.u_c_ab - inp.e_g_ab - self.R_g * state.i_g_ab) / self.L
        return [d_u_c_ab, d_i_g_ab]

    def meas_grid_currents(self) -> Any:
        """Measure the grid phase currents (A)."""
        return complex2abc(self.state.i_g_ab)

    def meas_capacitor_voltages(self) -> Any:
        """Measure the capacitor phase voltages (V)."""
        return complex2abc(self.state.u_c_ab)

    def create_time_series(self, t: np.ndarray) -> tuple[str, "LCFilterTimeSeries"]:
        """Create time series from state list."""
        return "ac_filter", LCFilterTimeSeries(t, self)


@dataclass
class LCFilterTimeSeries(SubsystemTimeSeries):
    """Continuous time series for AC filters."""

    t: InitVar[np.ndarray]
    subsystem: InitVar[LCFilter]
    # States
    u_c_ab: np.ndarray = field(default_factory=empty_array)
    i_g_ab: np.ndarray = field(default_factory=empty_array)
    # Inputs
    i_c_ab: np.ndarray = field(default_factory=empty_array)
    e_g_ab: np.ndarray = field(default_factory=empty_array)
    # Outputs
    u_g_ab: np.ndarray = field(default_factory=empty_array)

    def __post_init__(self, t: np.ndarray, subsystem: LCFilter) -> None:
        """Compute output time series from the states."""
        self.u_c_ab = np.array(subsystem._history.u_c_ab)
        self.i_g_ab = np.array(subsystem._history.i_g_ab)

    def compute_input_derived_signals(self, t: np.ndarray, subsystem: LCFilter) -> None:
        """Process input time series."""
        self.u_g_ab = subsystem.pcc_voltage(self, self)
