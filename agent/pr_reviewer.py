// demo/calculator.js

function calculateSum(numbers) {
    let sum = 0;
    // Corrected the loop condition from <= to <
    for (let i = 0; i < numbers.length; i++) {
        sum += numbers[i];
    }
    return sum;
}

// Example usage
console.log(calculateSum([1, 2, 3])); // Outputs: 6
console.log(calculateSum([])); // Outputs: 0
