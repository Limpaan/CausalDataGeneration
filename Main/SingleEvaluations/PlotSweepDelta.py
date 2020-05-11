import numpy as np
import matplotlib.pyplot as plt
from DataGenerator.data_generator import split_patients, generate_data
from DataGenerator.distributions import DiscreteDistributionWithSmoothOutcomes
from Main.SingleEvaluations import DeltaSweepSettings
import Main.SingleEvaluations.DeltaSweepSettings


def plot_sweep_delta(values, times, settings, plot_var=False):
    plot_colors = ['k', 'r', 'b', 'g', 'm', 'c', 'y']
    plot_markers = ['s', 'v', 'P', '1', '2', '3', '4']
    plot_lines = ['-', '--', ':', '-.']

    # Extract settings
    load_settings = settings.load_settings
    setup_algorithms = settings.setup_algorithms
    starting_seed, n_data_sets, n_deltas, n_z, n_x, n_a, n_y, n_training_samples, n_test_samples, file_name_prefix = load_settings()
    tmp_dist = DiscreteDistributionWithSmoothOutcomes(3, 1, 5, 3)
    algs = setup_algorithms(split_patients(generate_data(tmp_dist, 10)), tmp_dist, 0.1)
    file_name_prefix = file_name_prefix
    n_algorithms = len(algs)
    deltas = np.linspace(0.0, 1.0, n_deltas)

    values_mean = np.sum(values, 0) / n_data_sets
    times_mean = np.sum(times, 0) / n_data_sets
    values_var = np.zeros((n_deltas, n_algorithms))
    times_var = np.zeros((n_deltas, n_algorithms))
    for i_delta in range(n_deltas):
        for i_alg in range(n_algorithms):
            v_var = 0
            t_var = 0
            for i_data_set in range(n_data_sets):
                v_var += (values_mean[i_delta][i_alg] - values[i_data_set][i_delta][i_alg])**2
                t_var += (times_mean[i_delta][i_alg] - times[i_data_set][i_delta][i_alg])**2
            values_var[i_delta][i_alg] = v_var / (n_data_sets - 1)
            times_var[i_delta][i_alg] = t_var / (n_data_sets - 1)

    # Plot mean treatment effect vs delta
    fig, ax1 = plt.subplots(figsize=(10, 7))
    plt.title('Mean treatment effect/mean search time vs delta')
    plt.xlabel('delta')
    ax2 = ax1.twinx()
    ax1.set_ylabel('Mean treatment effect')
    ax2.set_ylabel('Mean search time')
    lns = []
    for i_alg in range(n_algorithms):
        ln1 = ax1.plot(deltas, values_mean[:, i_alg], plot_colors[i_alg],
                       label='{} {}'.format(algs[i_alg].label, 'effect'))
        ln2 = ax2.plot(deltas, times_mean[:, i_alg], plot_colors[i_alg] + plot_lines[1],
                       label='{} {}'.format(algs[i_alg].label, 'time'))
        lns.append(ln1)
        lns.append(ln2)
        if plot_var:
            ln1v = ax1.fill_between(deltas, values_mean[:, i_alg] - values_var[:, i_alg], values_mean[:, i_alg] + values_var[:, i_alg],
                                    facecolor=plot_colors[i_alg], alpha=0.3)
            ln2v = ax2.fill_between(deltas, times_mean[:, i_alg] - times_var[:, i_alg], times_mean[:, i_alg] + times_var[:, i_alg],
                                    facecolor=plot_colors[i_alg], alpha=0.3)
            lns.append(ln1v)
            lns.append(ln2v)
    plt.grid(True)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lgd = plt.legend(lines1 + lines2, labels1 + labels2, bbox_to_anchor=(1.04, 0), loc='upper left')
    plt.savefig("saved_values/" + file_name_prefix + "_plot.png", bbox_extra_artists=(lgd,), bbox_inches='tight')


if __name__ == '__main__':
    settings = DeltaSweepSettings
    starting_seed, n_data_sets, n_deltas, n_z, n_x, n_a, n_y, n_training_samples, n_test_samples, file_name_prefix = settings.load_settings()
    values = np.load('saved_values/' + file_name_prefix + "values.npy")
    times = np.load('saved_values/' + file_name_prefix + "times.npy")

    plot_sweep_delta(values, times, settings, True)