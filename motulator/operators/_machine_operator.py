from abc import ABC, abstractmethod
from motulator.model._machine_models import InductionMachine, InductionMachineInvGamma

class MachineOperator(ABC):
    
    @abstractmethod
    def calculate_currents(self):
        pass
    
    @abstractmethod
    def f(self):
        pass
    
    @abstractmethod
    def measure_phase_currents(self):
        pass



class InductionMachineOperator(MachineOperator):
    
    def calculate_currents(self, machine: InductionMachine):
        """
        Compute the stator and rotor currents.

        Parameters
        ----------
        psi_ss : complex
            Stator flux linkage (Vs).
        psi_rs : complex
            Rotor flux linkage (Vs).

        Returns
        -------
        i_ss : complex
            Stator current (A).
        i_rs : complex
            Rotor current (A).

        """
        return 
    
    
    def f(self) -> str:
        return "derivative"
    
    def measure_phase_currents(self) -> str:
        return "Measure currents"
    
    def calculate_gamma(self, L_M, L_sgm) -> float:
        """
        Calculate the magnetic coupling factor
        """
        return L_M/(L_M + L_sgm)

    def convert_to_gamma_parameters(self, inv_gamma: InductionMachineInvGamma) -> InductionMachine:
        """
        Convert the inverse-Γ parameters to the Γ parameters
        """
        gamma = self.calculate_gamma(inv_gamma.L_M, inv_gamma.L_sgm)
        return InductionMachine(inv_gamma.n_p, inv_gamma.R_s, 
                                inv_gamma.R_s/gamma**2, inv_gamma.L_sgm/gamma, 
                                inv_gamma.L_M + inv_gamma.L_sgm)