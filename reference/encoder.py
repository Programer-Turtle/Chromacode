import hashlib
import math

VERSION = 0

BOOTSTRAP_COLOR_MAP = {
    "000": ["white", "white", "white"],
    "001": ["white", "white", "black"],
    "010": ["white", "black", "white"],
    "011": ["white", "black", "black"],
    "100": ["black", "white", "white"],
    "101": ["black", "white", "black"],
    "110": ["black", "black", "white"],
    "111": ["black", "black", "black"]
}

COLOR_MAP = {
    0: "white",
    1: "black",
    2: "red",
    3: "green",
    4: "blue",
    5: "yellow",
    6: "cyan",
    7: "magenta"
}

ERROR_CORRECTION_MAP = {
    "L":"00",
    "M":"01",
    "Q":"10",
    "H":"11"
}

MODE_MAP = {
    "UTF-8":"0000"
}

def checksum16_binary(binary_string: bytes):
    value = int(binary_string, 2)
    data = value.to_bytes((len(binary_string) + 7) // 8, byteorder="big")
    checksum = sum(data) & 0xFFFF
    return format(checksum, "016b")

def text_to_binary(text):
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def main(data, color_density, model, mode, compression = "None", ec = "L", width = 0, height = 0):
    #Stores colors of each cell after encoding
    cells = []
    
    #Calculates the number of bits each cell can encode, verifys within range, and creates bootstrap header
    bit_cluster_length = math.ceil(math.log2(color_density))
    if bit_cluster_length > 8 or bit_cluster_length < 1:
        raise ValueError("The color density header is only 3 bits. Maximum color denisty of 256 and minimum of 2.")
    cells.extend(BOOTSTRAP_COLOR_MAP[format(bit_cluster_length - 1, "03b")])
    
    #Calibration Colors
    cells.extend(list(COLOR_MAP.values())[2:color_density])

    #Version Header
    if VERSION < 0 or VERSION > 31:
        raise ValueError("Version number can only be between 0 and 31")
    
    binary = format(VERSION, "05b")

    #Mode Header
    binary += MODE_MAP[mode]

    #Compression Header (Yet To Impletment)
    binary += "000"

    #Error Correction Header
    binary += ERROR_CORRECTION_MAP[ec]
    
    #Encodes Payload
    match mode:
        case "UTF-8":
            payload_binary = text_to_binary(data)
        case _:
            raise ValueError("Unsupported mode")

    #Payload Length Test
    if len(payload_binary) > 1048575:
        raise ValueError("Payload too large")
    
    #Payload Length Header
    binary += format(len(payload_binary), "020b")
    
    #Checksum Header
    binary += checksum16_binary(payload_binary)
    
    #Add paylaod and Padd
    binary += payload_binary
    binary += "0" * (-len(binary) % bit_cluster_length)

    #Convert
    for bit_index in range(0, len(binary), bit_cluster_length):
        cells.append(COLOR_MAP[int(binary[bit_index:bit_index+bit_cluster_length], 2)])

    print(cells)
    print(len(cells))
    return cells

if __name__ == "__main__":
    main("How are you doing? I'm doing pretty good!", color_density=8, model=1, mode="UTF-8", ec="L")