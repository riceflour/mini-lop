import random, os
from collections import defaultdict

TOTAL_EXEC_TIME = 0
TOTAL_EXEC = 0
TOTAL_BITMAPS = 0
TOTAL_BITMAP_SIZE = 0

def select_next_seed(seed_queue):
    coverage_seed = defaultdict(list)

    # build the coverage map
    for seed in seed_queue:
        for transition in seed.coverage:
            coverage_seed[transition].append(seed)
    
    # unmark all seeds first
    for seed in seed_queue:
        seed.unmark_favored()

    # mark the best seed for each transition as favored
    for seeds in coverage_seed.values():
        best = min(seeds, key=lambda s: s.avg_exec_time * s.avg_bitmap_size)
        best.mark_favored()
    
    # choose from seeds not yet visited
    favored = [s for s in seed_queue if s.favored and not s.visited]

    choice = random.randint(1, 10) 

    # if there are favoured and high chance to pick unvisited favoured
    if choice != 1 and favored:
        selected = random.choice(favored)
    else:
        # no unvisited favored seeds, pick unvisited seed
        unvisited = [s for s in seed_queue if not s.visited]
        if not unvisited:
            # reset visited
            for s in seed_queue:
                s.visited = False
            unvisited = seed_queue
        selected = random.choice(unvisited)
    # visited
    selected.visited = True
    return selected

# added func to calculate avg execution time 
def init_global_seed_stat(seed_queue):
    global TOTAL_EXEC_TIME, TOTAL_EXEC, TOTAL_BITMAP_SIZE, TOTAL_BITMAPS
    for seed in seed_queue:
        TOTAL_EXEC_TIME += seed.exec_time
        TOTAL_EXEC += 1
        TOTAL_BITMAP_SIZE += len(seed.coverage)
        TOTAL_BITMAPS += 1

# func that updates seed stats
def update_seed_stat(seed, exec_time, coverage):
    global TOTAL_EXEC_TIME, TOTAL_EXEC, TOTAL_BITMAP_SIZE, TOTAL_BITMAPS
    TOTAL_EXEC_TIME += seed.exec_time
    TOTAL_EXEC += 1
    TOTAL_BITMAP_SIZE += len(seed.coverage)
    TOTAL_BITMAPS += 1
    # update each seeds stats
    seed.exec_count += 1
    seed.total_exec_time += exec_time
    seed.avg_exec_time = seed.total_exec_time / seed.exec_count
    
    seed.total_bitmap_size += len(coverage)
    seed.avg_bitmap_size = seed.total_bitmap_size / seed.exec_count

# get the power schedule (# of new test inputs to generate for a seed)
def get_power_schedule(seed):
    global TOTAL_EXEC_TIME, TOTAL_EXEC, TOTAL_BITMAP_SIZE, TOTAL_BITMAPS
    # calc avg exec time and give score based off that
    avg_exec = TOTAL_EXEC_TIME / TOTAL_EXEC
    exec_time = seed.avg_exec_time
    if exec_time * 0.1 > avg_exec:
        perf_score = 10
    elif exec_time * 0.25 > avg_exec:
        perf_score = 25
    elif exec_time * 0.5 > avg_exec:
        perf_score = 50
    elif exec_time * 0.75 > avg_exec:
        perf_score = 75
    elif exec_time * 4 < avg_exec:
        perf_score = 300
    elif exec_time * 3 < avg_exec:
        perf_score = 200
    elif exec_time * 2 < avg_exec:
        perf_score = 150
    else:
        perf_score = 100  

    # coverage factor
    avg_coverage = TOTAL_BITMAP_SIZE / TOTAL_BITMAPS
    coverage = seed.avg_bitmap_size
    if coverage * 0.3 > avg_coverage:
        perf_score *= 3
    elif coverage * 0.5 > avg_coverage:
        perf_score *= 2
    elif coverage * 0.75 > avg_coverage:
        perf_score *= 1.5
    elif coverage * 3 < avg_coverage:
        perf_score *= 0.25
    elif coverage * 2 < avg_coverage:
        perf_score *= 0.25
    elif coverage * 1.5 < avg_coverage:
        perf_score *= 0.75
    else:
        pass
    perf_score = int(perf_score)
    # add randomness 
    return random.randint(perf_score // 2, perf_score)
    

