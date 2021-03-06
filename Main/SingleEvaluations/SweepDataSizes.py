from multiprocessing.pool import Pool

import numpy as np
import time
from Algorithms.constrained_dynamic_programming import generate_data, split_patients
from DataGenerator.distributions import DiscreteDistributionWithSmoothOutcomes
from Main.SingleEvaluations.Settings import DataAmountSettings
from Main.SingleEvaluations.Plotters.PlotSweepData import plot_sweep_data

def get_settings():
    return DataAmountSettings

def do_work(i_data_set, n_algorithms):
    settings = get_settings()
    starting_seed, n_data_sets, delta, n_data_set_sizes, n_z, n_x, n_a, n_y, n_training_samples_max, n_test_samples, file_name_prefix = settings.load_settings()
    res = np.zeros((2, n_data_set_sizes, n_algorithms))
    seeds = [x for x in range(starting_seed, starting_seed + n_data_sets)]
    n_training_samples_array = np.geomspace(10, n_training_samples_max, n_data_set_sizes).astype(int)

    print("Starting set {}".format(i_data_set))
    dist, unsplit_training_data, test_data = settings.setup_data_sets(n_z, n_x, n_a, n_y, n_training_samples_max, n_test_samples,
                                                             seeds[i_data_set])
    saved_table = None
    for i_size in range(n_data_set_sizes):
        print("Evaluating data set size = {}".format(n_training_samples_array[i_size]))
        d_tmp = {'x': np.copy(unsplit_training_data['x'][0:n_training_samples_array[i_size]]),
                 'h': np.copy(unsplit_training_data['h'][0:n_training_samples_array[i_size]]),
                 'z': np.copy(unsplit_training_data['z'][0:n_training_samples_array[i_size]])}
        training_data = split_patients(d_tmp)

        algorithms = settings.setup_algorithms(training_data, dist, delta)
        for alg in algorithms:
            start = time.time()
            print("Training {}".format(alg.name))
            if alg.name == "Dynamic Programming True":
                if saved_table is None:
                    alg.learn()
                    saved_table = alg.q_table
                else:
                    alg.q_table = saved_table
            else:
                alg.learn()
            print("Training {} took {:.3f} seconds".format(alg.name, time.time() - start))
        for i_alg in range(n_algorithms):
            print("Evaluating algorithm {}".format(algorithms[i_alg].name))
            total_time = 0
            n_at_max = 0
            for i_sample in range(len(test_data)):
                interventions = algorithms[i_alg].evaluate(test_data[i_sample])
                total_time += len(interventions)
                best_outcome = max([treatment[1] for treatment in interventions])
                if best_outcome == np.max(test_data[i_sample][2]):
                    n_at_max += 1
            res[0][i_size][i_alg] = n_at_max / n_test_samples
            res[1][i_size][i_alg] = total_time / n_test_samples
    return res


if __name__ == '__main__':
    settings = get_settings()

    # Settings
    plot_var = True
    starting_seed, n_data_sets, delta, n_data_set_sizes, n_z, n_x, n_a, n_y, n_training_samples_max, n_test_samples, file_name_prefix = settings.load_settings()

    # Setup

    # Quick hack to get n_algorithms
    tmp_dist = DiscreteDistributionWithSmoothOutcomes(n_z, n_x, n_a, n_y)
    algs = settings.setup_algorithms(split_patients(generate_data(tmp_dist, 10)), tmp_dist, 0.1)
    n_algorithms = len(algs)

    values = np.zeros((n_data_sets, n_data_set_sizes, n_algorithms))
    times = np.zeros((n_data_sets, n_data_set_sizes, n_algorithms))

    main_start = time.time()
    pool = Pool(processes=n_data_sets)
    results = []
    for i in range(n_data_sets):
        results.append(pool.apply_async(do_work, (i, n_algorithms)))
    for i in range(n_data_sets):
        r = results[i].get()
        values[i] = r[0]
        times[i] = r[1]
    np.save("saved_values/" + file_name_prefix + "values", values)
    np.save("saved_values/" + file_name_prefix + "times", times)
    plot_sweep_data(values, times, settings, plot_var)
    print("Total time for delta sweep was {:.3f} seconds".format(time.time() - main_start))
