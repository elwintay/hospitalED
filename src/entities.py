from statistics import mean
import simpy
import random
import pandas as pd
import numpy as np
import math
from utils import *
from parameters import *

class Patient:
    def __init__(self, p_id, arrival_time) -> None:
        self.p_id = p_id
        self.arrival_time = arrival_time
        self.time_in_system = 0
        self.params = Params()

    def set_priority(self):
        priority_distribution = DiscreteNormal(self.params.mean_priority, self.params.stdev_priority,1,5,1)
        self.priority = priority_distribution.sample()[0]

    def set_outcome(self):
        # decision tree - if priority 5, go to Minor Injury Unit (MIU) or home. Higher priority go to AE
        if self.priority <3:
            self.triage_outcome = 'main'
            self.lab_outcome = random.choices(['lab', 'no lab'], [self.params.p_main_lab, 1-self.params.p_main_lab])[0]
            self.bed_outcome = random.choices([True, False], [1-self.params.p_ed, self.params.p_ed])[0]
        elif self.priority >= 3: # of those who are priority 5, 20% will go home with advice, 80% go to 'MIU'
            self.triage_outcome = 'fast'
            self.lab_outcome = random.choices(['lab', 'no lab'], [self.params.p_fast_lab, 1-self.params.p_fast_lab])[0]
            self.bed_outcome = True

    def __lt__(self, other):
        return self.priority < other.priority  # Compare based on priority


if __name__ == "__main__":
    patient = Patient(1,1)
    patient.set_priority()
    patient.set_outcome()
    for var_name, var_value in vars(patient).items():
        print(f"{var_name}: {var_value}")

