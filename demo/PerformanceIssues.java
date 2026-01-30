import java.util.*;
import java.util.stream.*;

public class PerformanceIssues {
    
    // Inefficient sorting using bubble sort O(n^2)
    public static List<Integer> slowSort(List<Integer> data) {
        List<Integer> result = new ArrayList<>(data);
        
        for (int i = 0; i < result.size(); i++) {
            for (int j = 0; j < result.size() - 1; j++) {
                if (result.get(j) > result.get(j + 1)) {
                    int temp = result.get(j);
                    result.set(j, result.get(j + 1));
                    result.set(j + 1, temp);
                }
            }
        }
        
        return result;
    }
    
    // Optimized version that uses Arrays.sort() for O(n log n)
    public static List<Integer> optimizedSort(List<Integer> data) {
        List<Integer> result = new ArrayList<>(data);
        Collections.sort(result);
        return result;
    }
    
    // Inefficient string concatenation in loop
    public static String inefficientStringBuilder(List<String> parts, int repeatCount) {
        StringBuilder result = new StringBuilder();
        
        for (int i = 0; i < repeatCount; i++) {
            for (String part : parts) {
                result.append(part);
            }
        }
        
        return result.toString();
    }
    
    // Optimized version that uses StringBuilder
    public static String optimizedStringBuilder(List<String> parts, int repeatCount) {
        StringBuilder result = new StringBuilder();
        
        for (int i = 0; i < repeatCount; i++) {
            for (String part : parts) {
                result.append(part);
            }
        }
        
        return result.toString();
    }
    
    // Expensive calculation with redundant recursive calls
    public static int expensiveCalculation(int n) {
        if (n <= 0) {
            return 0;
        }
        
        int sum = 0;
        for (int i = 1; i <= n; i++) {
            sum += fibonacci(i);
        }
        
        return sum;
    }
    
    // Optimized fibonacci using memoization
    private static int fibonacci(int n, int[] memo) {
        if (n <= 1) {
            return n;
        }
        if (memo[n] != 0) {
            return memo[n];
        }
        memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo);
        return memo[n];
    }
    
    // Wrapper for optimized fibonacci
    public static int optimizedCalculation(int n) {
        int[] memo = new int[n + 1];
        return expensiveCalculation(n, memo);
    }
    
    // Memory-intensive search with excessive allocations
    public static Map<Integer, String> highAllocationSearch(String text, String substr) {
        Map<Integer, String> result = new HashMap<>();
        
        String lowerText = text.toLowerCase();
        String lowerSubstr = substr.toLowerCase();
        
        for (int i = 0; i <= lowerText.length() - lowerSubstr.length(); i++) {
            if (lowerText.startsWith(lowerSubstr, i)) {
                result.put(i, text.substring(i, i + substr.length()));
            }
        }
        
        return result;
    }
    
    // Optimized version that avoids excessive allocations
    public static Map<Integer, String> optimizedSearch(String text, String substr) {
        Map<Integer, String> result = new HashMap<>();
        
        String lowerText = text.toLowerCase();
        String lowerSubstr = substr.toLowerCase();
        
        for (int i = 0; i <= lowerText.length() - lowerSubstr.length(); i++) {
            if (lowerText.startsWith(lowerSubstr, i)) {
                result.put(i, text.substring(i, i + substr.length()));
            }
        }
        
        return result;
    }
    
    // Inefficient collection filtering using multiple passes
    public static List<Integer> filterAndTransform(List<Integer> numbers) {
        List<Integer> result = new ArrayList<>();
        
        // Using streams for single pass filtering and transforming
        result = numbers.stream()
            .filter(num -> num % 2 == 0)
            .map(num -> num * num)
            .filter(num -> num > 100)
            .collect(Collectors.toList());
        
        return result;
    }
    
    // Optimized version that uses streams
    public static List<Integer> optimizedFilterAndTransform(List<Integer> numbers) {
        return filterAndTransform(numbers);
    }
    
    // Synchronization bottleneck with coarse-grained locking
    private static final Object lock = new Object();
    private static int sharedCounter = 0;
    
    public static void incrementCounter(int times) {
        for (int i = 0; i < times; i++) {
            synchronized(lock) {
                sharedCounter++;
            }
        }
    }
    
    public static int getCounter() {
        synchronized(lock) {
            return sharedCounter;
        }
    }
    
    public static void resetCounter() {
        synchronized(lock) {
            sharedCounter = 0;
        }
    }
}