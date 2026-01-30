/**
 * Simple calculator utility
 * @module calculator
 */

/**
 * Calculate sum of array elements
 * @param {number[]} numbers - Array of numbers to sum
 * @returns {number} Sum of all numbers
 */
function calculateSum(numbers) {
    let sum = 0;
    for (let i = 0; i < numbers.length; i++) {
        sum += numbers[i];
    }
    return sum;
}

/**
 * Calculate average of array elements
 * @param {number[]} numbers - Array of numbers
 * @returns {number} Average value
 */
function calculateAverage(numbers) {
    const sum = calculateSum(numbers);
    return sum / numbers.length;
}

/**
 * Find maximum value in array
 * @param {number[]} numbers - Array of numbers
 * @returns {number} Maximum value
 */
function findMax(numbers) {
    let max = numbers[0];
    for (let i = 1; i < numbers.length; i++) {
        if (numbers[i] > max) {
            max = numbers[i];
        }
    }
    return max;
}

module.exports = {
    calculateSum,
    calculateAverage,
    findMax
};