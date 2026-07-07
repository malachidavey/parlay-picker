
def calculate_implied_probability(odds):
    if odds < 0:                                # negative odds
        return abs(odds) / (abs(odds) + 100)    # probability = |odds| / (|odds| + 100)
    else:                                       # positive odds
        return 100 / (odds + 100)               # probability = 100 / (odds + 100)

def calculate_combined_odds(list_of_odds):
    combined_decimal = 1                        # start at 1 since multiplication
    for odds in list_of_odds:                   
        decimal = american_to_decimal(odds)     # convert each leg to decimal
        combined_decimal *= decimal             # multiply all legs' decimal odds together
    return combined_decimal                     # return overal combined odds in decimal form

def calculate_true_probability(odds_side_a, odds_side_b):
    implied_a = calculate_implied_probability(odds_side_a)  # calculate implied probability for side A
    implied_b = calculate_implied_probability(odds_side_b)  # calculate implied probability for side B
    true_probability_a = implied_a / (implied_a + implied_b)    # calculate true probability for side A using the formula: true_prob_a = implied_a / (implied_a + implied_b)
    return true_probability_a


def calculate_ev(true_probability, combined_odds):
    profit_if_win = combined_odds - 1                     # calculate profit if win
    ev = (true_probability * profit_if_win) - (1 - true_probability) # calculate ev using the formula
    return ev

def american_to_decimal(odds):
    if odds < 0:                        # negative odds = favorite
        return (100 / abs(odds)) + 1
    else:                               # positive odds = underdog
        return (odds / 100) + 1

if __name__ == "__main__":
    print(calculate_implied_probability(-110))
    print(calculate_implied_probability(150))
    print(calculate_implied_probability(-200))
    print(calculate_implied_probability(300))

    print(american_to_decimal(-110))
    print(american_to_decimal(150))
    print(american_to_decimal(-200))

    print(calculate_combined_odds([-110,150]))
    print(calculate_combined_odds([-110,150,-200]))

    print(calculate_true_probability(-150, 130))
    print(calculate_true_probability(-110, -110))

    print(calculate_ev(0.15, 7.16))
    print(calculate_ev(0.60, 1.5))
    print(calculate_ev(0.90, 3.0))