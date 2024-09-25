snakeviz filename
python3 -m cProfile -o report.stats src/report.py


kernprof -l -o [profiling/utils.py.lprof] [src/utils.py]  ## generate profile
python3 -m line_profiler  "profiling/utils.py.lprof"  ## views profile