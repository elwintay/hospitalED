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
    number_triage = 1
    number_docs_fast = 1
    number_nurses_fast = 1
    number_docs_main = 2
    number_nurses_main = 2
    number_of_beds = 1

    """
    Non-deterministic parameters
    """
    # Patient interarrival time (exponential distribution)
    mean_interarrival = 10
    # Patient time taken at triage (lognormal distribution)
    mean_triage = 10
    stdev_triage = 3
    # Patient time taken to consult a doctor for Main (lognormal distribution)
    mean_doc_consult_main = 20 
    stdev_doc_consult_main = 3
    # Patient time taken to consult a doctor for Fast (lognormal distribution)
    mean_doc_consult_fast = 15
    stdev_doc_consult_fast = 3
    # Patient probability for lab for Fast (binomial distribution)
    p_fast_lab = 0.1
    # Patient probability for lab for Main (binomial distribution)
    p_main_lab = 0.4
    # Patient time taken for lab by nurse for Main (lognormal distribution)
    mean_lab_main = 45
    stdev_lab_main = 10
    # Patient time taken for lab by nurse for Fast (lognormal distribution)
    mean_lab_fast = 15
    stdev_lab_fast = 10
    # Patient probability to remain in ED (binomial distribution)
    p_ed = 0.2
    # Patient stay for bed (exponential distribution)
    mean_bed_time = 120