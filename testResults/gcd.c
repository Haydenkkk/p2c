#include <stdio.h>
int x, y;
int __func_gcd(int a,int b) {
	int gcd;
	if(b==0) {
		gcd=a;
	}
	else {
		gcd=__func_gcd(b,a%b);
	}
	return gcd;
}
int main() {
	scanf("%d%d", &x, &y);
	printf("%d\n", __func_gcd(x,y));
	return 0;
}
