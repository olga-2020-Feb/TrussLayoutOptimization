@CALL C:\ProgramData\Miniconda3\Scripts\activate.bat C:\ProgramData\Miniconda3
@CALL conda activate TrussTopologyOptimization
cd "D:\Truss\python_projects\algo_proj"
@CALL C:\ProgramData\Miniconda3\Scripts\activate.bat C:\ProgramData\Miniconda3
@CALL conda activate TrussTopologyOptimization

set intermediate_data_path=D:\Olga\intermediate_data

set PYTHONPATH=%PYTHONPATH%;D:\Truss\python_projects\common_utils_proj;D:\Truss\python_projects\math_utils_proj;D:\Truss\python_projects\vis_utils_proj

python main.py --nas_file_path D:\Truss\python_projects\input\nastran\wind_upendra_1.nas --csv_file_path D:\Truss\python_projects\output\wind_upendra_1\upendra.csv --mp4_file_path D:\Truss\python_projects\output\wind_upendra_1\upendra.mp4 --graph_png_file_path D:\Truss\python_projects\output\wind_upendra_1\upendra_graph.png


@CALL conda deactivate