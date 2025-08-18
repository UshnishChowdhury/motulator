"""
Continuous-time models for current-source converters.

A three-phase current-source converter with optional inductive DC-bus dynamics is
modeled, supplied from a stiff grid. Complex space vectors are used also for duty ratios
and switching states, wherever applicable.

"""

from dataclasses import InitVar, dataclass, field
from typing import Any, Callable

import numpy as np

from motulator.common.model._base import Subsystem
from motulator.common.utils._utils import empty_array


# %%
@dataclass
class Inputs:
    """Input variables."""

    q_c_ab: complex = 0j
    u_c_ab: complex = 0j
    u_dc: float | Callable[[float], float] | None = None


@dataclass
class Outputs:
    """Output variables for interconnection."""

    i_c_ab: complex
    i_dc: float


class CurrentSourceConverter(Subsystem):
    """
    Lossless three-phase current-source converter with constant DC-bus current.

    Parameters
    ----------
    i_dc : float
        DC-bus current (A).

    """

    def __init__(self, i_dc: float) -> None:
        self.i_dc = i_dc
        self.inp: Inputs = Inputs()
        self.out: Outputs = Outputs(i_c_ab=0j, i_dc=i_dc)
        self.state = None
        self._history = None

    def set_external_dc_voltage(self, u_dc: Callable[[float], float]) -> None:
        """Set external DC voltage (V)."""
        raise NotImplementedError

    def compute_internal_dc_voltage(self, inp: Any) -> Any:
        """Compute the internal DC voltage (V)."""
        return 1.5 * np.real(inp.q_c_ab * np.conj(inp.u_c_ab))

    def set_outputs(self, t: float) -> None:
        """Set output variables."""
        self.out.i_c_ab = self.inp.q_c_ab * self.out.i_dc

    def meas_dc_current(self) -> float:
        """Measure converter DC-bus current (A)."""
        return self.out.i_dc

    def rhs(self, t: float) -> list[complex]:
        """Default empty implementation."""
        return []

    def create_time_series(
        self, t: np.ndarray
    ) -> tuple[str, "CurrentSourceConverterTimeSeries"]:
        """Create time series."""
        return "converter", CurrentSourceConverterTimeSeries(t, self)


@dataclass
class CurrentSourceConverterTimeSeries[T: CurrentSourceConverter]:
    """Continuous time series."""

    t: InitVar[np.ndarray]
    subsystem: InitVar[T]
    i_dc: np.ndarray = field(default_factory=empty_array)
    q_c_ab: np.ndarray = field(default_factory=empty_array)
    i_c_ab: np.ndarray = field(default_factory=empty_array)
    u_c_ab: np.ndarray = field(default_factory=empty_array)
    u_dc_int: np.ndarray = field(default_factory=empty_array)

    def __post_init__(self, t: np.ndarray, subsystem: T) -> None:
        self.i_dc = np.full(np.size(t), subsystem.i_dc)

    def compute_zoh_input_derived_signals(self, t: np.ndarray, subsystem: T) -> None:
        """Compute zero-order hold derived signals."""
        self.i_c_ab = self.q_c_ab * self.i_dc

    def compute_input_derived_signals(self, t: np.ndarray, subsystem: T) -> None:
        """Process input time series."""
        self.i_dc_int = subsystem.compute_internal_dc_voltage(self)


# %%
@dataclass
class InductiveDCBusCurrentSourceConverterStates:
    """State variables."""

    i_dc: float


@dataclass
class InductiveDCBusCurrentSourceConverterStateHistory:
    """State history."""

    i_dc: list[complex] = field(default_factory=list)


class InductiveDCBusCurrentSourceConverter(CurrentSourceConverter):
    """
    Lossless current-source converter with inductive DC-bus dynamics.

    Parameters
    ----------
    i_dc : float
        DC-bus current (A).
    L_dc : float
        DC-bus inductance (H).

    """

    def __init__(self, i_dc: float, L_dc: float) -> None:
        super().__init__(i_dc)
        self.L_dc = L_dc
        self.state: InductiveDCBusCurrentSourceConverterStates = (
            InductiveDCBusCurrentSourceConverterStates(self.i_dc)
        )
        self._history: InductiveDCBusCurrentSourceConverterStateHistory = (
            InductiveDCBusCurrentSourceConverterStateHistory()
        )

    def set_external_dc_voltage(self, u_dc: Callable[[float], float]) -> None:
        """Set external DC voltage (V)."""
        self.inp.u_dc = u_dc

    def set_outputs(self, t: float) -> None:
        """Set output variables for interconnection."""
        self.out.i_dc = self.state.i_dc.real
        super().set_outputs(t)

    def rhs(self, t: float) -> list[complex]:
        """Compute state derivatives for DC-bus current."""
        if callable(self.inp.u_dc):
            u_dc = self.inp.u_dc(t)
        elif isinstance(self.inp.u_dc, (int, float)):
            u_dc = self.inp.u_dc
        else:
            u_dc = 0.0
        u_dc_int = self.compute_internal_dc_voltage(self.inp)
        d_i_dc = (u_dc - u_dc_int) / self.L_dc
        return [d_i_dc]

    def create_time_series(
        self, t: np.ndarray
    ) -> tuple[str, "InductiveDCBusCurrentSourceConverterTimeSeries"]:
        """Create time series from state list."""
        return "converter", InductiveDCBusCurrentSourceConverterTimeSeries(t, self)


@dataclass
class InductiveDCBusCurrentSourceConverterTimeSeries(
    CurrentSourceConverterTimeSeries[InductiveDCBusCurrentSourceConverter]
):
    """Continuous time series."""

    subsystem: InitVar[InductiveDCBusCurrentSourceConverter]

    def __post_init__(
        self, t: np.ndarray, subsystem: InductiveDCBusCurrentSourceConverter
    ) -> None:
        self.u_dc = np.array(subsystem._history.i_dc)
