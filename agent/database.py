def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0  # or return None
    return sum(numbers) / len(numbers)

# Example usage
if __name__ == '__main__':
    print(calculate_average([]))  # Should return 0 or None
