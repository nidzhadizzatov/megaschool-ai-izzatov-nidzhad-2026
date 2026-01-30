#include <vector>
#include <iostream>

using namespace std;

// Function to build prefix sum array
void buildPrefixSum(const vector<int>& arr, vector<int>& prefix) {
    int n = arr.size();
    prefix.resize(n + 1);
    prefix[0] = 0;  // Initialize prefix[0]
    for (int i = 1; i <= n; i++) {
        prefix[i] = prefix[i - 1] + arr[i - 1];
    }
}

// Function to perform binary search
int binarySearch(const vector<int>& arr, int target) {
    int left = 0;
    int right = arr.size() - 1;  // Corrected: right should be size() - 1
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

int main() {
    // Test cases
    vector<int> arr = {1, 2, 3, 4, 5};
    vector<int> prefix;
    buildPrefixSum(arr, prefix);
    for (int i = 0; i < prefix.size(); i++) {
        cout << prefix[i] << " ";
    }
    cout << endl;
    cout << "Index of 3: " << binarySearch(arr, 3) << endl;
    return 0;
}