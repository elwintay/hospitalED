# Hospital Emergency Department Simulation and Analysis

## Overview of the Simulation Model

The simulation model aims to replicate the patient flow through an emergency department (ED) using the SimPy library. It consists of distinct components such as triage, consultations, lab tests, and bed assignments, each managed by separate classes and processes.

## Components of the Simulation Model

1. **Parameters Configuration**:
   - **Deterministic and Non-Deterministic Parameters**: The model uses predefined parameters such as the number of doctors, nurses, and beds, along with patient arrival rates, service times, and outcomes, which are set in the `Params` class.

2. **Entities**:
   - **Patient Class**: Represents each patient in the system, holding attributes like `p_id`, `arrival_time`, wait times for triage, consultation, lab, and bed, and the outcome of their visit.

3. **Resource Management**:
   - **SimPy Resources**: Each stage (triage, consultation, lab tests, and bed assignment) is managed by resources that control access based on availability. 
     - For example, the triage process is handled by the `Triage` class using `simpy.Resource`, while main consultation and lab processes may use `simpy.PriorityResource` to prioritize patients based on their urgency.

4. **Patient Flow**:
   - **Patient Generation**: A `patient_generator` function simulates the arrival of patients at the ED at specified intervals, creating new `Patient` instances and adding them to the triage queue.
   - **Triage Process**:
     - Patients are assigned to triage, where they are prioritized, and their outcomes (fast or main consultation) are determined based on the results of the triage process.
   - **Consultation Process**:
     - Depending on the triage outcome, patients are added to either the `FastConsultation` or `MainConsultation` queues.
     - Each consultation has a defined service time, which is simulated using log-normal distributions.

5. **Lab Tests and Bed Assignments**:
   - Patients may require lab tests, which are handled in the `FastLab` or `MainLab` classes, depending on their consultation path.
   - After consultation and lab tests, patients may be assigned a bed if necessary, using the `BedAssignment` class.

6. **Data Collection**:
   - Throughout the simulation, data on each patient's journey (wait times, finished times) is collected and stored in a dataset. This dataset is later saved as a CSV file for analysis.

## Simulation Execution

1. **Initialization**: The simulation initializes multiple runs as defined in the `Params` class. For each run:
   - Sets up the simulation environment and all necessary resources.
   - Starts the patient generator process.

2. **Simulation Duration**: The environment runs for a specified duration, including a warm-up period to allow the system to stabilize before recording data.

3. **Result Compilation**: After each run, the dataset is aggregated and saved to a CSV file for later analysis.

# Prerequisites

Before proceeding, ensure that you have **Docker** and **Docker Compose** installed on your system. If you do not have them installed, follow the official installation guides below:

- **[Install Docker](https://docs.docker.com/get-docker/)**
- **[Install Docker Compose](https://docs.docker.com/compose/install/)**

## Verify Docker Installation

To check if Docker is installed, run the following command:

```bash
docker --version
```


## Step 1: Clone the Project Repository

To start, clone the project repository by running the following command in your terminal:

```bash
git clone https://github.com/elwintay/hospitalED.git
```

## Step 2: Navigate to the Project Directory

Once the repository is cloned, navigate into the project folder with the following command:
```bash
cd hospitalED
```

## Step 3: Build and Start the Docker Container

To build the Docker image and start the services, run this command:
```bash
docker-compose up -d
```

## Step 4: Verify the Running Containers

To confirm that the containers are up and running, use this command:
```bash
docker ps
```

## Step 5: Access the Running Container

You will need to interact with a running container to generate the simulated datasets. Use this command to open an interactive shell session inside the container:
```bash
docker exec -it hospitaled-hospitalemergency-1 /bin/bash
```

## Step 6: Run simulation and generate datasets

To run simulation and generate datasets, use this command in the interactive shell session inside the container:
```bash
python main.py
```

## Step 7: Hospital Emergency Analysis

To read my analysis on the simulated data, please click on the link below:
- **[Hospital Emergency Department Simulation and Optimisation Analysis](https://colab.research.google.com/drive/1_d5y_5236gpTsZXno_UBdq-Equ69eRvh?usp=sharing)**