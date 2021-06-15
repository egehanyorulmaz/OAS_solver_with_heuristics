from utils import *
from collections import defaultdict

def data_importer(order_number, tao_number, r_number, instance_number):

    dat_filename = f'Dataslack_{order_number}orders_Tao{tao_number}R{r_number}_{instance_number}_without_setup.dat'
    dat_filepath = f'project_data/{dat_filename}'

    datContent = [i.strip().split() for i in open(dat_filepath).readlines()]
    release_times = list_separator(datContent[1][0])
    processing_times = list_separator(datContent[4][0])
    revenues = list_separator(datContent[7][0])
    due_dates = list_separator(datContent[10][0])
    deadlines = list_separator(datContent[13][0])
    tardiness_penalty_costs = list_separator(datContent[16][0])

    JOB_ATTRIBUTES = defaultdict()

    for job_number in range(len(release_times)):
        JOB_ATTRIBUTES[job_number] = {'release_time': release_times[job_number],
                                      'processing_times': processing_times[job_number],
                                      'revenues': revenues[job_number],
                                      'due_dates': due_dates[job_number],
                                       'deadlines': deadlines[job_number],
                                      'tardiness_penalty_costs': tardiness_penalty_costs[job_number],
                                      'slack_time': due_dates[job_number] - release_times[job_number] - processing_times[job_number]
                                      }
    return JOB_ATTRIBUTES



def calculate_weighted_tardiness(completion_times, due_dates, deadlines, weights):
    weighted_tardiness = 0
    for completion_time, due_date, deadline, weight in zip(completion_times, due_dates, deadlines, weights):
        if due_date < completion_time:
            weighted_tardiness += weight * (completion_time - due_date)

    return weighted_tardiness




if __name__ == '__main__':
    data_dictionary = data_importer(10,1,5,6)

    print('a')