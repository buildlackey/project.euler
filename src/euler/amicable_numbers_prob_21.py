
from collections import defaultdict


limit = 9999
proper_divisors = defaultdict(list)

# get all factors of each number to limit
for target in range(2,limit+1):
    for candidate in range(1, limit):
        if (candidate < target and target % candidate == 0):
            proper_divisors[target].append(candidate)



print(f"proper_divisors: {proper_divisors}")

# multiply the factors to get the sum of factors for each number up to limit
proper_divisor_sums = {}
for target in range(2,limit+1):
    proper_divisor_sums[target] = sum(proper_divisors[target])


amicable_numbers = set()
for target, product_sum in proper_divisor_sums.items():
    if target != product_sum and product_sum in proper_divisor_sums:
        if (proper_divisor_sums[product_sum] == target):
            print(f"found amicable pair {target} and {product_sum}")
            amicable_numbers.add(product_sum)
            amicable_numbers.add(target)

print(f"Here are list of amicable numbers: {amicable_numbers}, and their sum: {sum(list(amicable_numbers))}")
