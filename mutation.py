import random


def havoc_mutation(conf, seed):
    # havoc mutation 
    with open(seed.path, 'rb') as f:
        data = bytearray(f.read())

        mutations = [
            flippy_mutate,  
            rotate_mutate, 
            add_sub_mutate, 
            replace_mutate, 
            delete_mutate,
            swapsies_mutate, 
            random_insert_mutate,
        ]
        # choosing num mutations from powers of 2
        num_mutations = random.choice([2, 4, 8, 16, 32, 64, 128])

        # mutate using a random strategy
        for _ in range(random.randint(1, num_mutations)):
            action = random.choice(mutations)
            data = action(data)

        # write the mutated data back to the current input file
        with open(conf['current_input'], 'wb') as f_out:
            f_out.write(data)


# randomly select a short int/int/long int (2/4/8 bytes) from the seed file, and add/sub a random value
def add_sub_mutate(data: bytearray):
    data_len = len(data)
    if data_len < 2:
        return random.choice([flippy_mutate, rotate_mutate])(data)

    possible_sizes = [2, 4, 8]
    num_bytes = random.choice([size for size in possible_sizes if size <= data_len])

    # take random chunk to mutate
    index = random.randint(0, data_len - num_bytes)
    chunk = data[index:index + num_bytes]
    # convert bytes to int
    value = int.from_bytes(chunk, byteorder='little', signed=False)
    delta_bytes = random.choice([1, 2])
    max_delta = min((1 << (8 * delta_bytes)) - 1, 1000)
    delta = random.randint(1, max_delta)

    if random.choice(["add", "sub"]) == "add":
        value = (value + delta)
    else:
        # prevent underflow
        value = (value - delta) % (1 << (8 * num_bytes)) 

    # ensure value fits in num_bytes after wrapping
    value = value % (1 << (8 * num_bytes))

    new_bytes = value.to_bytes(num_bytes, byteorder='little', signed=False)
    data[index:index + num_bytes] = new_bytes
    
    return data

# # randomly replace a short int/int/long int (2/4/8 bytes) with an interesting value (min/max/0/-1/1).
def replace_mutate(data: bytearray):
    if len(data) < 2:
        return random.choice([flippy_mutate, rotate_mutate])(data)
    # choose random byte value
    num_bytes = random.choice([2, 4, 8])  

    # interesting values
    values = {
        2: [0, 1, -1, -32768, 32767],
        4: [0, 1, -1, -2147483648, 2147483647],
        8: [0, 1, -1, -9223372036854775808, 9223372036854775807]
    }

    possible_sizes = [size for size in values if size <= len(data)]
    num_bytes = random.choice(possible_sizes)

    # choose index to mutate and value to mutate to
    index = random.randint(0, len(data) - num_bytes)
    value = random.choice(values[num_bytes])
    mutated_bytes = value.to_bytes(num_bytes, byteorder='little', signed=True)
    data[index:index + num_bytes] = mutated_bytes

    return data

# randomly replace a random length chunk of bytes in the seed input with another chunk in the same file
def swapsies_mutate(data: bytearray):
    if len(data) < 4:
        return random.choice([replace_mutate, add_sub_mutate])(data)
    
    # choose random chunk length between 1 and a quarter of len(data), or 32 which ever is smaller
    max_chunk_len = max(1, min(32, len(data) // 4))
    chunk_len = random.randint(1, max_chunk_len)

    # source and target locations
    source = random.randint(0, len(data) - chunk_len)
    target = random.randint(source, len(data) - chunk_len)

    # extract chunk
    chunk = data[source:source + chunk_len]
    data[target:target + chunk_len] = chunk

    return data

# default implementation that flips a bit of a random byte
def flippy_mutate(data: bytearray):
    if not data:
        return data
    # Randomly select a byte index to flip
    byte_index = random.randint(0, len(data) - 1)

    # Randomly select a bit to flip within the byte
    bit_position = random.randint(0, 7)

    # Flip the selected bit in the byte using XOR
    data[byte_index] ^= (1 << bit_position)
    return data

# strategy that deletes a random chunk of data
def delete_mutate(data: bytearray):
    if len(data) < 2:
        return random.choice([flippy_mutate, rotate_mutate])(data)
    # choose length to delete
    delete_len = random.randint(1, min(8, len(data)))
    # choose position to delete from
    position = random.randint(0, len(data) - delete_len)
    # return two chunks not including delete position
    return data[:position] + data[position + delete_len:]

# randomly replace a random length chunk of bytes in the seed input with a random chunk
def random_insert_mutate(data: bytearray):
    if len(data) < 4:
        return random.choice([replace_mutate, add_sub_mutate])(data)
    # choose random chunk length between 1 and a quarter of len(data)
    max_chunk_len = max(1, len(data) // 4)
    chunk_len = random.randint(1, max_chunk_len)

    # target locations
    target = random.randint(0, len(data) - chunk_len)

    # replace
    data[target:target + chunk_len] = bytearray(random.getrandbits(8) for _ in range(chunk_len))

    return data

# a helper func that rotates a byte
def rotate_byte(byte, bits):
    return ((byte << bits) & 0xFF) | (byte >> (8 - bits))

# rotates a random section of bytes (rotation of a byte not the whole section)
def rotate_mutate(data):
    if not data:
        return data
    # select random length
    chunk_len = random.randint(1, len(data))
    # random start index
    start = random.randint(0, len(data) - chunk_len)
    if random.random() < 0.5:
        # rotate each byte by 1
        rotated = bytearray(rotate_byte(b, 1) for b in data[start:start + chunk_len])
    else:
        # rotate each byte randomly
        rotated = bytearray(rotate_byte(b, random.randint(1, 7)) for b in data[start:start + chunk_len])
    return data[:start] + rotated + data[start + chunk_len:]