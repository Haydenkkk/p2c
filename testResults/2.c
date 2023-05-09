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
