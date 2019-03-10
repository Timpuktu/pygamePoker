
import math, random, pygame, sys, string, poker_logic
from pygame.locals import *

#CONSTANTS
BG_COLOR = (128, 128, 128, 255) # Application background color

SCREEN_WIDTH = 640              # Width of application window
SCREEN_HEIGHT = 480             # Height of application window

FPS = 30                        # Frames Per Second

SECOND = 1000

#Card scale, width and height
CARD_SCALE = 4
CARD_WIDTH = 16 * CARD_SCALE
CARD_HEIGHT = 24 * CARD_SCALE

#Max cards in deck
MAX_CARDS = 52

#Card position X & Y, margin and holding y offset
CARD_X = SCREEN_WIDTH / 2 - CARD_WIDTH / 2
CARD_Y = SCREEN_HEIGHT / 2 - CARD_HEIGHT / 2 + 60
CARD_MARGIN = 10
CARD_Y_HOLD = 24

#Number of cards in hand
CARDS_IN_HAND = 5

#Button scale, width, height and margin
BUTTON_SCALE = 4
BUTTON_WIDTH = 32 * BUTTON_SCALE
BUTTON_HEIGHT = 16 * BUTTON_SCALE
BUTTON_MARGIN = 10

#Number scale, width, height and margin
NUMBER_SCALE = 4
NUMBER_WIDTH = 5 * NUMBER_SCALE
NUMBER_HEIGHT = 8 * NUMBER_SCALE
NUMBER_MARGIN = 2

#Letter scale, width, height and margin
LETTER_SCALE = 4
LETTER_WIDTH = 5 * LETTER_SCALE
LETTER_HEIGHT = 5 * LETTER_SCALE
LETTER_MARGIN = 2

PRICE_SCALE = 4
PRICE_WIDTH = 77 * PRICE_SCALE
PRICE_HEIGHT = 8 * PRICE_SCALE

PRICES = [0, 1, 2, 4, 8, 12, 16, 24, 32, 44]

#Max bet value and offset from bet text
MAX_BET = 10
BET_OFFSET = 10

#Game states
STATE_BEGIN = 1
STATE_DRAW = 2
STATE_RESULT = 3

#Current game state
game_state = STATE_BEGIN

cards = []              #Current cards in hand
cards_in_hold = []      #Current cards to hold
cards_visible = []      #Which cards in hand are visible
free_cards = []         #Free cards in deck

card_delay = 1 * SECOND #Delay to wait until draw
card_timer = 0          #Card draw timer
draw_cards = False      #Do we draw cards

result_string = ''      #What is the result (human readable string)
result_value = -1       #How much money we won
result_show = False     #Are results visible

#Initialize cards
def init_cards():
    for i in range(CARDS_IN_HAND):
        cards.append(0)
        cards_in_hold.append(False)
        cards_visible.append(False)
    for i in range(MAX_CARDS):
        free_cards.append(True)

#Reset cards
def reset_cards():
    for i in range(CARDS_IN_HAND):
        cards[i] = 0
        cards_visible[i] = False
        cards_in_hold[i] = False
    for i in range(MAX_CARDS):
        free_cards[i] = True

#Get card inner rect
def get_card_rect(index):
    return Rect(poker_logic.get_number(index) * CARD_WIDTH, poker_logic.get_suit(index) * CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT)

#Get card y position
def get_card_y(index):
    return CARD_Y - CARD_Y_HOLD if cards_in_hold[index] else CARD_Y

#Get card world rect
def get_card_world_rect(index):
    return Rect((CARD_X - ((CARDS_IN_HAND / 2) * CARD_WIDTH)) + index * CARD_WIDTH + index * CARD_MARGIN, get_card_y(index), CARD_WIDTH, CARD_HEIGHT)

#return index of card position collided, -1 if no card found
def pick_card(x, y):
    for i in range(CARDS_IN_HAND):
        rect = get_card_world_rect(i)
        if rect.collidepoint(x, y):
            return i
    return -1

#Get card image (Face or Back)
#Return Surface
def get_card_image(index):
    return cards_img if cards_visible[index] else cards_back_img

#Get free card index and set selected not free
#Return n..MAX_CARDS if found else -1
def get_free_card_index():
    tries = 0
    while True:
        index = random.randrange(0, MAX_CARDS)
        if free_cards[index]:
            #Free card found, se it not free and return index
            free_cards[index] = False
            return index
        else: tries += 1
        if tries > MAX_CARDS:
            break
    #No free card found
    return -1

#Set all cards visibility status
def set_cards_visible(state):
    for i in range(CARDS_IN_HAND):
        cards_visible[i] = state

#Scale source image
#Return Surface
def load_image_scaled(source, scale):
    image = pygame.Surface((source.get_width() * scale, source.get_height() * scale))
    pygame.transform.scale(source, (source.get_width() * scale, source.get_height() * scale), image)
    return image

#Check if position is inside given rect
#Return bool
def pick_rect(rect, x, y):
    return rect.collidepoint(x, y)

#Render number at x,y position
def render_number(number, x, y):
    number_string = str(abs(number))
    for i in range(len(number_string)):
        index = int(number_string[i])
        DISPLAYSURF.blit(numbers_img, (x + i * NUMBER_WIDTH + i * NUMBER_MARGIN, y), Rect(index * NUMBER_WIDTH, 0, NUMBER_WIDTH, NUMBER_HEIGHT))

#Render text at x,y position
def render_text(text, x, y):
    for i in range(len(text)):
        index = ord(text[i]) - 97
        if index >= 0:
            DISPLAYSURF.blit(letters_img, (x + i * LETTER_WIDTH + i * LETTER_MARGIN, y), Rect(index * LETTER_WIDTH, 0, LETTER_WIDTH, LETTER_HEIGHT))

#Draw card if not in hold
def draw_card(index):
    if not cards_in_hold[index]: cards[index] = get_free_card_index()

#Begin round
def begin_round():
    for i in range(CARDS_IN_HAND):
        draw_card(i)
        cards_visible[i] = True
        cards_in_hold[i] = False

#Process results
#Return tuple
#   result_value - How much we won
#   result_string - human readable result
#   indices - indices of winning cards
#   result_index - used by prices UI
def process_results(bet):
    #cards = [0, 9, 10, 11, 12]
    poker_logic.print_cards(cards)
    straight = poker_logic.is_straight(cards)

    if poker_logic.is_royal_flush(cards)[0]:
        return(PRICES[9], 'Royal flush', poker_logic.is_royal_flush(cards)[1], 9)
    elif poker_logic.is_straight_flush(cards)[0]:
        return(PRICES[8], 'Straight flush', poker_logic.is_straight_flush(cards)[1], 8)
    elif poker_logic.is_four_of_a_kind(cards)[0]:
        return(PRICES[7], 'Four of a Kind', poker_logic.is_four_of_a_kind(cards)[1], 7)
    elif poker_logic.is_full_house(cards)[0]:
        return(PRICES[6], 'Full House', poker_logic.is_full_house(cards)[1], 6)
    elif poker_logic.is_flush(cards)[0]:
        return(PRICES[5], 'Flush', poker_logic.is_flush(cards)[1], 5)
    elif straight < 0 or straight > 0:
        return(PRICES[4], 'Straight', [0, 1, 2, 3, 4], 4)
    elif poker_logic.is_three_of_a_kind(cards)[0]:
        return(PRICES[3], 'Three of a Kind', poker_logic.is_three_of_a_kind(cards)[1], 3)
    elif poker_logic.is_two_pairs(cards)[0]:
        return(PRICES[2], 'Two pairs', poker_logic.is_two_pairs(cards)[1], 2)
    elif poker_logic.is_jacks_or_better(cards)[0]:
        return(PRICES[1], 'Jacks or Better', poker_logic.is_jacks_or_better(cards)[1], 1)
    return (PRICES[0], 'Nothing', None, 0)

#Width of given text string
def text_width(text):
    return len(result_string) * LETTER_WIDTH + len(result_string) * LETTER_MARGIN

#Width of given number integer
def number_width(number):
    return len(str(number)) * NUMBER_WIDTH + len(str(number)) * NUMBER_MARGIN

def get_display_x(index):
    return PRICE_WIDTH - PRICE_SCALE if index % 2 == 0 else 0

pygame.init()

#Setup application Window
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Video Poker')

#Clock for FPS tick
fpsClock = pygame.time.Clock()

#Setup cards
cards_img = load_image_scaled(pygame.image.load('cards.png').convert(), CARD_SCALE)
cards_back_img = load_image_scaled(pygame.image.load('card_back.png').convert(), CARD_SCALE)

init_cards()

#Setup buttons
buttons_img = load_image_scaled(pygame.image.load('buttons.png').convert(), BUTTON_SCALE)

btn_bet_hover = False
btn_bet_world_rect = Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT)
bet_button_interactable = True

btn_draw_hover = False
btn_draw_world_rect = Rect(SCREEN_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT)

#Setup numbers
numbers_img = load_image_scaled(pygame.image.load('numbers.png').convert(), NUMBER_SCALE)
numbers_img.set_colorkey((255, 0, 255))

#Setup letters
letters_img = load_image_scaled(pygame.image.load('letters.png').convert(), LETTER_SCALE)
letters_img.set_colorkey((255, 0, 255))

#Prices UI
prices_img = load_image_scaled(pygame.image.load('prices.png').convert(), PRICE_SCALE)
prices_img.set_colorkey((255, 0, 255))
prices_hover_img = load_image_scaled(pygame.image.load('prices_hover.png').convert(), PRICE_SCALE)
price_index = 0

#Bet and money
bet = 1
money = 100

#Game loop variables
game_running = True
game_over = False

#MAIN LOOP
while game_running:
    while not game_over:
        #Do we draw cards 
        if draw_cards:
            card_timer += fpsClock.get_time()
            if card_timer >= card_delay:
                if game_state == STATE_DRAW:
                    begin_round()
                    result_value, result_string, result_indices, price_index = process_results(bet)
                    if result_value > 0:
                        for i in range(len(result_indices)):
                            cards_in_hold[result_indices[i]] = True
                        money += result_value * bet
                    else:
                        if money <= 0:
                            print('game over!')
                            game_over = True
                    result_show = True
                    game_state = STATE_RESULT
                elif game_state == STATE_RESULT:
                    reset_cards()
                    begin_round()
                    game_state = STATE_DRAW
                draw_cards = False

        #Set background color
        DISPLAYSURF.fill(BG_COLOR)

        #Draw cards
        for i in range(CARDS_IN_HAND):
            rect = get_card_rect(cards[i]) if cards_visible[i] else Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
            DISPLAYSURF.blit(
                get_card_image(i),
                ((((CARD_X - ((CARDS_IN_HAND / 2) * CARD_WIDTH)) + i * CARD_WIDTH + i * CARD_MARGIN) + CARD_WIDTH / 2) - (CARDS_IN_HAND / 2) * CARD_MARGIN,
                get_card_y(i)),
                rect
            )

        #Display credits and bet
        render_text('credits', 10, 10)
        render_number(money, 180, 1)

        render_text('bet', 10, btn_bet_world_rect.y - 30)
        render_number(bet, 80, btn_bet_world_rect.y - 38)

        #Display results
        DISPLAYSURF.blit(prices_img, (14, 40), (0, 0, prices_img.get_width(), prices_img.get_height()))

        #result highlight
        if result_show:
            if price_index > 8:
                DISPLAYSURF.blit(prices_hover_img, (14 + (38 * PRICE_SCALE), 40), (get_display_x(9), 0, PRICE_WIDTH, PRICE_HEIGHT))
            elif price_index > 0:
                index = 9 - price_index
                DISPLAYSURF.blit(
                    prices_hover_img,
                    (14 + (PRICE_WIDTH - PRICE_SCALE if index % 2 == 0 else 0), 40 + math.ceil(index / 2) * PRICE_HEIGHT ),
                    (get_display_x(index + 1), int(index / 2) * PRICE_HEIGHT, PRICE_WIDTH, PRICE_HEIGHT))

        #result price values
        for i in range(9):
            if i + 1 > 8: render_number(PRICES[9] * bet, 350 + number_width(PRICES[9] * bet) / 2, 40)
            else: render_number(PRICES[9 - (i + 1)] * bet, 240 + (320 if (i + 1) % 2 == 0 else 0), 40 + math.ceil((i + 1) / 2) * PRICE_HEIGHT)

        '''
        if result_show:
            x = ((SCREEN_WIDTH / 2) - text_width(result_string) / 2)
            render_text(result_string.lower(), x, SCREEN_HEIGHT / 2 - (CARD_HEIGHT + 80))
            if result_value > 0:
                won_x = (x - 25) - (number_width(result_value) / 2)
                render_text('won', won_x, SCREEN_HEIGHT / 2 - (CARD_HEIGHT + 50))
                render_number(result_value, won_x + 80, SCREEN_HEIGHT / 2 - (CARD_HEIGHT + 58))
                render_text('credits', won_x + 90 + number_width(result_value), SCREEN_HEIGHT / 2 - (CARD_HEIGHT + 50))
        '''

        #Check buttons
        mx, my = pygame.mouse.get_pos()

        #Bet button
        btn_bet_hover = pick_rect(btn_bet_world_rect, mx, my)
        DISPLAYSURF.blit(buttons_img, (btn_bet_world_rect.x, btn_bet_world_rect.y), Rect(BUTTON_WIDTH if btn_bet_hover else 0, BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT))

        #Draw button
        btn_draw_hover = pick_rect(btn_draw_world_rect, mx, my)
        DISPLAYSURF.blit(buttons_img, (btn_draw_world_rect.x, btn_draw_world_rect.y), Rect(BUTTON_WIDTH if btn_draw_hover else 0, 0, BUTTON_WIDTH, BUTTON_HEIGHT))

        #Update screen and fps timer
        pygame.display.flip()
        fpsClock.tick(FPS)

        #Check events
        for event in pygame.event.get():
            if event.type == QUIT:
                game_running = False
                game_over = True
            elif event.type == MOUSEBUTTONUP:
                mx, my = pygame.mouse.get_pos()
                card_index = pick_card(mx, my)
                
                if card_index > -1 and game_state == STATE_DRAW:
                    cards_in_hold[card_index] = True if cards_in_hold[card_index] == False else False
                else:
                    if btn_bet_hover and bet_button_interactable:
                        bet += 1
                        bet = bet if bet <= MAX_BET else 1
                    elif btn_draw_hover:
                        if game_state == STATE_BEGIN:
                            if money >= bet:
                                print('State Begin')
                                reset_cards()
                                begin_round()
                                game_state = STATE_DRAW
                                money -= bet
                                bet_button_interactable = False
                        elif game_state == STATE_DRAW:
                            print('State Draw')
                            for i in range(CARDS_IN_HAND):
                                cards_visible[i] = True if cards_in_hold[i] else False
                            card_timer = 0
                            draw_cards = True
                            bet_button_interactable = True
                        elif game_state == STATE_RESULT:
                            print('State Result')
                            if money >= bet:
                                money -= bet
                                set_cards_visible(False)
                                card_timer = 0
                                draw_cards = True
                                bet_button_interactable = False
                                result_show = False
                                result_string = ''
                                result_value = -1
    while game_over and game_running:
        DISPLAYSURF.fill(BG_COLOR)
        
        render_text('no money left', 10, 10)
        render_text('game over', 10, 40)
        render_text('r to restart', 10, 70)

        pygame.display.flip()
        fpsClock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                game_running = False
                game_over = False
            elif event.type == KEYUP and event.key == pygame.K_r:
                money = 100
                bet = 1
                game_over = False
                game_state = STATE_BEGIN
                set_cards_visible(False)
                result_show = False
                result_string = ''
                result_value = -1

#END OF MAIN LOOP

#Shutdown application
pygame.quit()
sys.exit()