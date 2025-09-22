import ctypes
import sys
import sysv_ipc
from datetime import datetime

SHM_ENV_VAR   = "__AFL_SHM_ID"
MAP_SIZE_POW2 = 16
MAP_SIZE = (1 << MAP_SIZE_POW2)
EDGE_MAP = bytearray(MAP_SIZE)
START = datetime.now()

def setup_shm(libc):
    # map functions
    shmget = libc.shmget
    shmat = libc.shmat

    shmat.restype = ctypes.c_void_p
    shmat.argtypes = (ctypes.c_int, ctypes.c_void_p, ctypes.c_int)

    # get the shared memory segment

    shmid = shmget(sysv_ipc.IPC_PRIVATE, MAP_SIZE, sysv_ipc.IPC_CREAT | sysv_ipc.IPC_EXCL | 0o600)

    if shmid < 0:
        sys.exit("cannot get shared memory segment with key %d" % (sysv_ipc.IPC_PRIVATE))

    # map the shared segment into the current process' memory
    # the location (size + 4096) is just a hint
    shmptr = shmat(shmid, None, 0)
    if shmptr == 0 or shmptr== -1:
        sys.exit("cannot attach shared memory segment with id %d" % (shmid))

    print(f'created shared memory, shmid: {shmid}')

    return shmid, shmptr


def clear_shm(trace_bits):
    ctypes.memset(trace_bits, 0, MAP_SIZE)


def check_crash(status_code):
    crashed = False
    if status_code == 6:
        crashed = True
        print("Found an abort!")
    elif status_code == 134:
        crashed = True
        print("Found an abort!")
    elif status_code == 8:
        crashed = True
        print("Found a float-point error!")
    elif status_code == 11:
        crashed = True
        print("Found a segfault!")
    elif status_code == 139:
        crashed = True
        print("Found a segfault!")
    return crashed


def check_coverage(trace_bits):
    global EDGE_MAP
    raw_bitmap = ctypes.string_at(trace_bits, MAP_SIZE)
    new_edge_covered = False
    new_edges = set()

    for i in range(len(raw_bitmap)):
        if raw_bitmap[i] != 0:
            # new edge
            if EDGE_MAP[i] == 0:
                new_edge_covered = True
                EDGE_MAP[i] = 1
            new_edges.add(i)
    if new_edge_covered:
        edges = sum(1 for b in EDGE_MAP if b != 0)
        now = datetime.now()
        curr = datetime.now() - START
        total_seconds = int(curr.total_seconds())
        hour = total_seconds // 3600
        minute = (total_seconds % 3600) // 60
        second = total_seconds % 60
        print(f"Total coverage so far: {edges} edges {hour}:{minute:02}:{second:02} \t {now.hour}:{now.minute:02}:{now.second:02}")
    

    return new_edge_covered, new_edges