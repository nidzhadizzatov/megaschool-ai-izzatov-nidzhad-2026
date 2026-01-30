#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

/**
 * Binary Search implementation for competitive programming
 * Problem: Find first occurrence of target in sorted array
 */

int binarySearch(vector<int>& arr, int target) {
    int left = 0;
    int right = arr.size() - 1;  // Fixed: Last valid index
    
    while (left <= right) {  // Fixed: Change condition to <=
        int mid = (left + right) / 2;
        
        if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;  // Fixed: Adjust right for correct search
        }
    }
    
    if (left < arr.size() && arr[left] == target) {
        return left;
    }
    return -1;
}

/**
 * Range sum query using prefix sums
 * Problem: Calculate sum of elements in range [l, r]
 */
vector<int> buildPrefixSum(vector<int>& arr) {
    int n = arr.size();
    vector<int> prefix(n + 1, 0);
    
    for (int i = 1; i <= n; i++) {  // Fixed: Start loop from 1
        prefix[i] = prefix[i - 1] + arr[i - 1];  // Fixed: Access arr[i - 1]
    }
    
    return prefix;
}

int rangeSum(vector<int>& prefix, int left, int right) {
    return prefix[right + 1] - prefix[left];
}

/**
 * Find maximum subarray sum (Kadane's algorithm)
 */
int maxSubarraySum(vector<int>& arr) {
    int maxSum = arr[0];
    int currentSum = 0;
    
    for (int num : arr) {
        currentSum = max(num, currentSum + num);
        maxSum = max(maxSum, currentSum);
    }
    
    return maxSum;
}

int main() {
    // Test binary search
    vector<int> arr1 = {1, 2, 3, 4, 5, 6, 7, 8, 9};
    cout << "Binary search for 5: " << binarySearch(arr1, 5) << endl;
    
    // Test range sum
    vector<int> arr2 = {1, 2, 3, 4, 5};
    vector<int> prefix = buildPrefixSum(arr2);
    cout << "Sum [1, 3]: " << rangeSum(prefix, 1, 3) << endl;
    
    // Test max subarray
    vector<int> arr3 = {-2, 1, -3, 4, -1, 2, 1, -5, 4};
    cout << "Max subarray sum: " << maxSubarraySum(arr3) << endl;
    
    return 0;
}