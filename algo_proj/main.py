import argparse

from truss_opt_runner import trussOptOneTime

def parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nas_file_path', default='wind_upendra_1.nas')

    parser.add_argument('--csv_file_path', default=None)
    parser.add_argument('--mp4_file_path', default=None)
    parser.add_argument('--graph_png_file_path', default=None)

    args = parser.parse_args()
    params = args.__dict__
    return params

def main():
    params = parse_argument()
    nastran_file_path = params['nas_file_path']
    csv_file_path = params['csv_file_path']
    mp4_file_path = params['mp4_file_path']
    graph_png_file_path = params['graph_png_file_path']

    trussOptOneTime(nastran_file_path, csv_file_path, mp4_file_path, graph_png_file_path)


if __name__ == '__main__':
    main()