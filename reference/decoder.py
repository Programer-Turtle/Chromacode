MODES = {
    "0000":"UTF-8"
}

ECS = {
    "00": "L",
    "01": "M",
    "10": "Q",
    "11": "H"
}

def decode_utf8(binary):
    split_text = []
    for i in range(0, len(binary), 8):
        split_text.append(chr(int(binary[i:i+8], 2)))

    return "".join(split_text)

def decode_header(header_binary):
    VERSION = int(header_binary[:5], 2)
    MODE = MODES[header_binary[5:9]]
    COMPRESSION = int(header_binary[9:12], 2)
    EC = ECS[header_binary[12:14]]
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

def decode(binary):
    header_data = decode_header(binary[:50])
    print(header_data)
    payload_binary = binary[50:50+header_data["payload_length"]]
    
    match header_data["mode"]:
        case "UTF-8":
            print(decode_utf8(payload_binary))

COLOR_MAP = {
    "white": "000",
    "black": "001",
    "red": "010",
    "green": "011",
    "blue": "100",
    "yellow": "101",
    "cyan": "110",
    "magenta": "111"
}
final_binary = ""
colors = ['white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'red', 'cyan', 'white', 'white', 'white', 'black', 'green', 'white', 'white', 'blue', 'blue', 'black', 'blue', 'yellow', 'green', 'green', 'white', 'cyan', 'cyan', 'black', 'yellow', 'magenta', 'black', 'white', 'white', 'yellow', 'green', 'yellow', 'yellow', 'magenta', 'green', 'blue', 'blue', 'cyan', 'cyan', 'black', 'blue', 'blue', 'black', 'green', 'blue', 'red', 'white', 'black', 'black', 'black', 'black', 'white', 'white', 'cyan', 'cyan', 'black', 'yellow', 'magenta', 'green', 'yellow', 'blue', 'cyan', 'red', 'blue', 'blue', 'white', 'green', 'yellow', 'white', 'cyan', 'blue', 'black', 'yellow', 'black', 'green', 'blue', 'cyan', 'red', 'white', 'black', 'cyan', 'white', 'green', 'green', 'white', 'cyan', 'white', 'yellow', 'blue', 'green', 'green', 'black', 'red', 'red', 'white', 'black', 'yellow', 'black', 'green', 'yellow', 'white', 'red', 'green', 'yellow', 'cyan', 'green', 'black', 'white', 'white', 'cyan', 'white', 'yellow', 'cyan', 'magenta', 'green', 'black', 'red', 'magenta', 'black', 'yellow', 'yellow', 'magenta', 'green', 'green', 'red', 'cyan', 'red', 'blue', 'yellow', 'cyan']
for color in colors:
    final_binary += COLOR_MAP[color]

if __name__ == "__main__":
    decode(final_binary)
