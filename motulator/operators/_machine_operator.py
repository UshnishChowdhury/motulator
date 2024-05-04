from abc import ABC, abstractmethod

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
    
    def calculate_currents(self) -> str:
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
        return "hello"
    
    
    def f(self) -> str:
        return "derivative"
    
    def measure_phase_currents(self) -> str:
        return "Measure currents"