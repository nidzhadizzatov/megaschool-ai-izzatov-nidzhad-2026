def factorial(n):
    if n < 0:
        raise ValueError("Input must be a non-negative integer")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    try:
        factorial(-1)
    except ValueError:
        pass  # Expected behavior
    else:
        assert False, "ValueError not raised"

    assert factorial(3) == 6


test_factorial()