from statistics import mean
import simpy
import random
import pandas as pd
import numpy as np
import math
from utils import *
from parameters import *

class Patient:
    def __init__(self, p_id) -> None:
        self.p_id = p_id
        self.time_in_system = 0
        self.params = Params()

    def set_priority(self):
        # set priority according to weighted random choices - most are moderate in priority
        # self.priority = random.choices([1, 2, 3, 4, 5], [0.1, 0.2, 0.4, 0.2, 0.1])[0]
        priority_distribution = DiscreteNormal(self.params.mean_priority, self.params.stdev_priority,1,5,1)
        self.priority = priority_distribution.sample()[0]

    def set_outcome(self):
        # decision tree - if priority 5, go to Minor Injury Unit (MIU) or home. Higher priority go to AE
        if self.priority <5:
            self.triage_outcome = 'main'
            self.lab_outcome = random.choices(['lab', 'no lab'], [self.params.p_main_lab, 1-self.params.p_main_lab])[0]
            self.home_outcome = random.choices([True, False], [1-self.params.p_ed, self.params.p_ed])[0]
        elif self.priority == 5: # of those who are priority 5, 20% will go home with advice, 80% go to 'MIU'
            self.triage_outcome = 'fast'
            self.lab_outcome_outcome = random.choices(['lab', 'no lab'], [self.params.p_fast_lab, 1-self.params.p_fast_lab])[0]
            self.home_outcome = True

class AEDepartment:
    def __init__(self) -> None:
        self.env = simpy.Environment()
        self.params = Params()
        self.patient_counter = 0
        # set beds, docs and nurse as priority resources - urgent patients get seen first
        self.doc_main = simpy.PriorityResource(self.env, capacity=self.params.number_docs_main)
        self.nurse_main = simpy.PriorityResource(self.env, capacity=self.params.number_docs_main)
        self.beds = simpy.PriorityResource(self.env, capacity=self.params.number_of_labs)
        # set docs and nurse as normal resources - all FIFO
        self.doc_fast = simpy.Resource(self.env, capacity=self.params.number_docs_fast)
        self.nurse_fast = simpy.Resource(self.env, capacity=self.params.number_docs_fast)

    def patient_arrival(self):
        while True:
            self.patient_counter += 1

            # create class of AE patient and give ID
            patient = Patient(self.patient_counter)

            # simpy runs the attend ED methods
            self.env.process(self.attend_ae(patient))

            # Randomly sample the time to the next patient arriving to ae.  
            # The mean is stored in the g class.
            sampled_interarrival = random.expovariate(1.0 / self.params.mean_interarrival)

            # Freeze this function until that time has elapsed
            yield self.env.timeout(sampled_interarrival)

if __name__ == "__main__":
    patient = Patient(1)
    patient.set_priority()
    patient.set_outcome()
    for var_name, var_value in vars(patient).items():
        print(f"{var_name}: {var_value}")

