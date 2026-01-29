def calculate_average(numbers):
    if not numbers:
        return 0  # or return None
    return sum(numbers) / len(numbers)