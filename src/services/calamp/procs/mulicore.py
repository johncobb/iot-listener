""" only use for multi-core processing """
# import threading
# from multiprocessing import Pool
# from multiprocessing import cpu_count

# def multicore_proc(proc_handler):
#     count = 0
#     num_cores = cpu_count()
#     pool = Pool(processes=num_cores)

#     pool.apply_async(proc_handler, args=(None,))

#     while(True):
#         pass

#     pool.close()
#     pool.join()

# def main():
#     multicore_proc(proc_main)
