def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def main():
    number = 10
    result = calculate_fibonacci(number)
    print(f"Fibonacci({number}) = {result}")

if __name__ == "__main__":
    main()