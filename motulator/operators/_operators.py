from numpy import sqrt, pi
from motulator.model._base import NominalValues, BaseValues

class BaseOperations:
    
    def convert_to_peak_line_to_neutral(line_to_line: float) -> float:
        return sqrt(2/3)*line_to_line
    
    def convert_rms_to_peak_value(rms_value: float) -> float:
        return sqrt(2)*rms_value
    
    def calculate_angular_frequency(nominal_freq: float) -> float:
        return pi*nominal_freq
    
    def calculate_power_from_voltage_current(u: float, i:float) -> float:
        return (3/2)*u*i
    
    def calculate_flux_from_voltage_angular_freq(u: float, w: float) -> float:
        return u/w
    
    def calculate_impedance_from_voltage_current(u : float, i: float) -> float:
        return u/i
    
    def calculate_inductance_from_impedance_angular_freq(Z: float, w: float) -> float:
        return Z/w
    
    def calculate_torque_from_power_angular_freq(p: float, w: float, n_p: int) -> float:
        return n_p*p/w
    
    def get_base_values(nom_values: NominalValues) -> BaseValues:
        u = BaseOperations.convert_to_peak_line_to_neutral(nom_values.U_nom)
        i = BaseOperations.convert_rms_to_peak_value(nom_values.I_nom)
        w = BaseOperations.calculate_angular_frequency(nom_values.f_nom)
        psi = BaseOperations.calculate_flux_from_voltage_angular_freq(u, w)
        p = BaseOperations.calculate_power_from_voltage_current(u, i)
        Z = BaseOperations.calculate_impedance_from_voltage_current(u, i)
        L = BaseOperations.calculate_inductance_from_impedance_angular_freq(Z, w)
        tau = BaseOperations.calculate_torque_from_power_angular_freq(p, w, nom_values.n_p)
        return BaseValues(u, i, w, psi, p, Z, L, tau)