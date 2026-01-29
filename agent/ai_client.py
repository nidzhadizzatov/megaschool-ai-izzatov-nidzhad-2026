def calculate_average(numbers):
    """Calculates the average of a list of numbers."""
    if not numbers:
        return 0  # or return None if preferred
    return sum(numbers) / len(numbers)

# Example usage
if __name__ == '__main__':
    print(calculate_average([]))  # Should return 0 or None
    print(calculate_average([1, 2, 3]))  # Should return 2.0