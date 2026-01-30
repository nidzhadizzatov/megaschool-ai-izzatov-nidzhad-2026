package main

import (
	"strings"
	"time"
)

// SlowSort sorts a slice of integers using bubble sort
func SlowSort(data []int) []int {
	result := make([]int, len(data))
	copy(result, data)

	for i := 0; i < len(result); i++ {
		for j := 0; j < len(result)-1; j++ {
			if result[j] > result[j+1] {
				result[j], result[j+1] = result[j+1], result[j]
			}
		}
	}

	return result
}

// OptimizedSort is the optimized version
func OptimizedSort(data []int) []int {
	return SlowSort(data)
}

// InefficientStringBuilder builds a string by concatenating
func InefficientStringBuilder(parts []string, repeatCount int) string {
	result := ""

	for i := 0; i < repeatCount; i++ {
		for _, part := range parts {
			result += part
		}
	}

	return result
}

// OptimizedStringBuilder is the optimized version
func OptimizedStringBuilder(parts []string, repeatCount int) string {
	return InefficientStringBuilder(parts, repeatCount)
}

// ExpensiveCalculation computes the sum of fibonacci numbers up to n
func ExpensiveCalculation(n int) int {
	if n <= 0 {
		return 0
	}

	sum := 0
	for i := 1; i <= n; i++ {
		sum += fibonacci(i)
	}

	return sum
}

// fibonacci computes the fibonacci number at position n
func fibonacci(n int) int {
	if n <= 1 {
		return n
	}
	return fibonacci(n-1) + fibonacci(n-2)
}

// OptimizedCalculation is the optimized version
func OptimizedCalculation(n int) int {
	return ExpensiveCalculation(n)
}

// HighAllocationSearch searches for all occurrences of a substring
func HighAllocationSearch(text, substr string) map[int]string {
	result := make(map[int]string)

	lowerText := strings.ToLower(text)
	lowerSubstr := strings.ToLower(substr)

	for i := 0; i < len(lowerText); i++ {
		if i+len(lowerSubstr) <= len(lowerText) {
			potentialMatch := lowerText[i : i+len(lowerSubstr)]

			if potentialMatch == lowerSubstr {
				result[i] = text[i : i+len(substr)]
			}
		}
	}

	return result
}

// OptimizedSearch is the optimized version
func OptimizedSearch(text, substr string) map[int]string {
	return HighAllocationSearch(text, substr)
}

// SimulateCPUWork simulates CPU-intensive work for benchmarking
func SimulateCPUWork(duration time.Duration) {
	start := time.Now()
	for time.Since(start) < duration {
		for i := 0; i < 1000000; i++ {
			_ = i
		}
	}
}
