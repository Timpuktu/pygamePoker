COLS = 13
ROWS = 4

def get_number(index):
    return int(index % COLS)

def get_suit(index):
    return int(index / COLS)

def print_cards(cards):
    print(get_number(cards[0]), get_number(cards[1]), get_number(cards[2]), get_number(cards[3]), get_number(cards[4]))

def get_number_count(cards, number):
    temp = []
    count = 0
    for i in range(len(cards)):
        if (get_number(cards[i]) + 1) == number:
            count += 1
            temp.append(i)
    return count, temp

def get_pair_info(cards):
    indices = []
    for number in range(COLS):
        count, temp = get_number_count(cards, number + 1)
        if count > 1:
            indices.append((number + 1, temp))
    #print(indices)
    return indices

def is_continous(cards):
    cards.sort()
    #print(cards[0], cards[1], cards[2], cards[3], cards[4])

    count = 1
    for i in range(len(cards) - 1):
        count += 1 if cards[i + 1] == cards[i] + 1 else 0

    return count == len(cards)

def aces_low(cards):
    temp = [0, 0, 0, 0, 0]
    for i in range(len(cards)):
        number =  get_number(cards[i]) + 1
        temp[i] = 1 if number == 14 else number
    return temp

def aces_high(cards):
    temp = [0, 0, 0, 0, 0]
    for i in range(len(cards)):
        number = get_number(cards[i]) + 1
        temp[i] = 14 if number == 1 else number
    return temp

def is_straight(cards):
    if is_continous(aces_low(cards)):
        return -1
    elif is_continous(aces_high(cards)):
        return 1
    return 0

def is_flush(cards):
    temp = []
    count = 1
    suit = get_suit(cards[0])
    temp.append(0)
    for i in range(len(cards) - 1):
        if get_suit(cards[i + 1]) == suit:
            count += 1
            temp.append(i + 1)
    return count == len(cards), temp

def is_of_a_kind(cards, count):
    indices = get_pair_info(cards)
    if len(indices) == 1:
         if len(indices[0][1]) == count:
             return True, indices[0][1]
    return False, None

def is_royal_flush(cards):
    return is_flush(cards)[0] and is_straight(cards) > 0, [0, 1, 2, 3, 4]

def is_straight_flush(cards):
    return is_flush(cards)[0] and is_straight(cards) < 0, [0, 1, 2, 3, 4]

def is_full_house(cards):
    indices = get_pair_info(cards)
    if len(indices) == 2:
        if len(indices[0][1]) == 2 and len(indices[1][1]) == 3:
            return True, [0, 1, 2, 3, 4]
        elif len(indices[0][1]) == 3 and len(indices[1][1]) == 2:
            return True, [0, 1, 2, 3, 4]
    return False, None

def is_four_of_a_kind(cards):
    result, indices = is_of_a_kind(cards, 4)
    return result, indices

def is_three_of_a_kind(cards):
    result, indices = is_of_a_kind(cards, 3)
    return result, indices

def is_two_pairs(cards):
    indices = get_pair_info(cards)
    if len(indices) == 2:
        if len(indices[0][1]) == 2 and len(indices[1][1]) == 2:
            temp = []
            for i in range(len(indices)):
                for n in range(len(indices[i][1])):
                    temp.append(indices[i][1][n])
            return True, temp
    return False, None

def is_jacks_or_better(cards):
    indices = get_pair_info(cards)
    if len(indices) == 1:
        if len(indices[0][1]) == 2:
            #print('indices[0][0] =', indices[0][0])
            if indices[0][0] == 1:
                return True, indices[0][1]
            elif indices[0][0] >= 11 and indices[0][0] <= 13:
                return True, indices[0][1]
    return False, None
