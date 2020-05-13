import random as rand
import tkinter as tk
from PIL import Image, ImageTk

#UI element tags
SNAKE_TAG   = "SNAKE"
FOOD_TAG    = "FOOD"
SCORE_TAG   = "SCORE"

#move delta and refresh rate
MOVE_DELTA          = 20
UPDATES_PER_SECOND  = 10 #number of movements per second
REFRESH_RATE        = 1000 // UPDATES_PER_SECOND #canvas refresh rate

#dimensions
CANVAS_WIDTH    = 500
CANVAS_HEIGHT   = 500
BLOCK_SIZE      = 20

#movement directions
RIGHT_MOVEMENT_DIRECTION     = "Right"
LEFT_MOVEMENT_DIRECTION      = "Left"
UP_MOVEMENT_DIRECTION        = "Up"
DOWN_MOVEMENT_DIRECTION      = "Down"

#subclass of Canvas
class SnakeCanvas(tk.Canvas):
    def __init__(self):
        super().__init__(width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background="black", highlightthickness=0) #initial canvas setup

        self.snake_coordinates = [(200, 240), (180, 240), (160, 240), (140, 240)] #initial snake block coordinates
        self.food_coordinates = self.generate_food_coordinates() #initial food block coordinates

        self.score = 0 #initial score

        self.movement_direction = RIGHT_MOVEMENT_DIRECTION #initial movement direction
        self.bind_all("<Key>", self.handle_keypress) #handle all key presses

        self.load_gameplay_assets() #load image assets
        self.create_elements() #place assets at given coordinates

        self.after(REFRESH_RATE, self.update_frame)

    #loads image assets for snake and food
    def load_gameplay_assets(self):
        try:
            #load food block image
            self.food_block_image = Image.open("./assets/food.png")
            self.food = ImageTk.PhotoImage(self.food_block_image)

            #load snake block image
            self.snake_block_image = Image.open("./assets/snake.png")
            self.snake_block = ImageTk.PhotoImage(self.snake_block_image)
        except IOError as error:
            print(error)
            mainWindow.destroy() #close window in case of an error

    #creates elements to display
    def create_elements(self):
        self.create_text(60, 12, text=f"Current score: {self.score}", tag=SCORE_TAG, fill="#fff", font=("TkDefaultFont", 15)) #canvas method, creates text displaying score

        for x_coordinate, y_coordinate in self.snake_coordinates:
            self.create_image(x_coordinate, y_coordinate, image=self.snake_block, tag=SNAKE_TAG) #canvas method, creates snake image assets at given location

        self.create_image(self.food_coordinates[0], self.food_coordinates[1], image=self.food, tag=FOOD_TAG) #canvas method, creates food image asset at given location
        self.create_rectangle(10, 25, 490, 490, outline="#939eab") ##canvas method, defines boundary for game

    #moves snake body
    def animate_snake(self):
        head_x_coordinate, head_y_coordinate = self.snake_coordinates[0] #take first snake block position as head position

        #move by block size depending on direction
        if self.movement_direction == LEFT_MOVEMENT_DIRECTION:
            new_head_coordinates = (head_x_coordinate - MOVE_DELTA, head_y_coordinate)
        elif self.movement_direction == RIGHT_MOVEMENT_DIRECTION:
            new_head_coordinates = (head_x_coordinate + MOVE_DELTA, head_y_coordinate)
        elif self.movement_direction == UP_MOVEMENT_DIRECTION:
            new_head_coordinates = (head_x_coordinate, head_y_coordinate- MOVE_DELTA)
        elif self.movement_direction == DOWN_MOVEMENT_DIRECTION:
            new_head_coordinates = (head_x_coordinate, head_y_coordinate + MOVE_DELTA)

        #add new head coordinate
        self.snake_coordinates = [new_head_coordinates] + self.snake_coordinates[:-1] #drop the very last block of the snake body when updating coordinates

        #find all elements (images) tagged as Snake, get all coordinates, and zip them into a tuple
        for element, coordinate in zip(self.find_withtag(SNAKE_TAG), self.snake_coordinates):
            self.coords(element, coordinate) ##canvas method, updates snake image coordinates

    #update frame
    def update_frame(self):
        if self.detect_collisions():
            self.handle_end_of_game()
            return #if the snake collides into the edge, or itself, the game is over

        self.detect_food_collision() #before moving the snake body, check for any collisions with the food block

        self.animate_snake() #moves snake into new position
        self.after(REFRESH_RATE, self.update_frame) #calls itself after 100 millisecs

    #check for collisions of snake head with borders or itself
    def detect_collisions(self):
        head_x_position, head_y_position = self.snake_coordinates[0] #take first snake block position as head position

        return (head_x_position not in range(0, CANVAS_WIDTH)  #the head x coordinate cannot be more than the canvas width
                or head_y_position not in range(20, CANVAS_HEIGHT)  #the head y coordinate cannot be more than the canvas height, or stretch into the score label
                or (head_x_position, head_y_position) in self.snake_coordinates[1:]) #if the head coordinate is the same as one of the body element coordinates, the snake collided with itself

    #check for collisions of snake head with food
    def detect_food_collision(self):
        #if collision is detected
        if self.snake_coordinates[0] == self.food_coordinates:
            self.score += 1 #increase score
            self.snake_coordinates.append(self.snake_coordinates[-1]) #increase snake size by adding the last element again, as it will be removed anyway in the move function

            #create new snake body block image
            self.create_image(*self.snake_coordinates[-1], image=self.snake_block, tag=SNAKE_TAG) #canvas method, creates snake image assets at given location

            #generate new food coordinates, and update food block on screen using coords
            self.food_coordinates = self.generate_food_coordinates()
            self.coords(self.find_withtag(FOOD_TAG), *self.food_coordinates)

            #update score label text
            score = self.find_withtag(SCORE_TAG)
            self.itemconfigure(score, text=f"Current score: {self.score}", tag=SCORE_TAG)

    #generate new food coordinates
    def generate_food_coordinates(self):
        while True:
            #generate random coordinates
            x_position = rand.randint(1, (CANVAS_WIDTH // BLOCK_SIZE)-1) * MOVE_DELTA
            y_position = rand.randint(3, (CANVAS_HEIGHT // BLOCK_SIZE)-1) * MOVE_DELTA
            food_position = (x_position, y_position)

            #food block cannot have the same coordinate as the snake blocks
            if food_position not in self.snake_coordinates:
                return food_position

    #handle key press events
    def handle_keypress(self, event):
        new_movement_direction = event.keysym #event symbol gives the new direction

        #event key symbol must match one of the arrow keys
        all_possible_movement_directions = (LEFT_MOVEMENT_DIRECTION, RIGHT_MOVEMENT_DIRECTION, UP_MOVEMENT_DIRECTION, DOWN_MOVEMENT_DIRECTION)
        opposite_movement_directions = ({LEFT_MOVEMENT_DIRECTION, RIGHT_MOVEMENT_DIRECTION}, {UP_MOVEMENT_DIRECTION, DOWN_MOVEMENT_DIRECTION})

        #only handle arrow key presses, but ignore ones that are opposite of the current direction
        if new_movement_direction in all_possible_movement_directions and {self.movement_direction, new_movement_direction} not in opposite_movement_directions:
            self.movement_direction = new_movement_direction

    #handle end of game
    def handle_end_of_game(self):
        self.delete(tk.ALL) #delete everything in the canvas
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2, text="Game Over", fill="#fff", font=("TkDefaultFont", 30)) #display game over text

#main app window
mainWindow = tk.Tk()
mainWindow.title("Snake Game") #window title
mainWindow.resizable(False, False) #unresizable window at X and Y axis

gameCanvas = SnakeCanvas()
gameCanvas.pack() #puts canvas in window

mainWindow.mainloop()