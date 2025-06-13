import random
import pandas as pd

def draw_card():
    cards = [2,3,4,5,6,7,8,9,10,10,10,10,'Ace']
    return random.choice(cards)

def calculate_score(hand):
    score = 0
    aces = 0
    for card in hand:
        if card == 'Ace':
            score += 11
            aces += 1
        else:
            score += card
    while score > 21 and aces:
        score -= 10
        aces -= 1
    is_soft = aces > 0
    return score, is_soft, aces

def basic_strategy(player_score, dealer_card, is_soft):
    if is_soft:
        if player_score <= 17:
            return 1
        elif player_score == 18:
            return 0 if dealer_card in [2,7,8] else 1
        else:
            return 0
    else:
        if player_score <= 11:
            return 1
        elif 12 <= player_score <= 16:
            return 1 if dealer_card >= 7 else 0
        else:
            return 0

def dealer_play(hand):
    while True:
        score, is_soft, _ = calculate_score(hand)
        if score < 17 or (score == 17 and is_soft):
            hand.append(draw_card())
        else:
            break
    return calculate_score(hand)[0]

def play_hand(player_hand, dealer_hand):
    player_score, _, _ = calculate_score(player_hand)
    dealer_score = dealer_play(dealer_hand)

    if player_score > 21:
        return -1
    elif dealer_score > 21 or player_score > dealer_score:
        return 1
    elif player_score == dealer_score:
        return 0
    else:
        return -1

def simulate_hit_vs_stay(samples=1000000):
    data = []
    for _ in range(samples):
        initial_player_hand = [draw_card(), draw_card()]
        dealer_hand = [draw_card(), draw_card()]
        dealer_visible = 11 if dealer_hand[0]=='Ace' else dealer_hand[0]

        player_initial_score, player_is_soft, player_num_aces = calculate_score(initial_player_hand)

        stay_outcome = play_hand(initial_player_hand[:], dealer_hand[:])
        stay_final_score, _, _ = calculate_score(initial_player_hand)

        hit_player_hand = initial_player_hand[:] + [draw_card()]
        while True:
            hit_score, hit_is_soft, _ = calculate_score(hit_player_hand)
            if hit_score > 21:
                break
            if basic_strategy(hit_score, dealer_visible, hit_is_soft):
                hit_player_hand.append(draw_card())
            else:
                break
        hit_final_score, _, _ = calculate_score(hit_player_hand)
        hit_outcome = play_hand(hit_player_hand, dealer_hand[:])

        data.append({
            'player_card1': 11 if initial_player_hand[0]=='Ace' else initial_player_hand[0],
            'player_card2': 11 if initial_player_hand[1]=='Ace' else initial_player_hand[1],
            'player_initial_score': player_initial_score,
            'player_is_soft': int(player_is_soft),
            'player_num_aces': player_num_aces,
            'dealer_visible_card': dealer_visible,

            'stay_final_score': stay_final_score,
            'stay_outcome': stay_outcome,

            'hit_final_score': hit_final_score,
            'player_num_cards_hit': len(hit_player_hand),
            'hit_outcome': hit_outcome
        })

    return pd.DataFrame(data)

# Generate and save the enhanced dataset
df = simulate_hit_vs_stay(1000000)
df.to_csv('blackjack_hit_outcome_dataset.csv', index=False)
