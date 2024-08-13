#!/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
import sys

# Define valid unconditional branch opcodes and their fixed bit patterns
branch_opcodes = {
    'B': 0b000101 << 26,
    'BL': 0b100101 << 26,
    'CBZ': 0b10110100 << 24,
    'CBNZ': 0b10110101 << 24,
    'TBZ': 0b01101100 << 24,
    'TBNZ': 0b01101101 << 24
}

# Define condition codes for B.<condition> opcodes
condition_codes = {
    'EQ': 0b00000,
    'NE': 0b00001,
    'CS': 0b00010, 'HS': 0b00010,
    'CC': 0b00011, 'LO': 0b00011,
    'MI': 0b00100,
    'PL': 0b00101,
    'VS': 0b00110,
    'VC': 0b00111,
    'HI': 0b01000,
    'LS': 0b01001,
    'GE': 0b01010,
    'LT': 0b01011,
    'GT': 0b01100,
    'LE': 0b01101,
    'AL': 0b11110,
    'NV': 0b11111
}


def generate_branch_opcode(current_address, target_address, opcode):
    if opcode in branch_opcodes:
        # Handle B and BL instructions
        offset = (target_address - current_address) // 4
        if offset < -(2**25) or offset >= 2**25:
            raise ValueError(
                f"Target address is out of range for {opcode} instruction")
        opcode_bits = branch_opcodes[opcode] | (offset & 0x03FFFFFF)

    elif opcode.startswith('B.') and opcode[2:].upper() in condition_codes:
        # Handle conditional branches like B.EQ, B.NE, etc.
        condition = opcode[2:].upper()
        offset = (target_address - current_address - 4) // 4
        if offset < -(2**18) or offset >= 2**18:
            raise ValueError(
                f"Target address is out of range for {opcode} instruction")
        opcode_bits = (0b01010100 << 24) | (
            (offset & 0x7FFFF) << 5) | condition_codes[condition]

    else:
        valid_opcodes = list(branch_opcodes.keys()) + \
            [f"B.{cond}" for cond in condition_codes.keys()]
        raise ValueError(
            f"Invalid branch opcode '{opcode}'. Valid options are: {', '.join(valid_opcodes)}")

    # Return the opcode in hexadecimal format
    return f"{opcode_bits:08x}"


def convert_to_little_endian(hex_str):
    # Split the hex string into bytes and reverse the order
    byte_pairs = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    little_endian = ''.join(reversed(byte_pairs))
    return little_endian


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 generate_branch_opcode.py <current_address> <target_address> <branch_opcode>")
        print("Valid branch opcodes: ", ', '.join(
            list(branch_opcodes.keys()) + [f"B.{cond}" for cond in condition_codes.keys()]))
        sys.exit(1)

    # Parse the command-line arguments
    current_address = 0
    try:
        current_address = int(sys.argv[1], 16)
        target_address = int(sys.argv[2], 16)
        branch_opcode = sys.argv[3].upper()
    except ValueError:
        print("Error: Addresses must be valid hexadecimal numbers.")
        sys.exit(1)

    try:
        # Generate the branch opcode
        opcode = generate_branch_opcode(
            current_address, target_address, branch_opcode)
        print(f"{branch_opcode} Opcode: 0x{opcode}")
        little_endian_opcode = convert_to_little_endian(opcode)
        print(
            f"\n\nWrite the following starting at address: 0x{current_address:08x}")
        print(
            f"\n\n{branch_opcode} Opcode (Little Endian): 0x{little_endian_opcode}\n\n")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
