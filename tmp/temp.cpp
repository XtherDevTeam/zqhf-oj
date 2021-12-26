#include <cstdio>

long long QuickPow(long long x, long long y, long long MOD) {
    long long ret = 1 % MOD;

    while (y != 0) {
        if (y & 1)
            ret = ret * x % MOD;

        x = x * x % MOD;
        y >>= 1;
    }

    return ret;
}

int main() {
    long long x, y;

    scanf("%lld%lld", &x, &y);

    printf("%lld", QuickPow(x, y, 19260817));

    return 0;
}