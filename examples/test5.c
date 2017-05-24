int func1(int z) {
	int a;
	a = 1;
	return a + z;
}

int func2(void) {
	int a;
	a = 2;
	return a;
}

int func3(void) {
	int a;
	a = 4;
	return a;
}

int func4(int z, int x) {
	int a;
	{
		int b;
		b = 8;
		a = b;
	}
	{
		int b;
		b = 16;
		a = a + b;
	}
	return a + z + x;
}

int main(int z) {
	int a;
	int b;
	int c;
	a = b = c = 32;

	return func1(z) + func2() + func3() + func4(z, 10) + a + b + c;
}
