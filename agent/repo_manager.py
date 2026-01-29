def calculate_average(numbers):
    """Calculates the average of a list of numbers."""
    if not numbers:
        return 0  # or return None
    return sum(numbers) / len(numbers)

# Example usage:
# print(calculate_average([]))  # Should return 0 or None
