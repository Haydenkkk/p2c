const char pi314159265253897932384626433832795 = 3.1415;
double r, l;
double s;
int main() {
	scanf("%f", r);
	l=2*pi314159265253897932384626433832795*r;
	s=pi314159265253897932384626433832795*r*r;
	printf("%f%f\n", l, s);
	return 0;
}
int x, y, z;
int z;
void __func_s(int x,int& y) {
	x=5;
	y=6;
	z=7;
}
int main() {
	x=1;
	y=2;
	z=3;
	__func_s(x,y);
	printf("%d%d%d\n", x, y, z);
	return 0;
}
int x, y;
int __func_gcd(int a,int b) {
	int gcd;
	if(b==0) {
		gcd=a;
	}
	else {
		gcd=__func_gcd(b,amodb);
	}
	return gcd;
}
int main() {
	scanf("%d%d", x, y);
	printf("%d\n", __func_gcd(x,y));
	return 0;
}
