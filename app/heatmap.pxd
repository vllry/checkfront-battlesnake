import cython

cdef default_heatmap(int width, int height)
cdef int fractal_heat(state, data, int width, int height, int head_x, int head_y, int neck_x, int neck_y, int depth, double factor, int food_found=*)
cdef int heat_direction(state, data, int width, int height, int new_head_x, int new_head_y, int head_x, int head_y, int neck_x, int neck_y, int depth, double factor, int food_found)

@cython.locals(width = cython.int, height = cython.int, turn = cython.int, x = cython.int, y = cython.int)
cpdef gen_heatmap(requestdata, int maxturns=*, use_rings=*)
