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

MODES = {
    1: {"width":25, "height":25, "binary": "000"},
    2: {"width":49, "height":49, "binary": "001"},
    3: {"width":81, "height":81, "binary": "010"},
    4: {"width":177, "height":177, "binary": "011"}
}

ECS = {
    "L":"00",
    "M":"01",
    "Q":"10",
    "H":"11"
}

def text_to_binary(text):
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def main(data, color_density, model, mode, ec):
    #Stores colors of each cell after encoding
    block_colors = []
    
    #Calculates the number of bits each cell can encode, verifys within range, and creates bootstrap header
    bit_cluster_length = math.ceil(math.log2(color_density))
    if bit_cluster_length > 8 or bit_cluster_length < 1:
        raise Exception("The color density header is only 3 bits. Maximum color denisty of 256 and minimum of 2.")
    block_colors.extend(BOOTSTRAP_COLOR_MAP[format(bit_cluster_length - 1, "03b")])
    
    #Encodes binary based on mode
    match mode:
        case "text":
            binary = text_to_binary(data)

    binary += "0" * (-len(binary) % bit_cluster_length)

    for bit_index in range(0, len(binary), bit_cluster_length):
        block_colors.append(COLOR_MAP[int(binary[bit_index:bit_index+bit_cluster_length], 2)])

    print(block_colors)

if __name__ == "__main__":
    main("Hello World", color_density=8, model=1, mode="text", ec="L")