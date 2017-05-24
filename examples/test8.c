typedef enum { false, true } bool;

int main(int z) {
	bool b;

	b = z > 0;
	b = b || z >= 2;

    b = !b;
	return b;
}