#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-05-10 13:53
# describe：

import random

def generate_random_number(length):
    if length <= 0:
        return ''
    
    random_number = ''.join(str(random.randint(0, 9)) for _ in range(length))
    return random_number


if __name__ == "__main__":
    random_number = generate_random_number(15)
    print(random_number)