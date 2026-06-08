import math

COLOR_MAP = {
    0: "black",
    1: "white",
    2: "red",
    3: "green",
    4: "blue",
    5: "yellow",
    6: "cyan",
    7: "magenta"
}

def text_binary(text):
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def main(data, mode, color_density):
    bit_cluster_length = int(math.log2(color_density))
    match mode:
        case "text":
            binary = text_binary(data)

    binary += "0" * (-len(binary) % bit_cluster_length)

    for bit_index in range(0, len(binary), bit_cluster_length):
        print(COLOR_MAP[int(binary[bit_index:bit_index+bit_cluster_length], 2)])

if __name__ == "__main__":
    main("Hello World", "text",8)