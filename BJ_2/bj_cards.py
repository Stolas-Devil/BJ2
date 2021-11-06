import tkinter as tk
import os

assets_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'assets/'))

class Card:
    """ Одна игральная карта. """
    RANKS = ["01", "02", "03", "04", "05", "06", "07",
             "08", "09", "10", "11", "12", "13"]
    SUITS = ['c', 'd', 'h', 's'] # ♠ ♣ ♥ ♦
    
    def __init__(self, rank, suit):
        self.rank = rank 
        self.suit = suit

    def __str__(self):
        rep = self.rank + self.suit
        return rep

class Unprintable_Card(Card):
    """ Карта, номинал и масть которой не могут быть выведены на экран. """
    def __str__(self):
        return "<нельзя напечатать>"


class Positionable_Card(Card):
    """ Карта, которую можно положить лицом или рубашкой вверх. """
    def __init__(self, rank, suit, face_up = True):
        super(Positionable_Card, self).__init__(rank, suit)
        self.is_face_up = face_up

    def __str__(self):
        if self.is_face_up:
            rep = super(Positionable_Card, self).__str__()
        else:
            rep = "XX"
        return rep

    def flip(self):
        self.is_face_up = not self.is_face_up

    def get_image(self):
        if self.is_face_up:
            self.img = tk.PhotoImage(file=assets_folder + '/' + self.suit + self.rank + ".png")
        else:
            self.img = tk.PhotoImage(file=assets_folder + "/back.png")
        return self.img    

class Hand:
    """ Рука: набор карт на руках у одного игрока. """
    def __init__(self):
        self.cards = []

    def __str__(self):
        if self.cards:
           rep = ""
           for card in self.cards:
               rep += str(card) + "\t"
        else:
            rep = "<пусто>"
        return rep

    def clear(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def give(self, card, other_hand):
        self.cards.remove(card)
        other_hand.add(card)

class Deck(Hand):
    """ Колода игральных карт. """
    def populate(self):
        for suit in Card.SUITS:
            for rank in Card.RANKS: 
                self.add(Card(rank, suit))

    def shuffle(self):
        import random
        random.shuffle(self.cards)

    def deal(self, hands, per_hand = 1):
        for rounds in range(per_hand):
            for hand in hands:
                if self.cards:
                    top_card = self.cards[0]
                    self.give(top_card, hand)
                else:
                    print("Не могу больше сдавать: карты закончились!")

class BJ_Card(Positionable_Card):
    """ Карта для игры в Блек-джек. """
    ACE_VALUE = 1

    @property
    def value(self):
        if self.is_face_up:
            v = BJ_Card.RANKS.index(self.rank) + 1
            if v > 10:
                v = 10
        else:
            v = None
        return v

class BJ_Deck(Deck):
    """ Колода для игры в Блек-джек. """
    def populate(self):
        for suit in BJ_Card.SUITS: 
            for rank in BJ_Card.RANKS: 
                self.cards.append(BJ_Card(rank, suit))
    

class BJ_Hand(Hand):
    """ Рука игрока в Блек-джек. """
    def __init__(self, name):
        super(BJ_Hand, self).__init__()
        self.name = name

    def __str__(self):
        rep = self.name + ":\t" + super(BJ_Hand, self).__str__()  
        if self.total:
            rep += "(" + str(self.total) + ")"        
        return rep

    @property     
    def total(self):
        # если у одной из карт value равно None, 
        # то и все свойство равно None
        for card in self.cards:
            if not card.value:
                return None
        
        # суммируем очки, считая каждый туз за 1 очко
        # определяем, есть ли туз на руках у игрока
        t = 0
        contains_ace = False
        for card in self.cards:
            t += card.value
            if card.value == BJ_Card.ACE_VALUE:
                contains_ace = True
                
        # если на руках есть туз и сумма очков не превышает 11, 
        # будем считать туз за 11 очков
        if contains_ace and t <= 11:
            # прибавить нужно лишь 10, 
            # потому что единица уже вошла в общую сумму
            t += 10   
                
        return t

    def is_busted(self):
        return self.total > 21


class BJ_Player(BJ_Hand):
    """ Игрок в Блек-джек. """
    def is_hitting(self):
        response = games.ask_yes_no("\n" + self.name + 
            ", будете брать еще карты")
        return response == "y"

    def bust(self):
        print(self.name, "перебрал(а).")
        self.lose()

    def lose(self):
        print(self.name, "проиграл(а).")

    def win(self):
        print(self.name, "выиграл(а).")

    def push(self):
        print(self.name, "сыграл(а) с дилером вничью.")

        
class BJ_Dealer(BJ_Hand):
    """ Дилер в Блек-джек. """
    def is_hitting(self):
        return self.total < 17

    def bust(self):
        print(self.name, "перебрал.")

    def flip_first_card(self):
        first_card = self.cards[0]
        first_card.flip()

if __name__ == "__main__":
    print("Вы запустили модуль bj_cards, а не импортировали его (import bj_cards).")
    input("\n\nНажмите Enter, чтобы выйти.")