#include <vector>

void buildPrefixSum(const std::vector<int>& arr, std::vector<int>& prefix) {
    int n = arr.size();
    prefix.resize(n + 1);
    prefix[0] = 0;  // Initialize prefix[0]
    for (int i = 1; i <= n; i++) {
        prefix[i] = prefix[i - 1] + arr[i - 1];
    }
}

int binarySearch(const std::vector<int>& arr, int target) {
    int left = 0;
    int right = arr.size() - 1;  // Corrected to last valid index
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
    return -1;  // Target not found
}