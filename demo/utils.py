def calculate_average(numbers: list) -> float:
    """Calculates the average of a list of numbers.
    
    Args:
        numbers: A list of numbers to calculate the average of.
    
    Returns:
        The average of the numbers, or 0 if the list is empty.
    """
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

