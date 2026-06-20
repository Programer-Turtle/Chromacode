import hashlib
import math

VERSION = 0

COLOR_MAP = {
    "white": 0,
    "black": 1,
    "red": 2,
    "green": 3,
    "blue": 4,
    "yellow": 5,
    "cyan": 6,
    "magenta": 7
}

ERROR_CORRECTION_MAP = {
    "00": "L",
    "01": "M",
    "10": "Q",
    "11": "H"
}

MODE_MAP = {
    "0000":"UTF-8"
}

def checksum16_binary(binary_string: bytes):
    value = int(binary_string, 2)
    data = value.to_bytes((len(binary_string) + 7) // 8, byteorder="big")
    checksum = sum(data) & 0xFFFF
    return format(checksum, "016b")

def decode_utf8(binary):
    split_text = []
    for i in range(0, len(binary), 8):
        split_text.append(chr(int(binary[i:i+8], 2)))

    return "".join(split_text)

def decode_header(header_binary):
    #Pull Header From Binary
    VERSION = int(header_binary[:5], 2)
    MODE = MODE_MAP[header_binary[5:9]]
    COMPRESSION = int(header_binary[9:12], 2)
    EC = ERROR_CORRECTION_MAP[header_binary[12:14]]
    PAYLOAD_LENGTH = int(header_binary[14:34], 2)
    CHECKSUM = int(header_binary[34:], 2)

    print(" ".join([header_binary[:5], header_binary[5:9], header_binary[9:12], header_binary[12:14], header_binary[14:34], header_binary[34:]]))

    return {
        "version": VERSION,
        "mode": MODE,
        "compression": COMPRESSION,
        "ec": EC,
        "payload_length": PAYLOAD_LENGTH,
        "checksum": CHECKSUM
    }

def decode_binary(binary):
    header_data = decode_header(binary[:50])
    print(header_data)
    payload_binary = binary[50:50+header_data["payload_length"]]

    #Check Data Integrity
    checksum_test = checksum16_binary(payload_binary)
    print(checksum_test)
    if header_data["checksum"] != int(checksum_test, 2):
        print("Checksum Failed. Data Corrupted")
        return
    
    #Checks Mode and Decodes Binary
    match header_data["mode"]:
        case "UTF-8":
            print(decode_utf8(payload_binary))

def decode(color_blocks, color_density):
    #Calculates the number of bits each cell can encode and verifys it's within range.
    bit_cluster_length = math.ceil(math.log2(color_density))
    if bit_cluster_length > 8 or bit_cluster_length < 1:
        raise ValueError("The color density header is only 3 bits. Maximum color denisty of 256 and minimum of 2.")
    print(bit_cluster_length)

    #Converts colors back to binary
    final_binary = ""
    for color in color_blocks:
        final_binary += format(COLOR_MAP[color], f"0{bit_cluster_length}b")

    decode_binary(final_binary)

if __name__ == "__main__":
    decode(['white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'red', 'blue', 'blue', 'white', 'black', 'cyan', 'red', 'blue', 'cyan', 'blue', 'blue', 'black', 'yellow', 'magenta', 'green', 'yellow', 'cyan', 'red', 'white', 'black', 'blue', 'black', 'green', 'blue', 'blue', 'cyan', 'red', 'blue', 'blue', 'white', 'green', 'cyan', 'red', 'cyan', 'magenta', 'yellow', 'cyan', 'yellow', 'black', 'white', 'white', 'cyan', 'red', 'black', 'yellow', 'magenta', 'green', 'red', 'red', 'cyan', 'magenta', 'black', 'blue', 'magenta', 'black', 'magenta', 'cyan', 'red', 'white', 'black', 'black', 'black', 'black', 'black', 'cyan', 'cyan', 'cyan', 'blue', 'blue', 'white', 'green', 'black', 'white', 'cyan', 'magenta', 'yellow', 'yellow', 'black', 'green', 'green', 'blue', 'cyan', 'green', 'blue', 'blue', 'white', 'green', 'blue', 'white', 'magenta', 'black', 'black', 'blue', 'yellow', 'green', 'yellow', 'white', 'magenta', 'red', 'black', 'magenta', 'black', 'black', 'white', 'white', 'cyan', 'green', 'yellow', 'yellow', 'magenta', 'green', 'green', 'cyan', 'cyan', 'red', 'white', 'blue', 'black'], 8)