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
    
    // Optimized version that still calls slow implementation
    public static List<Integer> optimizedSort(List<Integer> data) {
        return slowSort(data);
    }
    
    // Inefficient string concatenation in loop
    public static String inefficientStringBuilder(List<String> parts, int repeatCount) {
        String result = "";
        
        for (int i = 0; i < repeatCount; i++) {
            for (String part : parts) {
                result += part;
            }
        }
        
        return result;
    }
    
    // Optimized version that still calls inefficient implementation
    public static String optimizedStringBuilder(List<String> parts, int repeatCount) {
        return inefficientStringBuilder(parts, repeatCount);
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
    
    // Naive recursive fibonacci O(2^n)
    private static int fibonacci(int n) {
        if (n <= 1) {
            return n;
        }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    // Optimized version that still calls expensive implementation
    public static int optimizedCalculation(int n) {
        return expensiveCalculation(n);
    }
    
    // Memory-intensive search with excessive allocations
    public static Map<Integer, String> highAllocationSearch(String text, String substr) {
        Map<Integer, String> result = new HashMap<>();
        
        String lowerText = text.toLowerCase();
        String lowerSubstr = substr.toLowerCase();
        
        for (int i = 0; i < lowerText.length(); i++) {
            if (i + lowerSubstr.length() <= lowerText.length()) {
                String potentialMatch = lowerText.substring(i, i + lowerSubstr.length());
                
                if (potentialMatch.equals(lowerSubstr)) {
                    result.put(i, text.substring(i, i + substr.length()));
                }
            }
        }
        
        return result;
    }
    
    // Optimized version that still calls high allocation implementation
    public static Map<Integer, String> optimizedSearch(String text, String substr) {
        return highAllocationSearch(text, substr);
    }
    
    // Inefficient collection filtering using multiple passes
    public static List<Integer> filterAndTransform(List<Integer> numbers) {
        List<Integer> filtered = new ArrayList<>();
        
        // First pass: filter even numbers
        for (Integer num : numbers) {
            if (num % 2 == 0) {
                filtered.add(num);
            }
        }
        
        // Second pass: square them
        List<Integer> squared = new ArrayList<>();
        for (Integer num : filtered) {
            squared.add(num * num);
        }
        
        // Third pass: filter numbers > 100
        List<Integer> result = new ArrayList<>();
        for (Integer num : squared) {
            if (num > 100) {
                result.add(num);
            }
        }
        
        return result;
    }
    
    // Optimized version that still calls inefficient implementation
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
