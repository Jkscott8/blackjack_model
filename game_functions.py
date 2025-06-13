import random
import time
import joblib
import numpy as np
import warnings
warnings.filterwarnings('ignore')

hit_model = joblib.load('blackjack_hit_prob_model.joblib')
stay_model = joblib.load('blackjack_stay_prob_model.joblib')


class Playing_card(object):
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def display_card(self):
        return str(self)

    def value(self):
        if isinstance(self.rank, int):
            return self.rank
        elif self.rank in ["Jack", "Queen", "King"]:
            return 10
        elif self.rank == "Ace":
            return 11

suits = ["♠️", "♥️", "♣️", "♦️"]
cards = [2,3,4,5,6,7,8,9,10, 'Ace', 'Jack', "Queen", "King"]

class Deck(object):
    def __init__(self):
        self.cards = self.build()

    def build(self):
        deck = []
        for rank in cards:
            for suit in suits:
                card = Playing_card(suit, rank)
                deck.append(card)
        return deck

    def show_deck(self):
        for cards in self.cards:
            print(cards.display_card())

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop() if self.cards else None

class Player(object):
    def __init__(self, name, chips=100):
        self.name = name
        self.hand = []
        self.chips = chips
        self.bet = 0

    def __str__(self):
        return f"{self.name}"

    def bet_chips(self, amount):
        if amount <= self.chips:
            self.bet = amount
            self.chips = self.chips - amount
            return True
        else:
            print("You don't have enough chips")
            return False

    def win_bet(self, multiplier):
        winnings = self.bet * multiplier
        self.chips += winnings
        self.bet = 0


    def draw_card(self, deck):
        card = deck.draw()
        if card:
            self.hand.append(card)

    def show_hand(self):
        return ', '.join(card.display_card() for card in self.hand)

    def score(self, return_soft=False):
        score = sum(card.value() for card in self.hand)
        aces = sum(1 for card in self.hand if card.rank == 'Ace')
        is_soft = False
        while score > 21 and aces:
            score -= 10
            aces -= 1
        if aces > 0:  # After adjustment, if an Ace still counts as 11, it's soft
            is_soft = True
        return (score, is_soft) if return_soft else score


def Hit(player, deck):
    player.draw_card(deck)
    time.sleep(1)
    print(f"{player} now has: {player.show_hand()} (Score: {player.score()})")


def model_predict(player, dealer, model):
    # Prepare features exactly like training
    features = np.array([[player.hand[0].value(),
                          player.hand[1].value(),
                          player.score(),
                          int(player.score(return_soft=True)[1]),  # is_soft
                          sum(1 for c in player.hand if c.rank == 'Ace'),  # num_aces
                          dealer.hand[0].value()]])

    outcome_pred = model.predict(features)[0]
    outcome_proba = model.predict_proba(features)[0]

    outcomes = {1: "Win", 0: "Tie", -1: "Lose"}
    return outcomes[outcome_pred], outcome_proba.max()



def Blackjack(all_players):
    deck = Deck()
    print("Shuffling Deck...")
    deck.shuffle()
    time.sleep(1)

    for player in all_players:
        player.hand = []

    dealer = Player("Dealer")

    for player in all_players:
        while True:
            try:
                player_bet = int(input(f"\n{player}, you have ${player.chips}.\n Enter your bet: "))
                if player.bet_chips(player_bet):
                    break
            except ValueError:
                print("Invalid input. Please try again.")

    for player in all_players:
        player.draw_card(deck)
        player.draw_card(deck)
        print(f"\n{player} has: {player.show_hand()} (Score: {player.score()})")
        time.sleep(2)

    dealer.draw_card(deck)
    dealer.draw_card(deck)
    print(f'\nDealer Shows: {dealer.hand[0].display_card()}')

    for player in all_players:
        while True:
            if player.score() == 21:
                print(f'{player} has Blackjack!')
                time.sleep(1)
                break

            hit_pred, hit_conf = model_predict(player, dealer, hit_model)
            stay_pred, stay_conf = model_predict(player, dealer, stay_model)

            time.sleep(1)
            print(f"\nML Predictions:")
            time.sleep(1)
            print(f" - If you HIT, predicted outcome: {hit_pred} ({hit_conf * 100:.1f}% confidence)")
            time.sleep(1)
            print(f" - If you STAY, predicted outcome: {stay_pred} ({stay_conf * 100:.1f}% confidence)")
            time.sleep(1)

            x = input(f"\n{player} Hit(1) or Stay(2): ")
            if x == "1":
                Hit(player, deck)
                if player.score() > 21:
                    time.sleep(1)
                    print(f"{player} Busts")
                    break
            elif x == "2":
                time.sleep(1)
                break
            else:
                print("Invalid input, enter 1 or 2\n")

    print(f'\nDealer Has: {dealer.show_hand()} (Score:{dealer.score()})')
    time.sleep(1)
    while True:
        dealer_score, dealer_is_soft = dealer.score(return_soft=True)
        if dealer_score < 17:
            Hit(dealer, deck)
        elif dealer_score == 17 and dealer_is_soft:
            Hit(dealer, deck)  # Hit if soft 17
        else:
            break

    if dealer.score() > 21:
        time.sleep(1)
        print(f"{dealer.name} Busts\n")
    else:
        time.sleep(1)
        print(f"{dealer.name} Stays with {dealer.score()}.\n")

    for player in all_players:
        time.sleep(1)
        if player.score() > 21:
            player.win_bet(0)
            print(f"{player.name} Busts, {player.score()} - loses. Chips now: ${player.chips}")
        elif dealer.score() > 21 or player.score() > dealer.score():
            if player.score() == 21 and len(player.hand) == 2:
                player.win_bet(2.5)
                print(f"Blackjack, {player.name} Wins! Chips now: ${player.chips}")
            else:
                player.win_bet(2)
                print(f"{player.name} Wins with {player.score()} vs Dealer's {dealer.score()}. Chips now: ${player.chips}")
        elif player.score() == dealer.score():
            player.win_bet(1)
            print(f"{player.name} Push (tie) with {player.score()}. Chips now: ${player.chips}")
        else:
            player.win_bet(0)
            print(f"{player.name} Loses with {player.score()} vs Dealer's {dealer.score()}. Chips now: ${player.chips}")

def start_game():
    player_names = []
    num_players = int(input("How many players would you like to play?: "))
    for i in range(num_players):
        name = input(f"Enter Player {i+1}: ")
        player_names.append(name)
    all_players = [Player(name) for name in player_names]
    while all_players:
        Blackjack(all_players)
        all_players = [player for player in all_players if player.chips > 0]
        if not all_players:
            print("All players are out of chips. Game Over :(")
            break
        again = input("Play Again? (y/n): ")
        if again.lower() != "y":
            time.sleep(1)
            for player in all_players:
                print(f"{player} cashes out with ${player.chips}!")
                time.sleep(1)
            print("Thank you for playing!")
            break
        else:
            print("Starting New Game...")

start_game()