// algorithms.cpp
#include <vector>
#include <iostream>

std::vector<int> buildPrefixSum(const std::vector<int>& arr) {
    int n = arr.size();
    std::vector<int> prefix(n + 1);
    prefix[0] = 0; // Initialize the first element
    for (int i = 1; i <= n; i++) {
        prefix[i] = prefix[i - 1] + arr[i - 1];
    }
    return prefix;
}

int binarySearch(const std::vector<int>& arr, int target) {
    int left = 0;
    int right = arr.size() - 1; // Corrected to size() - 1
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
    return -1; // Target not found
}

int main() {
    // Test cases
    std::vector<int> arr = {1, 2, 3, 4, 5};
    std::vector<int> prefix = buildPrefixSum(arr);
    for (int i = 0; i < prefix.size(); i++) {
        std::cout << prefix[i] << " ";
    }
    std::cout << std::endl;
    int index = binarySearch(arr, 3);
    std::cout << "Index of 3: " << index << std::endl;
    return 0;
}