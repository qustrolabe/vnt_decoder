import os
from datetime import datetime

# Constants
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
BODY_PREFIX = "BODY;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:"
DCREATED_PREFIX = "DCREATED:"

def decode_quoted_printable(encoded_str):
    """
    Decodes a quoted-printable encoded string without using the quopri library.
    """
    decoded_str = bytearray()
    i = 0
    while i < len(encoded_str):
        if encoded_str[i] == '=':
            # Handle soft line breaks
            if i + 1 < len(encoded_str) and encoded_str[i + 1] in '\r\n':
                i += 1
                if i + 1 < len(encoded_str) and encoded_str[i] == '\r' and encoded_str[i + 1] == '\n':
                    i += 1
            # Decode hex-encoded characters
            elif i + 2 < len(encoded_str):
                hex_value = encoded_str[i + 1:i + 3]
                try:
                    decoded_str.append(int(hex_value, 16))
                except ValueError:
                    decoded_str.extend(b'=' + hex_value.encode())
                i += 2
        else:
            decoded_str.append(ord(encoded_str[i]))
        i += 1
    return decoded_str.decode('utf-8', errors='replace')

def extract_body(content):
    """
    Extracts and decodes the BODY content from the .vnt file.
    """
    body_start = content.find(BODY_PREFIX) + len(BODY_PREFIX)
    body_end = content.find("\nDCREATED:", body_start)
    if body_end == -1:  # If DCREATED is missing, use END:VNOTE as fallback
        body_end = content.find("\nEND:VNOTE", body_start)
    encoded_body = content[body_start:body_end].replace("=\n", "").replace("=\r\n", "").strip()
    return decode_quoted_printable(encoded_body)

def extract_dcreated(content):
    """
    Extracts and formats the DCREATED field from the .vnt file.
    """
    dcreated_start = content.find(DCREATED_PREFIX) + len(DCREATED_PREFIX)
    dcreated_end = content.find("\n", dcreated_start)
    dcreated_raw = content[dcreated_start:dcreated_end].strip() if dcreated_start > -1 else None
    try:
        return datetime.strptime(dcreated_raw, "%Y%m%dT%H%M%S").strftime("%Y-%m-%d %H:%M:%S") if dcreated_raw else "[No creation date]"
    except ValueError:
        return "[Invalid creation date]"

def decode_vnt_file(input_path, output_path):
    """
    Decodes a .vnt file and writes the decoded content to the output path.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            content = infile.read()
            decoded_body = extract_body(content)
            dcreated_date = extract_dcreated(content)
    except FileNotFoundError:
        print(f"Error: File not found - {input_path}")
        return
    except Exception as e:
        print(f"Error reading file {input_path}: {e}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(f"Creation date: {dcreated_date}\n")
            outfile.write(decoded_body)
    except Exception as e:
        print(f"Error writing file {output_path}: {e}")

def decode_vnt_files():
    """
    Decodes all .vnt files in the input folder and saves them to the output folder.
    """
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith('.vnt'):
            input_path = os.path.join(INPUT_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, filename.replace('.vnt', '.txt'))
            decode_vnt_file(input_path, output_path)
            print(f"Decoded: {input_path} -> {output_path}")

if __name__ == "__main__":
    decode_vnt_files()
