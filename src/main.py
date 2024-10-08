from entities import Patient
import simpy
import random
import pandas as pd
from utils import *
from parameters import Params
from dataset import Dataset
import heapq

# Set a seed for reproducibility
random.seed(42)

class Triage:
    def __init__(self, env, fast_consultation, main_consultation, params):
        self.env = env
        self.params = params
        self.queue = []
        self.fast_consultation = fast_consultation
        self.main_consultation = main_consultation
        self.triage_resource = simpy.Resource(env, self.params.number_triage)

    def add_patient(self, patient):
        patient.set_priority()
        patient.set_outcome()
        self.queue.append(patient)
        print(f"Patient {patient.p_id} is queued at {self.env.now}.")
        self.env.process(self.attend_patient(patient))

    def attend_patient(self, patient):
        with self.triage_resource.request() as request:
            
            yield request
            wait_start_time = self.env.now

            # Simulate time taken to attend to the patient
            lognorm = Lognormal(mean=self.params.mean_triage, stdev=self.params.stdev_triage)
            service_time = lognorm.sample()
            yield self.env.timeout(service_time)
            print(f"Time {self.env.now}: TRIAGE resource utilization {self.triage_resource.count}/{self.triage_resource.capacity}, Queue: {len(self.triage_resource.queue)}")

            # Calculate wait time
            patient.triage_wait_time = wait_start_time - patient.arrival_time
            patient.finished_triage_time = self.env.now
            print(f"Patient {patient.p_id} finished triage {self.env.now} after waiting {patient.triage_wait_time} time units at the triage.")
            

        # Add patient to consultation queue
        main_queue_length = len(self.main_consultation.queue)
        fast_queue_length = len(self.fast_consultation.queue)
        
        #Decision to go fast or main consult based on queue length
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
            
        # Finish attending
        self.queue.pop(0)


class FastConsultation:
    def __init__(self, env, fast_lab, dataset, params):
        self.env = env
        self.params = params
        self.queue = []
        self.fast_lab = fast_lab
        self.consultation_resource = simpy.Resource(env, self.params.number_docs_fast)
        self.dataset = dataset

    def add_patient(self, patient):
        self.queue.append(patient)
        print(f"Patient {patient.p_id} added to consultation queue at {self.env.now}.")
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
            print(f"Time {self.env.now}: Resource utilization {self.consultation_resource.count}/{self.consultation_resource.capacity}, Queue: {len(self.consultation_resource.queue)}")

            print(f"Patient {patient.p_id} consulted FAST at {self.env.now} after waiting {patient.consultation_wait_time} time units after triage.")
        #decision to go lab
        if patient.lab_outcome == 'lab':
            print("FAST LAB")
            self.fast_lab.add_patient(patient)
        else:
            self.dataset.patient_list.append(patient)

        # Finish consulting
        self.queue.pop(0)

class MainConsultation:
    def __init__(self, env, main_lab, bed, dataset, params):
        self.env = env
        self.params = params
        self.queue = []
        self.main_lab = main_lab
        self.bed = bed
        self.consultation_resource = simpy.PriorityResource(env, self.params.number_docs_main)
        self.dataset = dataset

    def add_patient(self, patient):
        heapq.heappush(self.queue, (patient.priority, patient))
        print(f"Patient {patient.p_id} added to consultation queue at {self.env.now}.")
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
            print(f"Time {self.env.now}: Resource utilization {self.consultation_resource.count}/{self.consultation_resource.capacity}, Queue: {len(self.consultation_resource.queue)}")

            print(f"Patient {patient.p_id} consulted MAIN at {self.env.now} after waiting {patient.consultation_wait_time} time units after triage.")

        # Decision to go lab or get bedded or go home
        if patient.lab_outcome == 'lab':
            print("MAIN LAB")
            self.main_lab.add_patient(patient)
        else:
            if patient.bed_outcome:
                print("BED FROM CONSULT")
                self.bed.add_patient(patient)
            else:
                self.dataset.patient_list.append(patient)

        # Finish consulting
        self.queue.pop(0)

class FastLab:
    def __init__(self, env, dataset, params):
        self.env = env
        self.params = params
        self.queue = []
        self.lab_resource = simpy.Resource(env, self.params.number_nurses_fast)
        self.dataset = dataset

    def add_patient(self, patient):
        self.queue.append(patient)
        print(f"Patient {patient.p_id} added to FAST lab queue at {self.env.now}.")
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
            print(f"Time {self.env.now}: FAST LAB Resource utilization {self.lab_resource.count}/{self.lab_resource.capacity}, Queue: {len(self.lab_resource.queue)}")

            print(f"Patient {patient.p_id} finished lab FAST at {self.env.now} after waiting {patient.lab_wait_time} time units after consultation.")

        # Finish lab, output the patient
        self.dataset.patient_list.append(patient)
        self.queue.pop(0)

class MainLab:
    def __init__(self, env, bed, dataset, params):
        self.env = env
        self.params = params
        self.queue = []
        self.bed = bed
        self.lab_resource = simpy.PriorityResource(env, self.params.number_nurses_main)
        self.dataset = dataset

    def add_patient(self, patient):
        heapq.heappush(self.queue, (patient.priority, patient))
        print(f"Patient {patient.p_id} added to MAIN lab queue at {self.env.now}.")
        self.env.process(self.lab_patient(patient))

    def lab_patient(self, patient):
        with self.lab_resource.request(priority=patient.priority) as request:
            yield request  # Wait for a spot in the lab area
            wait_start_time = self.env.now
        
            # Simulate time taken to lab the patient
            lognorm = Lognormal(mean=self.params.mean_lab_main, stdev=self.params.stdev_lab_main)
            lab_time = lognorm.sample()
            yield self.env.timeout(lab_time)
            patient.lab_wait_time = wait_start_time - patient.finished_consult_time
            patient.finished_lab_time = self.env.now
            print(f"Time {self.env.now}: MAIN LAB Resource utilization {self.lab_resource.count}/{self.lab_resource.capacity}, Queue: {len(self.lab_resource.queue)}")

            print(f"Patient {patient.p_id} finished lab MAIN at {self.env.now} after waiting {patient.lab_wait_time} time units after consultation.")

        if patient.bed_outcome:
            print("BED FROM LAB")
            self.bed.add_patient(patient)
        else:
            self.dataset.patient_list.append(patient)

        # Finished lab
        self.queue.pop(0)

class BedAssignment:
    def __init__(self, env, dataset, params):
        self.env = env
        self.params = params
        self.queue = []
        self.bed_resource = simpy.PriorityResource(env, self.params.number_of_beds)
        self.dataset = dataset

    def add_patient(self, patient):
        heapq.heappush(self.queue, (patient.priority, patient))
        print(f"Patient {patient.p_id} added to bed queue at {self.env.now}.")
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
            patient.finished_bed_time = self.env.now
            print(f"Time {self.env.now}: Resource utilization {self.bed_resource.count}/{self.bed_resource.capacity}, Queue: {len(self.bed_resource.queue)}")

            print(f"Patient {patient.p_id} finished staying in bed at {self.env.now} after waiting {patient.bed_wait_time} time units after consultation.")

        # Finish consulting and move to the next patient if available
        self.dataset.patient_list.append(patient)
        self.queue.pop(0)


def patient_generator(env, params, triage):
    patient_id = 1
    while True:
        arrival_time = env.now
        patient = Patient(patient_id, arrival_time)
        triage.add_patient(patient)
        patient_id += 1

        # Simulate inter-arrival time
        yield env.timeout(random.expovariate(1.0 / params.mean_interarrival))

def run_simulator(params, save_file_name):
    #Setup for current patient load
    run_df_list = []
    for run in range(params.number_of_runs):
        # Setting up the simulation
        dataset = Dataset(params)
        env = simpy.Environment()
        warm_up = params.warm_up
        sim_duration = params.sim_duration
        bed = BedAssignment(env, dataset, params)
        fast_lab = FastLab(env, dataset, params)
        main_lab = MainLab(env, bed, dataset, params)
        fast_consultation = FastConsultation(env, fast_lab, dataset, params)
        main_consultation = MainConsultation(env, main_lab, bed, dataset, params)
        triage = Triage(env, fast_consultation, main_consultation, params)
        env.process(patient_generator(env, params, triage))

        # Run the simulation
        env.run(until=warm_up + sim_duration)
        curr_dataset = dataset.get_patients_df()
        curr_dataset['run'] = [run]*len(curr_dataset)
        run_df_list.append(curr_dataset)
    full_data = pd.concat(run_df_list)
    full_data.to_csv(f'data/{save_file_name}.csv', index=False)


if __name__ == "__main__":
    #Run with original settings
    params = Params()
    run_simulator(params, "simulated_ED_data_10min")
    # Run with mean_interarrival of 9min
    params = Params()
    params.mean_interarrival = 9
    run_simulator(params, "simulated_ED_data_9min")
    # Run with number_triage increase to 2 with mean_interarrival of 9min
    params = Params()
    params.mean_interarrival = 9
    params.number_triage = 2
    run_simulator(params, "simulated_ED_data_9min_number_triage_2")
    # Run with number_triage increase to 2 with mean_interarrival of 9min, with 3 main doctors, 2 beds
    params = Params()
    params.mean_interarrival = 9
    params.number_triage = 2
    params.number_docs_main = 3
    params.number_nurses_main = 2
    params.number_of_beds = 2
    run_simulator(params, "simulated_ED_data_9min_full_optimised")
    
    

