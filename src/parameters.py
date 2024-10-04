class Params:
    """
    Simulation metrics
    """
    warm_up = 120
    sim_duration = 480
    number_of_runs = 250

    """
    Deterministic parameters
    """
    number_docs_fast = 1
    number_nurses_fast = 1
    number_docs_main = 3
    number_nurses_main = 3
    number_of_beds = 10

    """
    Non-deterministic parameters
    """
    # Patient interarrival time (exponential distribution)
    mean_interarrival = 5
    # Patient priority (Discrete Normal: see utils.py)
    mean_priority = 3
    stdev_priority = 1
    # Patient time taken at triage (lognormal distribution)
    mean_triage = 10
    stdev_triage = 5
    # Patient time taken to consult a doctor for Main (lognormal distribution)
    mean_doc_consult_main = 30
    stdev_doc_consult_main = 10
    # Patient probability for lab for Fast (binomial distribution)
    p_fast_lab = 0.1
    # Patient probability for lab for Main (binomial distribution)
    p_main_lab = 0.4
    # Patient time taken to consult a doctor for Fast (lognormal distribution)
    mean_doc_consult_fast = 20
    stdev_doc_consult_fast = 7
    # Patient time taken for lab by nurse for Main (lognormal distribution)
    mean_doc_consult = 30
    stdev_doc_consult = 10
    # Patient time taken for lab by nurse for Fast (lognormal distribution)
    mean_doc_consult = 10
    stdev_doc_consult = 3
    # Patient probability to remain in ED (binomial distribution)
    p_ed = 0.2
    # Patient stay for bed (exponential distribution)
    mean_bed_time = 90

    """
    Placeholders
    """
    # some placeholders used to track wait times for resources
    wait_triage = []
    wait_cubicle = []
    wait_doc_main = []
    wait_doc_fast = []