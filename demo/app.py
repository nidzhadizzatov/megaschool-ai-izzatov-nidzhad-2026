def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0  # or return None
    return sum(numbers) / len(numbers)


# The rest of the file remains unchanged


if __name__ == "__main__":
    main()