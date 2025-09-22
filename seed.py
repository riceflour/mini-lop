import os
class Seed:
    def __init__(self, path, seed_id, coverage, exec_time):
        self.path = path
        self.seed_id = seed_id
        self.coverage = coverage
        self.exec_time = exec_time
        # by default, a seed is not marked as favored
        self.favored = 0
        self.visited = False
        # for seed prior and power schedule
        self.exec_count = 1
        self.total_exec_time = exec_time
        self.avg_exec_time = exec_time
        
        self.total_bitmap_size = len(coverage)
        self.avg_bitmap_size = len(coverage)

    def mark_favored(self):
        self.favored = 1

    def unmark_favored(self):
        self.favored = 0
