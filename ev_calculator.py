from queries import get_legs_by_parlay, update_parlay_odds

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

def evaluate_parlay(parlay_id):
    legs = get_legs_by_parlay(parlay_id)  #fetch all legs in the parlay

    #combined odds - based on the odds the user picked
    picked_odds_list = [leg['odds_at_pick'] for leg in legs]  # get odds at pick for each leg
    combined_odds = calculate_combined_odds(picked_odds_list)  # calculate combined odds for the parlay

    #combined implied probability - multiply each leg's implied probability together
    combined_implied_probability = 1
    for leg in legs:
        implied = calculate_implied_probability(leg['odds_at_pick'])
        combined_implied_probability *= implied
    
    #combined true probability - multiply each leg's no-vig true probability together
    combined_true_probability = 1
    for leg in legs:
        true_prob = calculate_true_probability(leg['odds_at_pick'], leg['opponent_odds'])
        combined_true_probability *= true_prob
    
    # ev using the combined true probability against combined decimal odds
    ev = calculate_ev(combined_true_probability, combined_odds)

    #save results back to the parlay row
    update_parlay_odds(
        parlay_id,
        combined_odds,
        combined_implied_probability,
        combined_true_probability,
        ev,
        ai_explanation=None,        #filled in later once GenAI exists
        status='pending'
    )

    return{
        "combined_odds" : combined_odds,
        "implied_probability" : combined_implied_probability,
        "true_probability" : combined_true_probability,
        "ev_value" : ev
    }



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

    result = evaluate_parlay(1)
    print("Evaluation result:", result)