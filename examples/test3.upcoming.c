typedef enum { false, true } bool;
int a;

void myFunc(float a, int b, bool c) {
	a = 2.0;
	{
		bool c;
		c = false;
		if (c) {
			return;
		}
	}
	while (b > 0) {
		b = b - 1;
		if (b == 5) {
			break;
		}
	}
}

int main(void) {
	a = (3);
	myFunc(1.0, 2, true);
	return a;
}