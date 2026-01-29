def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0  # or return None
    return sum(numbers) / len(numbers)