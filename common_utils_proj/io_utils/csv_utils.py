import numpy as np
import csv


def update_cell(result_table, row_index, col_index, samples_to_save):
    if isinstance(result_table[row_index, col_index], list):
        result_table[row_index, col_index].extend(samples_to_save)
    else:
        result_table[row_index, col_index] = samples_to_save


def write_csv(csv_file_path, result_table, top_labels_arr, left_labels_arr):
    file = open(csv_file_path, mode='w', newline='')
    csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(np.concatenate(([0], top_labels_arr)))
    for i in np.arange(len(left_labels_arr)):
        list_to_write = np.concatenate(([left_labels_arr[i]], result_table[i]))
        csv_writer.writerow(list_to_write)  # str(sleeve_rows_arr[i]) + ', ' + str(result[i])[1:-1].replace(' ', ', '))
    file.flush()
    file.close()