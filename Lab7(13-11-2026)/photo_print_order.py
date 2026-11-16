import math


def parse_order(text):
    """Parse 'size:copies' (e.g. '4x6:25') into ('4X6', 25).

    Returns None if the input is invalid.
    """
    if not isinstance(text, str):
        return None

    parts = text.split(':')
    if len(parts) != 2:
        return None

    size = parts[0].strip().upper()
    if not size:
        return None

    try:
        copies = int(parts[1])
    except ValueError:
        return None

    if copies < 1:
        return None

    return size, copies


def file_size_average(sizes_csv):
    """Return the average of comma-separated file sizes in MB.

    Returns None if the input is invalid (empty, non-numeric, negative, etc.).
    """
    if not isinstance(sizes_csv, str):
        return None

    values = []
    for part in sizes_csv.split(','):
        try:
            value = int(part)
        except ValueError:
            return None
        if value < 0:
            return None
        values.append(value)

    if not values:
        return None

    return sum(values) // len(values)


def payable_amount(text):
    """Parse 'amount|discount' and return the payable amount (18% tax added).

    Returns None if the input is invalid.
    """
    if not isinstance(text, str):
        return None

    parts = text.split('|')
    if len(parts) != 2:
        return None

    try:
        amount = float(parts[0])
        discount = float(parts[1])
    except ValueError:
        return None

    # Reject nan / inf and negative values
    if not (math.isfinite(amount) and math.isfinite(discount)):
        return None
    if amount < 0 or discount < 0:
        return None

    total = amount * 1.18 - discount
    if not math.isfinite(total):
        return None

    return max(total, 0)


def main():
    print("==== Running parse_order ====")
    user_input = input("Enter print size:copies (e.g. 4x6:25): ")
    result = parse_order(user_input)
    if result is None:
        print("Invalid input. Expected format: size:copies (e.g. 4x6:25)")
    else:
        print("Size and Copies:", result)

    print("\n==== Running file_size_average ====")
    user_input = input("Enter file sizes in MB as CSV (e.g. 4,8,12): ")
    result = file_size_average(user_input)
    if result is None:
        print("Invalid input. Expected comma-separated whole numbers (e.g. 4,8,12)")
    else:
        print("Average File Size:", result)

    print("\n==== Running payable_amount ====")
    user_input = input("Enter amount|discount (e.g. 450|50): ")
    result = payable_amount(user_input)
    if result is None:
        print("Invalid input. Expected format: amount|discount (e.g. 450|50)")
    else:
        print("Payable Amount:", result)


if __name__ == "__main__":
    main()