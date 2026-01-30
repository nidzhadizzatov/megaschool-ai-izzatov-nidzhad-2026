// demo/calculator.js

function calculateSum(numbers) {
    let sum = 0;
    for (let i = 0; i < numbers.length; i++) { // Changed from <= to <
        sum += numbers[i];
    }
    return sum;
}

// Example usage:
console.log(calculateSum([1, 2, 3])); // Outputs: 6
console.log(calculateSum([])); // Outputs: 0
