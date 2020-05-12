from DataGenerator.data_generator import split_patients, generate_data
from DataGenerator.distributions import DiscreteDistributionWithSmoothOutcomes
import numpy as np
import matplotlib.pylab as plt

from Main.SingleEvaluations import DataAmountSettings


def plot_sweep_data(values, times, settings, plot_var=False):

    plot_colors = ['k', 'r', 'b', 'g', 'm', 'c', 'y']
    plot_markers = ['s', 'v', 'P', '1', '2', '3', '4']
    plot_lines = ['-', '--', ':', '-.']

    load_settings = settings.load_settings
    setup_algorithms = settings.setup_algorithms
    starting_seed, n_data_sets, delta, n_data_set_sizes, n_z, n_x, n_a, n_y, n_training_samples_max, n_test_samples, file_name_prefix = load_settings()
    tmp_dist = DiscreteDistributionWithSmoothOutcomes(3, 1, 5, 3)
    algs = setup_algorithms(split_patients(generate_data(tmp_dist, 10)), tmp_dist, 0.1)
    file_name_prefix = file_name_prefix
    n_algorithms = len(algs)
    n_training_samples_array = np.geomspace(10, n_training_samples_max, n_data_set_sizes).astype(int)

    values_mean = np.sum(values, 0) / n_data_sets
    times_mean = np.sum(times, 0) / n_data_sets
    values_var = np.zeros((n_data_set_sizes, n_algorithms))
    times_var = np.zeros((n_data_set_sizes, n_algorithms))
    for i_size in range(n_data_set_sizes):
        for i_alg in range(n_algorithms):
            v_var = 0
            t_var = 0
            for i_data_set in range(n_data_sets):
                v_var += (values_mean[i_size][i_alg] - values[i_data_set][i_size][i_alg]) ** 2
                t_var += (times_mean[i_size][i_alg] - times[i_data_set][i_size][i_alg]) ** 2
            values_var[i_size][i_alg] = v_var / (n_data_sets - 1)
            times_var[i_size][i_alg] = t_var / (n_data_sets - 1)
    # Plot mean treatment effect vs delta
    fig, ax1 = plt.subplots(figsize=(10, 7))
    plt.title('Mean treatment value/Mean search time vs data set size (delta: {})'.format(delta))
    plt.xlabel('Data set size')
    ax2 = ax1.twinx()
    ax1.set_ylabel('Mean treatment value')
    ax2.set_ylabel('Mean search time')
    lns = []
    for i_alg in range(n_algorithms):
        ln1 = ax1.plot(n_training_samples_array, values_mean[:, i_alg], plot_colors[i_alg],
                       label='{} {}'.format(algs[i_alg].label, 'effect'))
        ln2 = ax2.plot(n_training_samples_array, times_mean[:, i_alg], plot_colors[i_alg] + plot_lines[1],
                       label='{} {}'.format(algs[i_alg].label, 'time'))
        lns.append(ln1)
        lns.append(ln2)
        if plot_var:
            ln1v = ax1.fill_between(n_training_samples_array, values_mean[:, i_alg] - values_var[:, i_alg], values_mean[:, i_alg] + values_var[:, i_alg],
                                    facecolor=plot_colors[i_alg], alpha=0.3)
            ln2v = ax2.fill_between(n_training_samples_array, times_mean[:, i_alg] - times_var[:, i_alg], times_mean[:, i_alg] + times_var[:, i_alg],
                                    facecolor=plot_colors[i_alg], alpha=0.3)
            lns.append(ln1v)
            lns.append(ln2v)
    plt.grid(True)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lgd = plt.legend(lines1 + lines2, labels1 + labels2, bbox_to_anchor=(1.04, 0), loc='upper left')
    plt.xscale('log')
    plt.savefig("saved_values/" + file_name_prefix + "_plot.png", bbox_extra_artists=(lgd,), bbox_inches='tight')


if __name__ == '__main__':
    settings = DataAmountSettings
    starting_seed, n_data_sets, delta, n_data_set_sizes, n_z, n_x, n_a, n_y, n_training_samples_max, n_test_samples, file_name_prefix = settings.load_settings()
    values = np.load("saved_values/" + file_name_prefix + "values.npy")
    times = np.load("saved_values/" + file_name_prefix + "times.npy")

    plot_sweep_data(values, times, settings, False)
