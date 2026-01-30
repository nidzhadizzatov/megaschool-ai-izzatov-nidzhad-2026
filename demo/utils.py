// C++ code for algorithms.cpp

#include <vector>

std::vector<int> buildPrefixSum(const std::vector<int>& arr) {
    int n = arr.size();
    std::vector<int> prefix(n + 1);
    prefix[0] = 0;  // Initialize prefix[0]
    for (int i = 1; i <= n; i++) {
        prefix[i] = prefix[i - 1] + arr[i - 1];
    }
    return prefix;
}

int binarySearch(const std::vector<int>& arr, int target) {
    int left = 0;
    int right = arr.size() - 1;  // Fixed: should be size() - 1
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;  // Not found
}