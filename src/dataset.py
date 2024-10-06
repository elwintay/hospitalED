import pandas as pd

class Dataset:
    def __init__(self):
        self.patient_list = []

    def get_patients_df(self):
        patient_dict_list = []
        for patient in self.patient_list:
            patient_dict = {}
            for var_name, var_value in vars(patient).items():
                if var_name != "params":
                    patient_dict[var_name] = var_value
            patient_dict_list.append(patient_dict)
            df = pd.DataFrame(patient_dict_list)
            df = df.sort_values(by='p_id')
        return df