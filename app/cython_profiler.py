import pstats, cProfile

import heatmap

cProfile.runctx("heatmap.test_generate(10)", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
