import random

def random_numbers():
    rand_numbers = []
    for i in range(6):
        rand_numbers.append(random.randint(0, 2500))
    print(rand_numbers)
    return rand_numbers

def sum_three_numbers(number_list):
  return sum(number_list)

if __name__ == '__main__':
  rand_numbers = random_numbers()
  print(sum_three_numbers(rand_numbers[:3]))
  print(sum_three_numbers(rand_numbers[-3:]))