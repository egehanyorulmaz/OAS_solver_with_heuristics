import random
import time

from funcs import data_importer, calculate_weighted_tardiness
from utils import symmetrical_difference_positions, element_exist_in_list

random.seed(25)


class Tabu:
    def __init__(self, num_orders, tabu_tenure, termination_for_not_improving, path_relinking_frequency,
                 path_relinking_requirement):
        self.all_solution = []

        # keeping track of the best solution
        self.best_solution = 0
        self.best_solution_iteration = 0
        self.best_solution_sequence = []
        self.best_solution_rejected_jobs = []

        self.tabu_search_improved_best = 0
        self.path_relinking_improved_best = 0

        self.iteration_number = 0
        self.candidate_solution = ''

        # tabu search parameters
        self.tabu_list = []
        self.tabu_tenure = tabu_tenure

        # path relinking parameters
        self.path_relinking_frequency = path_relinking_frequency  # iteration frequency to apply path_relinking
        self.path_relinking_requirement = path_relinking_requirement  # to satisfy potential improvement by avoiding already tried solutions

        self.termination_for_not_improving = termination_for_not_improving
        self.num_orders = num_orders
        self.job_desc_dict = ''

    # completion time of the orders should be calculated
    def calculate_statistics(self, print_rejected=True):
        """
        Calculate performance metrics of the current job sequence
        :param print_rejected: Boolean: to print reject jobs
        :return:
        """
        idx = 0
        time_elapsed = 0
        completiontimes = []
        deadlines = []
        duedates = []
        weights = []
        job_sequence = []
        rejected_jobs = []
        total_revenue = 0

        for job_number, job_info in self.candidate_solution.items():
            pre_time_elapse = time_elapsed
            if idx == 0:  # pass dummy order
                idx += 1
                continue
            else:
                if idx == 1:  # wait for first order's release_time
                    time_elapsed += job_info['release_time']
                    idx += 1

                if time_elapsed >= job_info['release_time']:  # if current job is already released
                    if time_elapsed + job_info['processing_times'] > job_info['deadlines']:
                        rejected_jobs.append(job_number)
                        if print_rejected:
                            print(f'Reject job {job_number}')
                        continue
                    else:
                        total_revenue += job_info['revenues']
                        time_elapsed += job_info['processing_times']

                else:  # if current job is not released at time_elapsed, then process must wait for it to be released.
                    if job_info['release_time'] + job_info['processing_times'] > job_info['deadlines']:  # reject job
                        if print_rejected:
                            print(f'Reject job {job_number}')
                        rejected_jobs.append(job_number)
                        continue
                    else:  # accept job
                        total_revenue += job_info['revenues']
                        time_elapsed = job_info['release_time'] + job_info['processing_times']

                # absolute time
                if pre_time_elapse != time_elapsed:
                    job_sequence.append(job_number)
                    completiontimes.append(time_elapsed)
                    deadlines.append(job_info['deadlines'])
                    duedates.append(job_info['due_dates'])
                    weights.append(job_info['tardiness_penalty_costs'])

        weighted_tardiness = calculate_weighted_tardiness(deadlines=deadlines,
                                                          due_dates=duedates,
                                                          completion_times=completiontimes,
                                                          weights=weights)

        profit = total_revenue - weighted_tardiness
        return job_sequence, completiontimes[
            len(completiontimes) - 1], weighted_tardiness, total_revenue, profit, rejected_jobs

    def neighbour_swap(self, i, k):
        """
        Performs one-opt operation on job orders. Selects the positioning to perform one-opt by random.
        :return:
        """

        job_orders = list(self.candidate_solution.keys())  # job sequence
        old_job_orders = job_orders.copy()

        if self.iteration_number == 2799:
            print('a')
            pass

        # TABU
        i_index = job_orders.index(i)  # position of first job
        k_index = job_orders.index(k)  # position of second job

        job_orders[i_index], job_orders[k_index] = job_orders[k_index], job_orders[i_index]

        self.candidate_solution = {k: self.candidate_solution[k] for k in job_orders}

    def objective_evaluation(self):

        iteration_statistics = self.calculate_statistics()
        self.all_solution.append({self.iteration_number: {'job_sequence': iteration_statistics[0],
                                                          'completion_time': iteration_statistics[1],
                                                          'weighted_tardiness': iteration_statistics[2],
                                                          'revenue': iteration_statistics[3],
                                                          'profit': iteration_statistics[4],
                                                          'rejected_jobs': iteration_statistics[5]}
                                  }
                                 )

        print('Current job sequence: ', iteration_statistics[0])
        print(f'\tRejected jobs are: {iteration_statistics[5]}')

        print(f'\tCompletion time: {iteration_statistics[1]}')
        print(f'\tWeighted tardiness: {iteration_statistics[2]}')
        print(f'\tTotal revenue: {iteration_statistics[3]}')
        print(f'\tProfit is: {iteration_statistics[4]}')

    def detect_best_solution(self):
        """
        Controls best solution found so far and save information about the solution as attributes
        :return:
        """

        for solution in self.all_solution:
            key = list(solution.keys())[0]
            value = list(solution.values())[0]
            if value['profit'] > self.best_solution:
                self.best_solution = value['profit']
                self.best_solution_iteration = key
                self.best_solution_sequence = value['job_sequence']
                self.best_solution_rejected_jobs = value['rejected_jobs']
                self.tabu_search_improved_best += 1

    def generate_first_solution(self):
        """
        Generetes starting solution of the problem
        :return:
        """
        order_dict = self.job_desc_dict.copy()

        order_dict = dict(sorted(order_dict.items(), key=lambda item: item[1]['slack_time']))
        return order_dict

    def swap_move_generator(self):
        """
        Recommends one-opt swapping moves
        :return: jobs to swap
        """
        (i, k) = random.sample(range(1, self.num_orders - 1), 2)  # order numbers are given for swapping
        return (i, k)

    # tabu search
    def tabu_check(self, i, k):
        """
        Controls whether swapping move is in tabu list
        """
        return (i, k) in self.tabu_list

    def tabu_update(self, i, k):
        """
        Inserts new swap to the tabu list
        :param i: latest accepted job 1
        :param k: latest accepted job 2
        :return:
        """
        if len(self.tabu_list) >= self.tabu_tenure:  # tabu list update
            self.tabu_list.pop(self.tabu_tenure - 1)
            self.tabu_list.insert(0, (i, k))
        else:
            self.tabu_list.insert(0, (i, k))

    def aspiration(self, i, k):
        """
        Controls whether the swapping moves can be allowed even though it is in tabu list.
        """
        job_sequence, completiontimes, weighted_tardiness, total_revenue, profit, rejected_jobs = self.calculate_statistics()
        if profit > self.best_solution:  # candidate solution improves the best solution. Therefore it can be avoided in tabu list
            return True
        else:
            return False

    def path_relinking(self, initial_solution, guiding_solution):
        """
        :param initial_solution: solution to move through guiding solution
        :param guiding_solution: sequence of the best solution so far
        :return: potentials moves suggested by path relinking to test
        """
        symmetric_difference = symmetrical_difference_positions(initial_solution, guiding_solution)

        swap_moves = []
        terminate = False
        iteration_count = 0
        last_inserting_iteration = 0

        while not terminate:
            # swap move generator. It suggest swapping moves that decreases the symmetrical difference between
            # initial solution and guiding solution
            first_position = random.choice(symmetric_difference)
            second_position = guiding_solution.index(initial_solution[first_position])

            if not element_exist_in_list(swap_moves, (first_position, second_position)):
                swap_moves.append((first_position, second_position))
                last_inserting_iteration = iteration_count

            if (len(swap_moves) == self.path_relinking_requirement) | (iteration_count - last_inserting_iteration > 10):
                # terminate generating candidate swap moves either if you had already filled as path_relinking_requirement
                # or couldnt find any moves for 10 iterations
                terminate = True

            iteration_count += 1

        terminate = False
        potential_moves = []
        for candidate_move in swap_moves:  # performs swapping operations and append new solutions to the list
            a, b = candidate_move
            initial_solution_temp = initial_solution.copy()
            initial_solution_temp[b], initial_solution_temp[a] = initial_solution_temp[a], initial_solution_temp[b]
            potential_moves.append(initial_solution_temp)

        return potential_moves

    def pick_same_rejected_sequence(self):
        """
        Loops over all candidates that stored as an attribute and returns the job sequence with the same
        jobs rejected.
        :return:
        """

        candidate_initial_solutions = []
        for solution in self.all_solution:  # appends job sequences with same rejected_jobs

            key = list(solution.keys())[0]
            value = list(solution.values())[0]

            candidate_solution_rejected = set(value['rejected_jobs'])
            best_solution_rejected = set(self.best_solution_rejected_jobs)

            if (len(candidate_solution_rejected.symmetric_difference(best_solution_rejected)) == 0) & \
                    (element_exist_in_list(candidate_initial_solutions, self.best_solution_sequence)):
                # same rejected jobs and not already appended to the list
                candidate_initial_solutions.append(value['job_sequence'])

        if len(candidate_initial_solutions) != 0:
            print('Initial solution is selected from list')
            random_selection = random.randint(0, len(candidate_initial_solutions) - 1)
            return candidate_initial_solutions[random_selection]
        else:
            print('Best solution is shuffled.')
            shuffled = random.sample(self.best_solution_sequence, len(self.best_solution_sequence))
            return shuffled

    def optimize(self):
        """

        Main function to run the optimization
        :return:
        """
        terminate = False
        # count of iterations with no improvement in sol
        noimprovementcount = 0
        print("Starting Tabu Search")
        # iterate until termination criteria is met
        self.candidate_solution = self.generate_first_solution()

        while not terminate:
            print(f'\nIteration no: {self.iteration_number}')

            if (self.iteration_number + 1) % self.path_relinking_frequency != 0:
                i, k = self.swap_move_generator()
                solution_in_tabu = self.tabu_check(i, k)
                self.neighbour_swap(i, k)

                if solution_in_tabu:  # aspiration control
                    if self.aspiration(i, k):
                        self.objective_evaluation()

                else:
                    self.objective_evaluation()
                    self.tabu_update(i, k)

                self.detect_best_solution()
                if self.iteration_number - self.best_solution_iteration > self.termination_for_not_improving:
                    terminate = True

                self.iteration_number += 1

            else:
                cache_last_candidate_solution = self.candidate_solution
                path_relinking_solution = self.pick_same_rejected_sequence()  # generates same job sequences with the same job numbers used.

                best_pr_solution = 0
                best_pr_sequence = list()

                while path_relinking_solution != self.best_solution_sequence:
                    solution_sequences = self.path_relinking(initial_solution=path_relinking_solution,
                                                             guiding_solution=self.best_solution_sequence)

                    best_inloop_pr_solution = 0
                    best_inloop_pr_sequence = list()

                    for solution_sequence in solution_sequences:  # iterate over solutions generated by steps of path relinking

                        self.candidate_solution = {k: self.candidate_solution[k] for k in solution_sequence}
                        job_sequence, completion_times, weighted_tardiness, total_revenue, profit, rejected_jobs = self.calculate_statistics(
                            print_rejected=False)

                        if profit > best_inloop_pr_solution:
                            best_inloop_pr_solution = profit
                            best_inloop_pr_sequence = solution_sequence

                    path_relinking_solution = best_inloop_pr_sequence.copy()

                    print(len(symmetrical_difference_positions(best_inloop_pr_sequence, self.best_solution_sequence)))

                    if best_inloop_pr_solution > best_pr_solution:
                        best_pr_solution = best_inloop_pr_solution
                        best_pr_sequence = best_inloop_pr_sequence.copy()

                if best_pr_solution > self.best_solution:
                    self.candidate_solution = cache_last_candidate_solution
                    self.best_solution = best_pr_solution
                    self.best_solution_sequence = best_pr_sequence
                    self.best_solution_iteration = self.iteration_number
                    self.iteration_number += 1
                    self.path_relinking_improved_best += 1
                else:
                    self.candidate_solution = cache_last_candidate_solution
                    self.iteration_number += 1


if __name__ == '__main__':
    # Data file parameters. Change to work on a different dataset.
    order_count = 50
    tao = 9  # increases complexity of the problem
    r = 9  # increases complexity of the problem
    instance = 7

    tabu_obj = Tabu(num_orders=order_count, tabu_tenure=150, termination_for_not_improving=2000,
                         path_relinking_frequency=50, path_relinking_requirement=500)  # num orders are

    tabu_obj.job_desc_dict = data_importer(order_number=order_count, tao_number=tao, r_number=r,
                                           instance_number=instance)

    time_start = time.time()
    tabu_obj.optimize()
    time_end = time.time()

    print('\n\nBest solution is: ', tabu_obj.best_solution)
    print('Sequence is: ', tabu_obj.best_solution_sequence)
    print('Rejected jobs are: ', tabu_obj.best_solution_rejected_jobs)
    print(f'Best solution is found in {time_end - time_start} seconds.')

    print(f'Best solution is improved by tabu search {tabu_obj.tabu_search_improved_best} times.')
    print(f'Best solution is improved by path relinking {tabu_obj.path_relinking_improved_best} times.')
