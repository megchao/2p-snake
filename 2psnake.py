"""
6.177 Final Project (IAP 2015)
Two-Player Snake!
Completed by:
Megan Chao
Arden Marin
Lisa Deng
"""

import pygame, sys, random

### Global Variables
WIDTH = 26  # this is the width of an individual square
HEIGHT = 26 # this is the height of an individual square
DIMENSION = 17 # dimensions of the board, in squares
ROUND = 0 # the round of the game, determines obstacles
ONE_SCORE = 0 # player one's score
TWO_SCORE = 0 # player two's score

# RGB Color definitions
black = (0, 0, 0)
white = (255, 255, 255)

def new_game():
    # Sets up all necessary components to start a new game.
    pygame.init() # initialize all imported pygame modules
    window_size = [WIDTH * DIMENSION + 20, HEIGHT * DIMENSION + 70] #DENG
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("***2P Snake***") # caption sets title of Window 
    board = Board(DIMENSION, 0, screen) #DENG
    clock = pygame.time.Clock()
    board.round_and_score() #redraws the round and scores
    main_loop(screen, board, clock, False, False)

def main_loop(screen, board, clock, stop, pause): #CHAO
    board.update() # redraw the board
    pygame.display.flip()
    
    while stop == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # user clicks close
                stop = True
                pygame.quit()
            elif event.type==pygame.KEYDOWN: # checks for keyboard input
                if event.key==pygame.K_p: # press P to pause
                    if pause:
                        pause = False
                    else:
                        pause = True
                elif event.key == pygame.K_ESCAPE: # alternate way to end game: escape key
                    stop = True
                    pygame.quit()
                elif (board.game_over() or board.collision()) and event.key==pygame.K_SPACE: # press space for new game
                    global ROUND
                    ROUND += 1 # of rounds go up when a new game starts
                    new_game()
                elif pause == False:
                     board.player1.turn(event.key) # check to see if either player wants to change direction
                     board.player2.turn(event.key)
                     if not board.game_over():
                         board.update() # redraw the board if both players are alive
        if pause == False:
            board.player1.move_forward(board) # move the players
            board.player2.move_forward(board)
            if board.collision() and not board.game_over(): # both players hit each other
                board.player1.explode() # both of them die
                board.player2.explode()
                board.game_over_msg("HEAD-ON COLLISION!")
            board.update() # redraw the board
            pygame.display.flip()
            clock.tick(5)            
    pygame.quit() # closes things, keeps idle from freezing

class Board:
    # The place where the game takes place
    
    def __init__(self, size, rounds, screen): #DENG
        self.screen = screen
        self.size = size

        #---Initializes Squares (the "Board")---#
        self.squares = pygame.sprite.RenderPlain()
        self.boardSquares = [] # list of squares in the board
        self.occupied = [] # list of squares that are "occupied" -- players will die if they run into these squares
        self.obstacles = pygame.sprite.RenderPlain()
        
        #---Populate boardSquares and squares with Squares---#
        for row in range(size): #DENG
            for col in range (size):
                s = Square(row, col, white)
                self.squares.add(s)
                self.boardSquares.append(s)

        #---Initialize Players and Add to Sprite List---#
        self.player1 = Player(self, size/2, 0, 1)
        self.player2 = Player(self, size/2, size-1, 2)
        self.players = pygame.sprite.RenderPlain()
        self.players.add(self.player1)
        self.players.add(self.player2)

        #---Initialize Score Images and Add to Sprite List---#
        self.score1 = Score(1)
        self.score2 = Score(2)
        self.scores = pygame.sprite.RenderPlain()
        self.scores.add(self.score1)
        self.scores.add(self.score2)
        
        #---Populate occupied and obstacles with randomly placed obstacles--- #MARIN
        n = ROUND * 2 # number of obstacles is twice the round number
        for i in range(n):
            row = random.randint(0,size-1) # random row
            while (row == size/2 or row == 3 or row == size-4): # keep some rows clear for movement
                row = random.randint(0,size-1)
            col = random.randint(0,size-1) # random column
            while (col == size/2-1 or col == size/2+1 or col == 4 or col == size-5): # also keep some columns clear, assures movement
                col = random.randint(0,size-1)
            randSquare = Square(row, col, black)
            self.occupied.append(randSquare)
            obs = Obstacle(self, row, col, i)
            self.obstacles.add(obs)

    def update(self): #CHAO
        # updates the game by redrawing the squares, players, and obstacles, called in main loop
        self.squares.draw(self.screen) # draw squares
        self.players.draw(self.screen)# draw player Sprites
        self.obstacles.draw(self.screen) # draws obstacles
    
    def get_square(self, x, y):
        # Given an (x, y) pair, return the Square at that location
        for s in self.boardSquares:
            if (s.row == x and s.col == y):
                return s

    def is_obstacle(self, x, y): #DENG
        # Looks for square in list of occupied squares and returns true if it is found, called in main loop
        occupant = self.get_square(x, y)
        for sq in self.occupied:
            if sq == occupant:
                return True
        return False   

    def get_obstacle_number(self, rounds): #DENG
        # returns number of obstacles needed, called in main loop
        return self.rounds * 2
    
    def game_over(self): #CHAO
        # checks if the game is over by checking if either or both players are dead
        if self.player1.is_dead() or self.player2.is_dead():
            return True
        return False

    def collision(self): #CHAO
        # if the players end up on top of each other, they are both dead
        if self.player1.get_current_square() == self.player2.get_current_square():
            return True
        return False

    def print_text(self, text, centerx, centery): #CHAO
        # prints text to the screen
        textRect = text.get_rect()
        textRect.centerx = centerx
        textRect.centery = centery
        self.screen.blit(text, textRect)
    
    def game_over_msg(self, msg): #CHAO
        # prints a message at the bottom of the screen when the game is over
        font = pygame.font.Font(None, 20)
        text = font.render(msg, True, white, black)
        self.print_text(text, text.get_width()/2+10, HEIGHT*(DIMENSION+1)+30)
        text = font.render("Press Space to play again", True, white, black)
        self.print_text(text, WIDTH*DIMENSION-text.get_width()/2, HEIGHT*(DIMENSION+1)+30)
        pygame.display.flip()

    def round_and_score(self): #MARIN
        # prints game text, such as the round number, the scores, and the pause message
        font = pygame.font.Font(None, 40) 
        text = font.render("ROUND "+str(ROUND+1), True, white, black)
        self.print_text(text, WIDTH*DIMENSION/2+10, text.get_height()/2+8) # shows the round number

        self.scores.draw(self.screen) # draws score sprites

        font = pygame.font.Font(None, 25) 
        text = font.render(str(ONE_SCORE), True, white, black)
        self.print_text(text, WIDTH+text.get_width()/2+20, text.get_height()/2+12) # shows player 1's score

        text = font.render(str(TWO_SCORE), True, white, black)
        self.print_text(text, WIDTH*(DIMENSION-1)-text.get_width()/2, text.get_height()/2+12) # shows player 2's score
        
        font = pygame.font.Font(None, 20)
        text = font.render("Press P to pause game", True, white, black) # shows message that you can pause the game
        self.print_text(text, WIDTH*DIMENSION-text.get_width()/2, HEIGHT*(DIMENSION+1)+30)

        pygame.display.flip()

class Square(pygame.sprite.Sprite): #MARIN
    # squares used to make the board
    
    def __init__(self, row, col, color):
        pygame.sprite.Sprite.__init__(self)
        self.row = row
        self.col = col
        self.image = pygame.Surface([WIDTH, HEIGHT])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = 10+self.col*WIDTH # location of square
        self.rect.y = 40+self.row*HEIGHT

    def get_rect_from_square(self):
        return self.rect
    
class Player(pygame.sprite.Sprite): #MARIN
    # game player
    
    def __init__(self, board, row, col, index):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        self.row = row
        self.board = board
        self.rect = board.get_square(self.row, self.col).get_rect_from_square()
        self.index = index
        self.behind = self.get_current_square()
        
        if self.index == 1: # Player 1 faces right
            self.rotation = (1,0)
            self.set_pic(-90)
        elif self.index == 2:
            self.rotation = (-1,0) # Player 2 faces left
            self.set_pic(90)

        self.lastrotation = self.rotation

    def is_dead(self): #CHAO
        # a player is dead if it has run into an obstacle or into the edge of the board
        if self.board.is_obstacle(self.row, self.col) or self.col < 0 or self.col >= self.board.size or self.row < 0 or self.row >= self.board.size:
            return True
        return False

    def explode(self): #CHAO
        # changes the player's sprite to an explosion if it has died
        self.image = pygame.image.load("sprites/boom.png").convert_alpha()

    def undo_move(self): #CHAO
        # player undoes its last move
        cur = self.get_current_square()
        self.col -= self.rotation[0] # move player backwards using the rotation tuple
        self.row += self.rotation[1]
        if (self.board.occupied.count(cur) > 0):
            self.board.occupied.remove(cur) # unoccupy the spot where the player used to be
        self.rect = self.board.get_square(self.row, self.col).get_rect_from_square()
        cur.image = pygame.Surface([WIDTH, HEIGHT])
        cur.image.fill(white)
    
    def get_current_square(self): #MARIN
        # returns the square the player is on
        return self.board.get_square(self.row, self.col)
    
    def move_forward(self, board): #MARIN
        # moves player and adds a trail behind the player as it moves
        if not board.game_over() and not board.collision():
            cur = self.get_current_square()
            self.col += self.rotation[0] # move the player
            self.row -= self.rotation[1]
            if self.is_dead(): #CHAO
                self.explode() # change the player sprite if it has died
                if self.index == 1: # if Player 1 dies first we have to check if Player 2 dies on the same turn
                    cur = board.player2.get_current_square()
                    board.player2.col += board.player2.rotation[0] # move Player 2
                    board.player2.row -= board.player2.rotation[1]
                    if board.player2.is_dead():
                        board.player2.explode()
                        board.game_over_msg("BOTH PLAYERS HAVE DIED")
                    else: # if Player 2 has not died, then Player 2 wins and we undo the move
                        board.player2.undo_move()
                        board.game_over_msg("PLAYER 1 HAS DIED")
                        global TWO_SCORE #MARIN
                        TWO_SCORE += 1
                else: # Player 1 wins
                    board.player1.undo_move() # Since Player 1 moved first, we need to move Player 1 back (undo the turn) if Player 2 died.
                    board.game_over_msg("PLAYER 2 HAS DIED")
                    global ONE_SCORE #MARIN
                    ONE_SCORE += 1                 
            else: # player has not died
                self.rect = board.get_square(self.row, self.col).get_rect_from_square()
                cur.image = pygame.image.load("sprites/trail"+str(self.index)+".png").convert_alpha() # leave trail behind player
                board.occupied.append(cur) # previous square is now occupied
                self.behind = cur                

    def turn(self, direction): #MARIN
        # allows the user to change the direction of the player with given keys
        if not self.board.game_over() and not self.board.collision():
            self.lastrotation = self.rotation
            if self.index == 1: # Player 1's controls
                if direction == pygame.K_a: # left
                    self.rotation = (-1,0)
                    self.set_pic(90)
                if direction == pygame.K_d: # right
                    self.rotation = (1,0)
                    self.set_pic(-90)
                if direction == pygame.K_w: # up
                    self.rotation = (0,1)
                    self.set_pic(0)
                if direction == pygame.K_s: # down
                    self.rotation = (0,-1)
                    self.set_pic(180)
            elif self.index == 2: # Player 2's controls
                if direction == pygame.K_LEFT: # left
                    self.rotation = (-1,0)
                    self.set_pic(90)
                if direction == pygame.K_RIGHT: # right
                    self.rotation = (1,0)
                    self.set_pic(-90)
                if direction == pygame.K_UP: # up
                    self.rotation = (0,1)
                    self.set_pic(0)
                if direction == pygame.K_DOWN: # down
                    self.rotation = (0,-1)
                    self.set_pic(180)
            if self.board.get_square(self.row-self.rotation[1], self.col+self.rotation[0]) == self.behind: # prevent player from turning 180 degrees and accidentally suiciding
                self.rotation = self.lastrotation # rotate player back to its last rotation
                if self.rotation == (-1,0):
                    self.set_pic(90)
                if self.rotation == (1,0):
                    self.set_pic(-90)
                if self.rotation == (0,1):
                    self.set_pic(0)
                if self.rotation == (0,-1):
                    self.set_pic(180)

    def set_pic(self, rot): #MARIN
        # rotates the picture to whatever direction the player moves
        self.image = pygame.image.load("sprites/player"+str(self.index)+".png").convert_alpha() # sets player image
        self.image = pygame.transform.rotate(self.image, rot) # rotates player image

class Obstacle(pygame.sprite.Sprite): #CHAO
    # As the round increases, more and more obstacles will show up on the board. If a player runs into one, it will die.
    
    def __init__(self, board, row, col, index):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        self.row = row
        self.board = board
        self.board.occupied.append(self.board.get_square(self.row, self.col)) # occupies square
        self.rect = self.board.get_square(self.row, self.col).get_rect_from_square()
        self.image = pygame.image.load("sprites/obstacle.png").convert_alpha().convert_alpha() # sets the image for the obstacle

class Score(pygame.sprite.Sprite): #CHAO
    # Draws scorekeeper sprites (is purely aesthetic)
    
    def __init__(self, index):
        pygame.sprite.Sprite.__init__(self)
        self.index = index
        self.image = pygame.image.load("sprites/score"+str(self.index)+".png").convert_alpha() #set image
        self.rect = self.image.get_rect()
        if self.index == 1: # sets location of player 1's scorekeeper
            self.rect.x = 10
            self.rect.y = 8
        if self.index == 2: # sets location of player 2's scorekeeper
            self.rect.x = WIDTH*(DIMENSION-1)+10
            self.rect.y = 8
    
if __name__ == "__main__":
      new_game()
