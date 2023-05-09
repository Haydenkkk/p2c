int n, t, i, j;
int f[1001][1001];
int w[1001],v[1001];
int __func_max(int x,int y) {
	int max;
	if(x>y) {
		max=x;
	}
	else {
		max=y;
	}
	return max;
}
int main() {
	scanf("%d%d", &t, &n);
	for(int i = 1; i <= n; ) {
		scanf("%d%d", &w[i], &v[i]);
	}
	for(int i = 1; i <= n; ) {
		for(int j = 0; j <= t; ) {
			f[i][j]=f[i-1][j];
			if(j>=w[i]) {
				f[i][j]=__func_max(f[i-1][j-w[i]]+v[i],f[i][j]);
			}
		}
	}
	printf("%d\n", f[n][t]);
	return 0;
}
