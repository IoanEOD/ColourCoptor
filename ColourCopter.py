import pygame
import random
from tkinter import *
from tkinter import ttk
import shelve
import os

pygame.init()

# Open The file used to store variables from the "File_Saves" directory
ShelfFile = shelve.open(os.path.join("File_Saves", "'Saved_Variables'"))
# Define the clock variable to allow th FPS to be set in later code
Clock = pygame.time.Clock()

# Set constants
Black = (0, 0, 0)
Green = (28, 154, 14)
Red = (201, 32, 32)
Blue = (44, 77, 222)
Grey = (90, 90, 90)
SkyBlue = (	135, 206, 235)
ColourList = (Green, Red, Blue)
ScreenInfo = pygame.display.Info()
ScreenWidth = ScreenInfo.current_w
ScreenHeight = ScreenInfo.current_h

############################################
# The following variables are not constants
# They need to be set at the beginning in order for the program to run
############################################
Screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
FirstDeploy = True
Running = True
FirstObstacle = False
SecObstacle = False
KeyUp = False
PointObs1 = False
PointObs2 = False
GameOver = False
StartScreen = True
MouseOnSettings = False
Fall = False
WaitToStart = True
Settings = False
MaxSpeed = 10
FractionSpeed = 0
ObstaclesPast = 0
Difficulty = 1
Score = 0
XCenter = ScreenWidth//2
Control = pygame.K_SPACE
KeyName = "the space bar"
#################################
# Create the class for the player
# derived from class: pygame.sprite.Sprite
#################################


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        # Load each possible image for the sprite from the "Sprite_Images" directory
        self.red_player = pygame.image.load(os.path.join("Sprite_Images", "RedCopter.png"))
        self.green_player = pygame.image.load(os.path.join("Sprite_Images", "GreenCopter.png"))
        self.blue_player = pygame.image.load(os.path.join("Sprite_Images", "BlueCopter.png"))

        # Randomize the colour of the helicopter for when it spawns in
        self.colour_list = [self.red_player, self.green_player, self.blue_player]
        self.coloured_sprite = self.colour_list[random.randint(0, 2)]

        self.colour = Green

        # Sets the image of the player to the appropriate colour
        self.image = self.coloured_sprite

        # Allocates the starting position of the helicopter
        self.rect = self.image.get_rect()
        self.rect.x = ScreenWidth//4.5
        self.rect.y = ScreenHeight//2

        # Allocates the initial vertical speed of the helicopter
        self.y_speed = 0
        self.change_y = 0

    # Function to reset speed and position of the helicopter
    def reset(self):
        self.rect.y = ScreenHeight//2
        self.y_speed = 0
        self.change_y = 0

    # Function that allows the vertical position of the helicopter to be accessed externally
    def get_y(self):
        return self.rect.y

    # Function that changes the vertical speed of the helicopter
    def change_speed(self, max_speed, fraction_speed):
        ###########################################################################
        # Use of multiplication allows acceleration and terminal velocity to be set
        # Integer needed as there can not be fractions of a pixel
        ###########################################################################
        self.change_y = int(max_speed * fraction_speed)

    # Function to randomly allocate the colour of the helicopter whilst maintaining its current position
    def change_colour(self, x, y):
        # Picks out a random image of the possible colours of the helicopter
        self.coloured_sprite = self.colour_list[random.randint(0, 2)]

        # Creates a new rectangle containing the new image
        self.image = self.coloured_sprite
        self.rect = self.image.get_rect()

        # Sets the position of the new rectangle to the position of the previous sprite rectangle
        self.rect.x = x
        self.rect.y = y

    # Function to be called every time we want to change the sprites properties
    def update(self):
        # Changes the position of the helicopter by its current speed
        self.rect.y -= self.change_y

        # if statements needed to return RGB values associated with the colour of the helicopter
        if self.coloured_sprite == self.red_player:
            self.colour = Red
        if self.coloured_sprite == self.green_player:
            self.colour = Green
        if self.coloured_sprite == self.blue_player:
            self.colour = Blue


class Obstacle(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.speed = 5

    # Function to spawn a random obstacle at a point
    def deploy(self):
        # Chooses a random colour for the obstacle
        self.colour = ColourList[random.randint(0, 2)]

        # Randomly chooses between stationary and vertically moving obstacle
        self.obstacle_num = random.randint(1, 2)

        # Stationary obstacle
        if self.obstacle_num == 1:
            # Chooses a random height for the obstacle
            Height = 100 * (random.randint(3, 7))

            # Creates the image for the obstacle by filling in a pygame surface with specified dimensions
            self.image = pygame.Surface([50, Height])
            self.image.fill(self.colour)

            # Sets the initial position of the obstacle
            position = random.randint(0, int(ScreenHeight*0.7) - Height)

            # Spawns the obstacle in rectangle form
            self.rect = self.image.get_rect()
            self.rect.x = ScreenWidth
            self.rect.y = position

        # Moving obstacle
        elif self.obstacle_num == 2:
            # Spawns in the obstacle with a random vertical position
            self.height = 500
            self.image = pygame.Surface([50, self.height])
            self.image.fill(self.colour)
            position = random.randint(0, int(ScreenHeight*0.7) - self.height)
            self.rect = self.image.get_rect()
            self.rect.x = ScreenWidth
            self.rect.y = position

            # Variable used to see if the obstacle is moving towards or away from y = 0
            self.lifting = True

    # Function carried out when the sprite is updated
    def update(self):
        # if statement needed as different updates required for stationary and moving obstacles
        if self.obstacle_num == 1:
            # Moves the obstacle left every update
            self.rect.x -= self.speed
        if self.obstacle_num == 2:
            # Moves the obstacle left every update
            self.rect.x -= self.speed

            # Randomises the speed at which the obstacle rises and falls
            self.y_speed = random.randint(1, 3)

            # if statement to determine if obstacle should change vertical direction
            # y < 0 means vertical direction should switch from up to down
            if self.rect.y < 0 and self.lifting:
                self.lifting = False
                self.rect.y += self.y_speed
            # Length subtracted as direction needs to change when bottom (not top) of obstacle hits bottom of the screen
            elif self.rect.y > ScreenHeight - self.height and not self.lifting:
                self.lifting = True
                self.rect.y -= self.y_speed

            # Sets direction accordingly
            if self.lifting:
                self.rect.y -= self.y_speed
            else:
                self.rect.y += self.y_speed

    # Used to initially spawn the second obstacle further to the right so there is a distance between the two obstacles
    def offset(self, amount):
        self.rect.x += amount

    def get_x(self):
        return self.rect.x

    # Function to remove the obstacle from the screen when the player gets a point
    def drop(self):
        if self.obstacle_num == 1:
            self.rect.y += 200
        if self.obstacle_num == 2:
            self.rect.y += 200
            self.y_speed = 0


# Function used for creating texts that can be displayed in pygame
class Text:
    def __init__(self, text, font, size, x, y, colour, background=None):
        # Sets the desired font and size of the text
        self.font = pygame.font.Font(font, size)

        # Renders the text so it is ready to be drawn onto the screen
        self.text = self.font.render(text, True, colour, background)

        # Converts the render into a rectangle
        self.rect = self.text.get_rect()

        # Sets the position of the text so that inserted co-ordinates are associated with the center of the rectangle
        self.rect.center = (x, y)


# Class for making a user interface with TkInter
class TkInterUI:

    def __init__(self):
        # sets the setting variables to those previously assigned in a different session using ShelFile
        self.ThrustControl = ShelfFile['Control']
        self.Theme = ShelfFile['Theme']

    # Function to activate and open the window
    def open(self):
        # Creates a window
        Root = Tk()

        # Sets the title at the top of the window
        Root.title("Settings")

        # Sets the size and position of the window
        Root.geometry("500x105+710+488")

        # Sets the variables to be used as the outputs of the drop down boxes
        self.ControlOption = StringVar()
        self.ThemeOption = StringVar()

        # Creates text item
        ControlText = ttk.Label(text="Key to control thrust:")
        # Displays the item in the window
        ControlText.pack()

        # Creates a drop down menu, assigning the current setting as the ControlOption variable
        MyCombobox1 = ttk.Combobox(Root, textvariable=self.ControlOption)
        #################################
        # Displays the item in the window
        # fill = X makes the box the same length as the window
        #################################
        MyCombobox1.pack(fill=X)
        # Creates the different options for the drop down box
        MyCombobox1.config(values=('Space Bar', 'Up Arrow', 'w', 'Enter(ON KEYPAD)'))
        # Sets the current displayed value to the current value
        self.ControlOption.set(self.ThrustControl)

        ColourText = ttk.Label(text="Theme:")
        ColourText.pack()

        MyCombobox2 = ttk.Combobox(Root, textvariable=self.ThemeOption)
        MyCombobox2.pack(fill=X)
        MyCombobox2.config(values=('Night', 'Day'))
        self.ThemeOption.set(self.Theme)

        ##############################################
        # Creates a button with the text "Apply" on it
        # When the button is clicked the function "apply_settings() is carried out
        ##############################################
        MyButton = ttk.Button(Root, text="Apply", command=self.apply_settings)
        MyButton.pack()

        #  Brings window above other windows
        Root.wm_attributes("-topmost", 1)

        ################################################
        # Pauses python execution until window is closed
        # mainloop() also checks for update in the window
        ################################################
        Root.mainloop()

    # Function carried out when "Apply" button is pressed
    def apply_settings(self):
        # Assigns variables to selected options
        self.ThrustControl = self.ControlOption.get()
        self.Theme = self.ThemeOption.get()


# Function that returns True if a specified rectangle is clicked on
def Pressed(Name, Event):
    #####################################################################################
    # rect.colidepoint will return True if selected co-ordinates are inside the rectangle
    # Selected co-ordinates are the position of the mouse from mouse.get_pos()
    #####################################################################################
    if Name.rect.collidepoint(pygame.mouse.get_pos()):
        OnButton = True
    else:
        OnButton = False
    # Returns True if the mouse is on the rectangle and is being clicked at the same time
    if Event.type == pygame.MOUSEBUTTONDOWN and OnButton:
        return True


# Set constants that need to be defined after classes have been defined
Helicopter = Player()
Obstacle1 = Obstacle()
Obstacle2 = Obstacle()
SettingsWindow = TkInterUI()
AllSpritesList = pygame.sprite.Group()
ObstacleGroup = pygame.sprite.Group()
PlayerGroup = pygame.sprite.Group()

# Adds sprites to respected sprite groups
AllSpritesList.add(Helicopter)
PlayerGroup.add(Helicopter)
AllSpritesList.add(Obstacle1)
AllSpritesList.add(Obstacle2)
ObstacleGroup.add(Obstacle1)
ObstacleGroup.add(Obstacle2)

# Defines settings to values from previous file saves
if ShelfFile['Control'] == "Space Bar":
    Control = pygame.K_SPACE
    KeyName = "The space bar"
elif ShelfFile['Control'] == "Up Arrow":
    Control = pygame.K_UP
    KeyName = "up"
elif ShelfFile['Control'] == "w":
    Control = pygame.K_w
    KeyName = "'w'"
elif ShelfFile['Control'] == "Enter(ON KEYPAD)":
    Control = pygame.K_KP_ENTER
    KeyName = "Enter"

if SettingsWindow.Theme == 'Night':
    ShelfFile['Colour'] = Black
elif SettingsWindow.Theme == 'Day':
    ShelfFile['Colour'] = SkyBlue
BackgroundColour = ShelfFile['Colour']


# Creates Text variables that don't require updates
TitleText = Text("ColourCoptor", "SlopeOpera-gg1Y.ttf", 200, XCenter, int(ScreenHeight*0.3), Green)
GameOverText = Text("GameOver", "SlopeOpera-gg1Y.ttf", 200, XCenter, int(ScreenHeight*0.2), Red)

# Starts the main loop that is active whilst the game is running
while Running:

    # Define variables that require updates
    Key = pygame.key.get_pressed()
    SettingsButton = Text("Settings", "SlopeOpera-gg1Y.ttf", 70, int(ScreenWidth * 0.15), int(ScreenHeight * 0.8), Grey)
    QuitButton = Text("Quit", "SlopeOpera-gg1Y.ttf", 70, int(ScreenWidth * 0.9), int(ScreenHeight * 0.8), Grey)
    StartScreenButton = Text("start screen", "SlopeOpera-gg1Y.ttf", 70, XCenter, int(ScreenHeight * 0.8), Grey)
    FinalScoreDisplay = Text("Score: " + str(Score), "SlopeOpera-gg1Y.ttf", 100, ScreenWidth // 2, int(ScreenHeight * 0.21) + 150, Green)
    PressKeyGoText = Text("Press the " + KeyName + " to start again", "SlopeOpera-gg1Y.ttf", 80, XCenter, int(ScreenHeight * 0.56), Blue)
    PressKeyStartText = Text("Press " + KeyName + " to start", "SlopeOpera-gg1Y.ttf", 100, XCenter, int(ScreenHeight * 0.45), Blue)
    ScoreScreen = Text("Score: " + str(Score), "SlopeOpera-gg1Y.ttf", 80, XCenter, int(ScreenHeight * 0.1), Helicopter.colour)
    BestScreen = Text("PersonalBest: " + str(ShelfFile['MaxScore']), "SlopeOpera-gg1Y.ttf", 80, XCenter, int(ScreenHeight * 0.45), Green)

    # Sets what happens when the player loses
    if GameOver:

        # Resets all variables
        FirstObstacle = False
        SecObstacle = False
        Difficulty = 1
        ObstaclesPast = 0
        Obstacle1.speed = 5
        Obstacle2.speed = 5

        # Updates the players personal best
        if Score > ShelfFile['MaxScore']:
            ShelfFile['MaxScore'] = Score

        ############################
        # Draws the game over screen
        # Screen.blit displays the items on the screen
        ############################
        Screen.fill(BackgroundColour)
        Screen.blit(GameOverText.text, GameOverText.rect)
        Screen.blit(FinalScoreDisplay.text, FinalScoreDisplay.rect)
        Screen.blit(StartScreenButton.text, StartScreenButton.rect)
        Screen.blit(PressKeyGoText.text, PressKeyGoText.rect)
        Screen.blit(BestScreen.text, BestScreen.rect)

        # Looks at every pygame event
        for Event in pygame.event.get():
            # Exits the game over screen and starts the game again if the user presses their chosen control button
            if Event.type == pygame.KEYDOWN:
                if Event.key == Control:
                    GameOver = False
                    WaitToStart = True

            # Opens the start screen if the Start Screen Button is pressed
            if Pressed(StartScreenButton, Event):
                StartScreen = True
                GameOver = False

    elif StartScreen:

        if not Settings:
            # Draws the start screen
            Screen.fill(BackgroundColour)
            Screen.blit(TitleText.text, TitleText.rect)
            Screen.blit(PressKeyStartText.text, PressKeyStartText.rect)
            Screen.blit(SettingsButton.text, SettingsButton.rect)
            Screen.blit(QuitButton.text, QuitButton.rect)

            for Event in pygame.event.get():

                if Event.type == pygame.KEYDOWN:
                    # Exits the start screen and starts the game if the user presses their chosen control button
                    if Event.key == Control:
                        StartScreen = False
                        WaitToStart = True

                # Opens settings menu if the settings button is pressed
                if Pressed(SettingsButton, Event):
                    Settings = True
                # Quits the game if the quit button is pressed
                if Pressed(QuitButton, Event):
                    Running = False

        # Code for the TkInter settings window
        else:
            # Changes the pygame to a window with no borders so that the TkInter window can be displayed above it
            Screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)

            SettingsWindow.open()

            # Takes the chosen settings and applies them to their associated variables
            if SettingsWindow.ThrustControl == "Space Bar":
                Control = pygame.K_SPACE
                KeyName = "The space bar"
            elif SettingsWindow.ThrustControl == "Up Arrow":
                Control = pygame.K_UP
                KeyName = "up"
            elif SettingsWindow.ThrustControl == "w":
                Control = pygame.K_w
                KeyName = "'w'"
            elif SettingsWindow.ThrustControl == "Enter(ON KEYPAD)":
                Control = pygame.K_KP_ENTER
                KeyName = "Enter"

            if SettingsWindow.Theme == 'Night':
                ShelfFile['Colour'] = Black
            elif SettingsWindow.Theme == 'Day':
                ShelfFile['Colour'] = SkyBlue
            BackgroundColour = ShelfFile['Colour']

            # Resets the display back to full screen
            Screen = pygame.display.set_mode((ScreenWidth, ScreenHeight), pygame.FULLSCREEN)

            # Exits settings menu code
            Settings = False

    #############################################################
    # Wait to start screen appears when the player starts playing
    # It pauses the game until the user presses their chosen control key
    #############################################################
    elif WaitToStart:
        # Resets variables
        Score = 0
        FractionSpeed = 0
        FirstDeploy = True

        Helicopter.reset()

        # Draws the screen
        Screen.fill(BackgroundColour)
        PlayerGroup.update()
        PlayerGroup.draw(Screen)
        Screen.blit(ScoreScreen.text, ScoreScreen.rect)

        for Event in pygame.event.get():
            if Event.type == pygame.KEYUP:
                KeyUp = True
            if Event.type == pygame.KEYDOWN:
                # Starts the game if user presses their chosen control key
                # Use KeyUp variable as need to ensure the user has released the key from their previous play
                if Event.key == Control and KeyUp:
                    WaitToStart = False
                    KeyUp = False

    # Code for when the game is being played
    else:
        for Event in pygame.event.get():
            # Checks if the control key has been released
            if Event.type == pygame.KEYUP:
                if Event.key == Control:
                    KeyUp = True
            # Checks if the control key has been released
            elif Event.type == pygame.KEYDOWN:
                if Event.key == Control:
                    KeyUp = False

        if Helicopter.get_y() > 0 or Fall:
            # Increases the helicopters speed if the user presses the control key
            if Key[Control] and not Fall:
                # Increasing fraction speed acts as acceleration as it increases the fraction of the speed every cycle
                if FractionSpeed < 0.5:
                    FractionSpeed += 0.068
                Helicopter.change_speed(27, FractionSpeed)

            if KeyUp:
                # Fall variable is needed to prevent the helicopter from jolting when colliding with the top of the screen
                if Fall:
                    FractionSpeed = 0
                    FractionSpeed -= 0.06
                elif FractionSpeed > -1:
                    FractionSpeed -= 0.06
                Helicopter.change_speed(19, FractionSpeed)
                Fall = False

            ######################################################################################
            # Ends the game if the BOTTOM of the helicopter collides with the bottom of the screen
            # - 102 as the height of the helicopter image is 102 pixels
            ######################################################################################
            if Helicopter.get_y() > ScreenHeight - 102:
                GameOver = True

        # Stops the helicopter from going any higher if it is at the top of the screen
        elif Helicopter.get_y() < 0 and not KeyUp:
            Helicopter.change_y = 0

        elif Helicopter.get_y() < 0:
            Fall = True

        # if statement carries out if obstacle is not on the screen
        if not FirstObstacle:
            Obstacle1.deploy()
            ObstaclesPast += 1
            FirstObstacle = True
            # Resets the point for that obstacle as a point is available for the user to obtain when it is first deployed
            PointObs1 = False
        else:
            # Removes the obstacle if it has moved past the left edge of the screen
            if Obstacle1.get_x() < -30:
                FirstObstacle = False

        if not SecObstacle:

            # First obstacle is needed to offset its deploy position when it is first deployed
            if FirstDeploy:
                Obstacle2.deploy()
                ObstaclesPast += 1
                Obstacle2.offset(ScreenWidth//2)
                SecObstacle = True
                FirstDeploy = False
            else:
                Obstacle2.deploy()
                ObstaclesPast += 1
                SecObstacle = True
                PointObs2 = False
        else:
            if Obstacle2.get_x() < -30:
                SecObstacle = False

        #####################################################################################
        # Acts as both an animation and a way to randomly change the colour of the helicopter
        # Animation works as the helicopter will rapidly change colour as Obstacle 1 moves between the two specified points
        #####################################################################################
        if int(0.1 * ScreenWidth) < Obstacle1.get_x() < int(0.3 * ScreenWidth):
            Helicopter.change_colour(Helicopter.rect.x, Helicopter.rect.y)

        ###################################################################
        # Increases speed when a certain amount of obstacles have gone past
        # This amount increases as the difficulty increases
        ###################################################################
        if ObstaclesPast == 5 * Difficulty:
            Difficulty += 1
            # Horizontal speed of obstacles increases as difficulty increases
            Obstacle1.speed += 2
            Obstacle2.speed += 2
            # Resets the obstacles past so that they can be counted from zero for each difficulty level
            ObstaclesPast = 0

        # Checks if the helicopter collides with the player using pygame's sprite groups
        for Obstacle in pygame.sprite.spritecollide(Helicopter, ObstacleGroup, False):
            if Obstacle.colour != Helicopter.colour:
                # Ends the game if the player collides with the wrong colour
                GameOver = True
            else:
                #############################################################
                # Adds a point if the player collides with the correct colour
                # Using the PointsObs boolean variables means that the user can only pick up a maximum of one point while they are colliding with the obstacle
                #############################################################
                if Obstacle == Obstacle1:
                    if not PointObs1:
                        Score += 1
                        PointObs1 = True
                else:
                    if Obstacle == Obstacle2:
                        if not PointObs2:
                            Score += 1
                            PointObs2 = True

        # Removes the first obstacle if the player has collided with it and it is the correct colour
        if PointObs1:
            if Obstacle1.rect.y < ScreenHeight:
                Obstacle1.drop()

        # Removes the second obstacle if the player has collided with it and it is the correct colour
        elif PointObs2:
            if Obstacle2.rect.y < ScreenHeight:
                Obstacle2.drop()

        # Draws the game screen
        Screen.fill(BackgroundColour)
        # Uses pygame's sprite functionality to carry out the update function of both the player and the obstacles
        AllSpritesList.update()
        AllSpritesList.draw(Screen)
        Screen.blit(ScoreScreen.text, ScoreScreen.rect)

    # Updates the display
    pygame.display.flip()
    # Ensures the game runs at 60 frames per second
    Clock.tick(60)

# Saves the required variables to a file so they remain the same for the next time the program is opened
ShelfFile['Theme'] = SettingsWindow.Theme
ShelfFile['Control'] = SettingsWindow.ThrustControl
ShelfFile.close()

# Closes the pygame window
pygame.quit()
