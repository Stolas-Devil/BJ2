# Блек-джек
# От 1 до 7 игроков против дилера

import tkinter as tk
import bj_cards, os

assets_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'assets/'))

class BJ_Game:
    """ Игра в Блек-джек. """
    def __init__(self, names):      
        self.players = []
        for name in names:
            player = bj_cards.BJ_Player(name)
            self.players.append(player)

        self.dealer = bj_cards.BJ_Dealer("Дилер")

        self.deck = bj_cards.BJ_Deck()
        self.new_deal()

    @property
    def still_playing(self):
        sp = []
        for player in self.players:
            if not player.is_busted():
                sp.append(player)
        return sp

    def __additional_cards(self, player):
        while not player.is_busted() and player.is_hitting():
            self.deck.deal([player])
            print(player)
            if player.is_busted():
                player.bust()

    def new_deal(self):
        # удаление всех карт
        for player in self.players:
            player.clear()
        self.dealer.clear()
        # сдача всем по две карты и пополнение колоды
        self.deck.clear()
        self.deck.populate()
        self.deck.populate()
        self.deck.populate()
        self.deck.populate()
        self.deck.shuffle()
        self.deck.deal(self.players + [self.dealer], per_hand = 2)
        self.dealer.flip_first_card()    

    def play(self):
        # сдача всем по две карты
        self.deck.deal(self.players + [self.dealer], per_hand = 2)
        self.dealer.flip_first_card()    
        # первая из карт, сданных дилеру, переворачивается
        for player in self.players:
            print(player)
        print(self.dealer)

        # сдача дополнительных карт игрокам
        for player in self.players:
            self.__additional_cards(player)

        self.dealer.flip_first_card()    # первая карта дилера раскрывается

        if not self.still_playing:
            # все игроки перебрали, покажем только "руку" дилера
            print(self.dealer)
        else:
            # сдача дополнительных карт дилеру
            print(self.dealer)
            self.__additional_cards(self.dealer)

            if self.dealer.is_busted():
                # выигрывают все, кто еще остался в игре
                for player in self.still_playing:
                    player.win()                    
            else:
                # сравниваем суммы очков у дилера и у игроков, оставшихся в игре
                for player in self.still_playing:
                    if player.total > self.dealer.total:
                        player.win()
                    elif player.total < self.dealer.total:
                        player.lose()
                    else:
                        player.push()

        # удаление всех карт
        for player in self.players:
            player.clear()
        self.dealer.clear()

    def player_hit(self, player):    
        if not player.is_busted():
            self.deck.deal([player])

    def get_winner_names(self):
        winners = []
        if self.dealer.is_busted():
            # выигрывают все, кто еще остался в игре
            for player in self.still_playing:
                winners.append(player.name)
        else:
            # сравниваем суммы очков у дилера и у игроков, оставшихся в игре
            for player in self.still_playing:
                if player.total > self.dealer.total:
                    winners.append(player.name)
            if not winners:
                winners.append(self.dealer.name)
        return winners

class GameScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack")
        self.geometry("800x640")
        self.resizable(False, False)
        
        self.CARD_ORIGINAL_POSITION = 100
        self.CARD_WIDTH_OFFSET = 100

        self.PLAYER_CARD_HEIGHT = 300
        self.DEALER_CARD_HEIGHT = 100

        self.PLAYER_SCORE_TEXT_COORDS = (400, 450)
        self.WINNER_TEXT_COORDS = (400, 200)

        self.game_state = BJ_Game(['Игрок ' + str(i+1) for i in range(3)])
        
        self.player = self.game_state.players[0]
        self.dealer = self.game_state.dealer

        self.game_screen = tk.Canvas(self, width=800, height=500, bg="white")

        self.bottom_frame = tk.Frame(self, width=800, height=140, bg="red")
        self.bottom_frame.pack_propagate(0)

        self.hit_button = tk.Button(self.bottom_frame, text="Карту", width=25, command=self.hit)
        self.stick_button = tk.Button(self.bottom_frame, text="Пас", width=25, command=self.stick)
        self.play_again_button = tk.Button(self.bottom_frame, text="Новая игра", width=25, command=self.play_again)
        self.quit_button = tk.Button(self.bottom_frame, text="Выход", width=25, command=self.end_game)

        self.hit_button.pack(side=tk.LEFT, padx=(100, 200))
        self.stick_button.pack(side=tk.LEFT)

        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.game_screen.pack(side=tk.LEFT, anchor=tk.N)

        self.display_table()

    def display_table(self):
        player_card_images = [card.get_image() for card in self.player.cards]
        dealer_card_images = [card.get_image() for card in self.dealer.cards]

        self.game_screen.delete("all")
        self.tabletop_image = tk.PhotoImage(file=assets_folder + "/tabletop.png")
        self.game_screen.create_image((400, 250), image=self.tabletop_image)

        for card_number, card_image in enumerate(player_card_images):
            self.game_screen.create_image(
                (self.CARD_ORIGINAL_POSITION + self.CARD_WIDTH_OFFSET * card_number, self.PLAYER_CARD_HEIGHT),
                image=card_image
            )

        for card_number, card_image in enumerate(dealer_card_images):
            self.game_screen.create_image(
                (self.CARD_ORIGINAL_POSITION + self.CARD_WIDTH_OFFSET * card_number, self.DEALER_CARD_HEIGHT),
                image=card_image
           )

        score = str(self.player.total)
        if self.player.is_busted():
            score += ' ПЕРЕБОР!!!'
        self.game_screen.create_text(self.PLAYER_SCORE_TEXT_COORDS, text=score, font=(None, 20))

        self.center_message = self.game_screen.create_text(
            self.WINNER_TEXT_COORDS, text=self.player.name, font=(None, 30))

    def hit(self):
        self.game_state.player_hit(self.player)
        self.display_table()
        if self.player.is_busted():
            self.after(500, self.stick)    
    
    def stick(self):
        players = self.game_state.players
        player_index = players.index(self.player)
        if player_index < len(players) - 1:
            self.player = players[player_index + 1]        
            self.display_table()
        else:
            self.dealer.flip_first_card()
            self.display_table()
            if self.game_state.still_playing:
                self.after(1000, self.dealer_hit)
            else:
                self.show_winners()

    def dealer_hit(self):
        if not self.dealer.is_busted() and self.dealer.is_hitting():
            self.game_state.player_hit(self.dealer)
            self.display_table()
            self.after(1000, self.dealer_hit)
        else:
            self.after(500, self.show_winners)
    
    def show_winners(self):
        winner_names = self.game_state.get_winner_names()
        if len(winner_names) > 1:
            winner_text = ' '.join([s for s in winner_names]) + ' ПОБЕДИЛИ!'
        elif len(winner_names) == 1:
            winner_text = winner_names[0] + ' ПОБЕДИЛ!'
        else:
            winner_text = 'НИЧЬЯ'
        self.game_screen.itemconfigure(self.center_message, text=winner_text)
        self.show_play_again_options()
    
    def show_play_again_options(self):
        self.hit_button.pack_forget()
        self.stick_button.pack_forget()
        self.play_again_button.pack(side=tk.LEFT, padx=(100, 200))
        self.quit_button.pack(side=tk.LEFT)

    def show_gameplay_buttons(self):
        self.play_again_button.pack_forget()
        self.quit_button.pack_forget()
        self.hit_button.pack(side=tk.LEFT, padx=(100, 200))
        self.stick_button.pack(side=tk.LEFT)

    def play_again(self):
        self.show_gameplay_buttons()
        self.game_state.new_deal()
        self.player = self.game_state.players[0]
        self.display_table()

    def end_game(self):
        self.destroy()

# def main():
#     print("\t\tДобро пожаловать в игру Блек-джек!\n")
    
#     names = []
#     number = games.ask_number("Сколько всего игроков? (1 - 7): ", 
#         low = 1, high = 7)
#     for i in range(number):
#         name = input("Введите имя игрока № " + str(i + 1) + " :")
#         names.append(name)
#     print()
        
#     game = BJ_Game(names)

#     again = None
#     while again != "n":
#         game.play()
#         again = games.ask_yes_no("\nХотите сыграть еще раз")

if __name__ == "__main__":
    gs = GameScreen()
    gs.mainloop()
