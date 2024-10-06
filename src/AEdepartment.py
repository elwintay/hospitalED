from entities import Patient
from statistics import mean
import simpy
import random
import pandas as pd
import numpy as np
import math
from utils import *
from parameters import Params
from dataset import Dataset

# Set a seed for reproducibility
random.seed(42)

class Triage:
    def __init__(self, env, fast_consultation, main_consultation):
        self.env = env
        self.params = Params()
        self.queue = []
        self.fast_consultation = fast_consultation
        self.main_consultation = main_consultation
        self.triage_resource = simpy.Resource(env, self.params.number_triage)

    def add_patient(self, patient):
        patient.set_priority()
        patient.set_outcome()
        self.queue.append(patient)
        print(f"Patient {patient.p_id} is queued at {self.env.now}.")
        # Start attending to this patient if there is capacity
        if len(self.queue) == 1:
            self.env.process(self.attend_patient(patient))

    def attend_patient(self, patient):
        with self.triage_resource.request() as request:
            
            yield request
            wait_start_time = self.env.now

            # Simulate time taken to attend to the patient
            lognorm = Lognormal(mean=self.params.mean_triage, stdev=self.params.stdev_triage)
            service_time = lognorm.sample()
            yield self.env.timeout(service_time)

            # Calculate wait time
            patient.triage_wait_time = wait_start_time - patient.arrival_time
            patient.finished_triage_time = self.env.now
            print(f"Patient {patient.p_id} finished triage {self.env.now} after waiting {patient.triage_wait_time} time units at the triage.")

        # Add patient to consultation queue
        main_queue_length = len(self.main_consultation.queue)
        fast_queue_length = len(self.fast_consultation.queue)
        print(main_queue_length, fast_queue_length)
        if patient.triage_outcome == 'fast':
            if fast_queue_length <= main_queue_length:
                print("FAST CONSULT")
                self.fast_consultation.add_patient(patient)
            else:
                print("MAIN CONSULT")
                self.main_consultation.add_patient(patient)
        else:
            print("MAIN CONSULT")
            self.main_consultation.add_patient(patient)
            
        # Finish attending and move to the next patient if available
        self.queue.pop(0)

        if self.queue:
            next_patient = self.queue[0]
            yield self.env.process(self.attend_patient(next_patient))

class FastConsultation:
    def __init__(self, env, fast_lab, dataset):
        self.env = env
        self.params = Params()
        self.queue = []
        self.fast_lab = fast_lab
        self.consultation_resource = simpy.Resource(env, self.params.number_docs_fast)
        self.dataset = dataset

    def add_patient(self, patient):
        self.queue.append(patient)
        print(f"Patient {patient.p_id} added to consultation queue at {self.env.now}.")

        # Start attending to this patient if there is capacity
        if len(self.queue) == 1:
            self.env.process(self.consult_patient(patient))

    def consult_patient(self, patient):
        with self.consultation_resource.request() as request:
            yield request  # Wait for a spot in the consultation area
            wait_start_time = self.env.now
        
            # Simulate time taken to consult the patient
            lognorm = Lognormal(mean=self.params.mean_doc_consult_fast, stdev=self.params.stdev_doc_consult_fast)
            consultation_time = lognorm.sample()
            yield self.env.timeout(consultation_time)
            patient.consultation_wait_time = wait_start_time - patient.finished_triage_time
            patient.finished_consult_time = self.env.now

            print(f"Patient {patient.p_id} consulted FAST at {self.env.now} after waiting {patient.consultation_wait_time} time units after triage.")
        
        if patient.lab_outcome == 'lab':
            print("FAST LAB")
            self.fast_lab.add_patient(patient)
        else:
            self.dataset.patient_list.append(patient)

        # Finish consulting and move to the next patient if available
        self.queue.pop(0)

        if self.queue:
            next_patient = self.queue[0]
            yield self.env.process(self.consult_patient(next_patient))

class MainConsultation:
    def __init__(self, env, main_lab, bed, dataset):
        self.env = env
        self.params = Params()
        self.queue = []
        self.main_lab = main_lab
        self.bed = bed
        self.consultation_resource = simpy.PriorityResource(env, self.params.number_docs_main)
        self.dataset = dataset

    def add_patient(self, patient):
        self.queue.append(patient)
        print(f"Patient {patient.p_id} added to consultation queue at {self.env.now}.")

        # Start attending to this patient if there is capacity
        if len(self.queue) == 1:
            self.env.process(self.consult_patient(patient))

    def consult_patient(self, patient):
        with self.consultation_resource.request(priority=patient.priority) as request:
            yield request  # Wait for a spot in the consultation area
            wait_start_time = self.env.now
        
            # Simulate time taken to consult the patient
            lognorm = Lognormal(mean=self.params.mean_doc_consult_main, stdev=self.params.stdev_doc_consult_main)
            consultation_time = lognorm.sample()
            yield self.env.timeout(consultation_time)
            patient.consultation_wait_time = wait_start_time - patient.finished_triage_time
            patient.finished_consult_time = self.env.now

            print(f"Patient {patient.p_id} consulted MAIN at {self.env.now} after waiting {patient.consultation_wait_time} time units after triage.")

        if patient.lab_outcome == 'lab':
            print("MAIN LAB")
            self.main_lab.add_patient(patient)
        else:
            if patient.bed_outcome:
                print("BED FROM CONSULT")
                self.bed.add_patient(patient)
            else:
                self.dataset.patient_list.append(patient)

        # Finish consulting and move to the next patient if available
        self.queue.pop(0)

        if self.queue:
            next_patient = self.queue[0]
            yield self.env.process(self.consult_patient(next_patient))

class FastLab:
    def __init__(self, env, dataset):
        self.env = env
        self.params = Params()
        self.queue = []
        self.lab_resource = simpy.Resource(env, self.params.number_nurses_fast)
        self.dataset = dataset

    def add_patient(self, patient):
        self.queue.append(patient)
        print(f"Patient {patient.p_id} added to FAST lab queue at {self.env.now}.")

        # Start attending to this patient if there is capacity
        if len(self.queue) == 1:
            self.env.process(self.lab_patient(patient))

    def lab_patient(self, patient):
        with self.lab_resource.request() as request:
            yield request  # Wait for a spot in the consultation area
            wait_start_time = self.env.now
        
            # Simulate time taken to consult the patient
            lognorm = Lognormal(mean=self.params.mean_lab_fast, stdev=self.params.stdev_lab_fast)
            lab_time = lognorm.sample()
            yield self.env.timeout(lab_time)
            patient.lab_wait_time = wait_start_time - patient.finished_consult_time
            patient.finished_lab_time = self.env.now

            print(f"Patient {patient.p_id} finished lab FAST at {self.env.now} after waiting {patient.lab_wait_time} time units after consultation.")

        # Finish consulting and move to the next patient if available
        self.dataset.patient_list.append(patient)
        self.queue.pop(0)

        if self.queue:
            next_patient = self.queue[0]
            yield self.env.process(self.lab_patient(next_patient))

class MainLab:
    def __init__(self, env, bed, dataset):
        self.env = env
        self.params = Params()
        self.queue = []
        self.bed = bed
        self.lab_resource = simpy.PriorityResource(env, self.params.number_nurses_fast)
        self.dataset = dataset

    def add_patient(self, patient):
        self.queue.append(patient)
        print(f"Patient {patient.p_id} added to MAIN lab queue at {self.env.now}.")

        # Start attending to this patient if there is capacity
        if len(self.queue) == 1:
            self.env.process(self.lab_patient(patient))

    def lab_patient(self, patient):
        with self.lab_resource.request(priority=patient.priority) as request:
            yield request  # Wait for a spot in the consultation area
            wait_start_time = self.env.now
        
            # Simulate time taken to consult the patient
            lognorm = Lognormal(mean=self.params.mean_lab_main, stdev=self.params.stdev_lab_main)
            lab_time = lognorm.sample()
            yield self.env.timeout(lab_time)
            patient.lab_wait_time = wait_start_time - patient.finished_consult_time
            patient.finished_lab_time = self.env.now

            print(f"Patient {patient.p_id} finished lab MAIN at {self.env.now} after waiting {patient.lab_wait_time} time units after consultation.")

        if patient.bed_outcome:
            print("BED FROM LAB")
            self.bed.add_patient(patient)
        else:
            self.dataset.patient_list.append(patient)

        # Finish consulting and move to the next patient if available
        self.queue.pop(0)

        if self.queue:
            next_patient = self.queue[0]
            yield self.env.process(self.lab_patient(next_patient))

class BedAssignment:
    def __init__(self, env, dataset):
        self.env = env
        self.params = Params()
        self.queue = []
        self.bed_resource = simpy.PriorityResource(env, self.params.number_of_beds)
        self.dataset = dataset

    def add_patient(self, patient):
        self.queue.append(patient)
        print(f"Patient {patient.p_id} added to bed queue at {self.env.now}.")

        # Start attending to this patient if there is capacity
        if len(self.queue) == 1:
            self.env.process(self.bed_patient(patient))

    def bed_patient(self, patient):
        with self.bed_resource.request(priority=patient.priority) as request:
            yield request  # Wait for a spot in the consultation area
            wait_start_time = self.env.now
        
            # Simulate time taken to consult the patient
            bed_time = random.expovariate(1.0 / params.mean_bed_time)
            yield self.env.timeout(bed_time)
            if patient.lab_outcome == 'lab':
                patient.bed_wait_time = wait_start_time - patient.finished_lab_time
            else:
                patient.bed_wait_time = wait_start_time - patient.finished_consult_time

            print(f"Patient {patient.p_id} finished staying in bed at {self.env.now} after waiting {patient.bed_wait_time} time units after consultation.")

        # Finish consulting and move to the next patient if available
        self.dataset.patient_list.append(patient)
        self.queue.pop(0)
        

        if self.queue:
            next_patient = self.queue[0]
            yield self.env.process(self.bed_patient(next_patient))


def patient_generator(env, params, triage):
    patient_id = 1
    while True:
        arrival_time = env.now
        patient = Patient(patient_id, arrival_time)
        triage.add_patient(patient)
        patient_id += 1

        # Simulate inter-arrival time
        yield env.timeout(random.expovariate(1.0 / params.mean_interarrival))

if __name__ == "__main__":
    params = Params()
    run_df_list = []
    for run in range(params.number_of_runs):
        # Setting up the simulation
        dataset = Dataset()
        env = simpy.Environment()
        
        warm_up = params.warm_up
        sim_duration = params.sim_duration
        runs = params.number_of_runs
        bed = BedAssignment(env, dataset)
        fast_lab = FastLab(env, dataset)
        main_lab = MainLab(env, bed, dataset)
        fast_consultation = FastConsultation(env, fast_lab, dataset)
        main_consultation = MainConsultation(env, main_lab, bed, dataset)
        triage = Triage(env, fast_consultation, main_consultation)
        env.process(patient_generator(env, params, triage))

        # Run the simulation
        env.run(until=warm_up + sim_duration)
        run_df_list.append(dataset.get_patients_df())
    print(run_df_list[0])

