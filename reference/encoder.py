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

MODELS = {
    1: "000",
    2: "001",
    3: "010",
    4: "011",
    5: "100"
}

ECS = {
    "L":"00",
    "M":"01",
    "Q":"10",
    "H":"11"
}

MODES = {
    "UTF-8":"0000"
}

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
    cells.extend(list(COLOR_MAP.values())[2:])

    #Attaches Header Data
    #Version 5
    if VERSION < 0 or VERSION > 31:
        raise ValueError("Version number can only be between 0 and 31")
    
    binary = format(VERSION, "05b")

    #Model 3 
    if model not in MODELS:
        raise ValueError("Invalid Model")
    
    binary += MODELS[model]

    #Model Custom 12
    if model == 5:
        if width < 0 or width > 4095:
            raise ValueError("Width can only be between 0 and 4095")
    
        binary += format(width, "012b")

        if height < 0 or height > 4095:
            raise ValueError("Height can only be between 0 and 4095")
    
        binary += format(height, "012b")

    #Mode 4
    binary += MODES[mode]

    #Compression 3 Not supported yet
    binary += "000"

    #EC 2
    binary += ECS[ec]
    
    #Encodes binary based on mode
    match mode:
        case "UTF-8":
            payload_binary = text_to_binary(data)
        case _:
            raise ValueError("Unsupported mode")

    #Payload Length
    if len(payload_binary) > 1048575:
        raise ValueError("Payload too large")
    
    binary += format(len(payload_binary), "020b")
    
    #Checksum 16
    checksum = int(binary, 2) % 65536
    binary += format(checksum, "016b")
    
    binary += payload_binary
    binary += "0" * (-len(binary) % bit_cluster_length)

    for bit_index in range(0, len(binary), bit_cluster_length):
        cells.append(COLOR_MAP[int(binary[bit_index:bit_index+bit_cluster_length], 2)])

    print(cells)
    print(len(cells))

if __name__ == "__main__":
    with open("draw.html", "r", encoding="utf-8") as file:
        data = file.read()
    main(data, color_density=8, model=1, mode="UTF-8", ec="L")