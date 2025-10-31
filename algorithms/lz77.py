class Lz77:
    def __new__(cls): pass

    @staticmethod
    def encode(file_path: str, save_path: str):
        with open(file_path, 'rb') as file:
            bytes_ = file.read()
            encoded_bytes = bytearray()

            # index
            i = 0
            while i < len(bytes_):
                # distance between current index and matched pointer
                match_distance = 0

                # length of the matched pointer
                match_length = 0

                # search index
                for j in range(max(0, i - 255), i):
                    # the lookahead index for continues byte group
                    k = 0

                    # conditions for increasing the lookahead index
                    while all([
                        # the lookahead index musn't be greater than
                        # the number of byte after i, so decoder won't
                        #  give an index error
                        (k < len(bytes_) - i - 1),

                        # lookahead index musn't be greater than 255,
                        # so it can fit in one byte
                        (k < 256),

                        # sum of the lookahead index and the search index
                        # musn't be greater than current index, so decoder
                        # won't try to access not loaded byte
                        # after current index
                        (j + k < i),

                        # look after the current index and the search index,
                        # they must be same
                        (bytes_[i + k] == bytes_[j + k]),
                    ]):
                        # +1 -> indexes starts from 0, lengths starts from 1
                        length = k + 1

                        # distance -> current index - search index
                        distance = i - j

                        # get pointer that has max length
                        if (length >= match_length):
                            match_length = length
                            match_distance = distance

                        k += 1

                # increase index by length of the matched byte
                i += match_length

                # get the next byte from byte
                next_byte = bytes_[i]

                # add the distance, length and next byte to the list
                encoded_bytes.append(match_distance)
                encoded_bytes.append(match_length)
                encoded_bytes.append(next_byte)

                i += 1
        
        with open(save_path, 'wb') as save:
            save.write(encoded_bytes)

    @staticmethod
    def decode(file_path: str, save_path: str):
        with open(file_path, 'rb') as file:
            decoded_bytes = bytearray()
            
            while True:
                bytes_ = file.read(3)
                
                # if the file ends, or is corrupted, stop reading
                if (len(bytes_) != 3):
                    break
                
                # get distance, length and next byte from
                # the file in the fixed order
                distance, length, next_byte = bytes_
                
                # if it is a pointer to the past byte
                if (distance != 0):
                    # the start of the byte
                    start = len(decoded_bytes) - distance

                    # skip to the `start` and take the first `length` byte
                    bytes_ = decoded_bytes[start: start + length]

                    decoded_bytes.extend(bytes_)

                # add next byte to the list
                decoded_bytes.append(next_byte)
        
        with open(save_path, 'wb') as save:
            save.write(decoded_bytes)
