import pygame
from pygame.locals import *
from gamelib import game_objects
from gamelib import file_io
from gamelib import config_load


def main():

    # Loads the config file and sets them to sensible variable names
    config_map = config_load.load_config()

    # Initialise the game
    pygame.init()

    # Sets the FPS of the game
    fps = 30
    fps_clock = pygame.time.Clock()

    # Create the game window
    screen = pygame.display.set_mode((config_map["screen_x_axis"], config_map["screen_y_axis"]))
    # Gets the windows size to be used to ensure things stay in the window / where they can spawn
    display_info = pygame.display.Info()
    display_size = {
        "display_w": display_info.current_w,
        "display_h": display_info.current_h
    }

    # Sets the background image
    if display_size["display_w"] == 1280:
        background = pygame.image.load('images/background1.png').convert()
    else:
        background = pygame.image.load('images/background2.png').convert()

    # Set the game icon and name
    pygame.display.set_icon(pygame.image.load('images/game_icon.png'))
    pygame.display.set_caption('Bat Out of Hell')

    # Create a custom event to add enemies, clouds, gems and water
    # If gems and / or water are disabled in config, they will not have a spawn timer set
    ADDENEMY = pygame.USEREVENT + 1
    ADDCLOUD = pygame.USEREVENT + 2
    ADDGEM = pygame.USEREVENT + 3
    ADDWATER = pygame.USEREVENT + 4
    pygame.time.set_timer(ADDCLOUD, 1000)
    if config_map["spawn_gems"]:
        pygame.time.set_timer(ADDGEM, 4000)
    if config_map["spawn_water"]:
        pygame.time.set_timer(ADDWATER, config_map["lives_spawn_rate"])

    # Instantiate the player
    player = game_objects.Player(display_size)
    # Creating sprite groups to store the game sprites
    # Group for enemies
    enemies = pygame.sprite.Group()
    # Group for clouds
    clouds = pygame.sprite.Group()
    # Group for gems
    gems = pygame.sprite.Group()
    # Groups for hearts
    hearts = pygame.sprite.Group()
    # Group for water
    water_drops = pygame.sprite.Group()
    # Start text
    startup = pygame.sprite.Group()
    # Other Text
    screen_text = pygame.sprite.Group()
    # Score text
    score_display = pygame.sprite.Group()
    # Beating score text
    beating_scores = pygame.sprite.Group()
    # This separates the clouds to make sure they are drawn first
    all_but_clouds = pygame.sprite.Group()

    # Variable to keep the game running
    running = True
    # And to track if player is alive
    alive = False
    # Save score is used so it doesn't save the scores multiple times
    save_score = False
    # Get score, get it at the beginning to track if you have a high score
    get_score = False
    # Tells the game to level up and increase the enemy spawn rate
    level_up = True
    # Used to differentiate between start up screen and when the game starts
    start_game = False
    # Used to add the start up text to a group
    start_up = True
    # Tells the game if the help screen can be displayed
    help_screen = True
    # Tells the game to show the text at the end of the game
    end_text = False

    # Game Loop
    while running:
        for event in pygame.event.get():
            # Check for keypress event
            if event.type == KEYDOWN:
                # Check is esc key was pressed
                # And if it is, quit the game
                if event.key == K_ESCAPE:
                    running = False
                # On pressing enter, it will give game info. If you haven't started and you press it again
                # it will take you back to the start screen
                # If you have started, it will return you to the game
                elif event.key == K_RETURN:
                    sprite_removal_group(startup)
                    if help_screen:
                        new_help_screen = game_objects.HelpScreen(display_size)
                        startup.add(new_help_screen)
                        help_screen = False
                    else:
                        help_screen = True
                        if not start_game:
                            startup_text = game_objects.StartText(display_size)
                            startup.add(startup_text)
                # Check if space was pressed
                elif event.key == K_SPACE:
                    # If it is, remove player and enemy sprites
                    sprite_removal_group(all_but_clouds)
                    sprite_removal_group(screen_text)
                    # Set the score back to 0
                    game_objects.Enemy.score = 0
                    # and lives back to the starting life total
                    game_objects.Water.lives = config_map["starting_lives"]
                    # Re-create the player, add them to the group, and set them to alive
                    player = game_objects.Player(display_size)
                    all_but_clouds.add(player)
                    sprite_removal_group(startup)
                    # Loads all the game text
                    score_text = game_objects.ScoreText()
                    exit_text = game_objects.ExitText(display_size)
                    life_text = game_objects.LifeText()
                    screen_text.add(score_text)
                    screen_text.add(exit_text)
                    screen_text.add(life_text)
                    top_scores = file_io.load_scores()
                    alive = True
                    # Set the var to start_game
                    start_game = True
            # Check for quit event
            elif event.type == QUIT:
                running = False
            # Checks for the event to create an Enemy
            elif event.type == ADDENEMY:
                # Creates and adds to the enemy group
                new_enemy = game_objects.Enemy(display_size, config_map["enemy_min_speed"], config_map["enemy_max_speed"])
                enemies.add(new_enemy)
                all_but_clouds.add(new_enemy)
            elif event.type == ADDCLOUD:
                # Creates and adds to the cloud group
                new_cloud = game_objects.Cloud(display_size)
                clouds.add(new_cloud)
            elif event.type == ADDGEM:
                # Creates and adds to the gem group
                new_gem = game_objects.Gem(display_size)
                gems.add(new_gem)
                all_but_clouds.add(new_gem)
            elif event.type == ADDWATER:
                # Creates and adds to water group
                new_water = game_objects.Water(display_size)
                water_drops.add(new_water)
                all_but_clouds.add(new_water)

        # This run when the game starts_up
        if alive == False and start_up:
            startup_text = game_objects.StartText(display_size)
            startup.add(startup_text)
            start_up = False

        # Increase the amount of bullets as you get more points
        while level_up:
            if game_objects.Enemy.score <= config_map["first_level_up"]:
                pygame.time.set_timer(ADDENEMY, config_map["enemy_spawn_rate"])
                level_up = False
            elif game_objects.Enemy.score >= config_map["first_level_up"] + 1 and game_objects.Enemy.score <= config_map["second_level_up"]:
                pygame.time.set_timer(ADDENEMY, config_map["enemy_spawn_rate"] - config_map["level_up_spawn_increase"])
                level_up = False
            elif game_objects.Enemy.score > config_map["second_level_up"]:
                pygame.time.set_timer(ADDENEMY, config_map["enemy_spawn_rate"] - (config_map["level_up_spawn_increase"] * 2))
                level_up = False
        if game_objects.Enemy.score == config_map["first_level_up"] + 1 and config_map["game_level_up"]:
            level_up = True
        elif game_objects.Enemy.score == config_map["second_level_up"] + 2 and config_map["game_level_up"]:
            level_up = True

        # Draws the background
        screen.blit(background, (0, 0))
        # This draws all sprites on to the screen
        # Making sure clouds are drawn first
        clouds.draw(screen)
        if start_game:
            all_but_clouds.draw(screen)
            screen_text.draw(screen)
            # Draws the life heart on the screen
            # And increases and decreases when you get / lose life
            for x in range(0 + game_objects.Water.lives):
                heart = game_objects.Heart((x + 1) * 35, True)
                screen.blit(heart.image, heart.rect)
                health_range = x + 1
            for x in range(config_map["max_lives"] - game_objects.Water.lives):
                if game_objects.Water.lives > 0:
                    heart = game_objects.Heart((health_range + x + 1) * 35, False)
                else:
                    heart = game_objects.Heart((x + 1) * 35, False)
                screen.blit(heart.image, heart.rect)
            sprite_removal_group(score_display)
            # This draws the score on the screen
            x_counter = 0
            for digit in str(game_objects.Enemy.score):
                new_number = game_objects.NumbersText(int(digit), (220 + (30 * x_counter), 90))
                score_display.add(new_number)
                x_counter += 1
            score_display.draw(screen)
        # Draws the start up text
        startup.draw(screen)

        # Saves the score, then set to false to it doesn't run again
        while save_score:
            if game_objects.Enemy.score > 0:
                file_io.save_score(game_objects.Enemy.score)
            save_score = False

        # Gets the scores and adds them to the screen test group to be printed
        if get_score:
            # Loads the scores
            top_scores = file_io.load_scores()
            counter = 0
            # For each number in the top_scores
            for row in top_scores:
                x_counter = 0
                row_length = len(row)
                # For each digit in that row
                for digit in row:
                    # Creates a new number object, with the digit, and the rect.
                    # Doing the spacing based on the index of the number
                    score_x_axis = ((display_size["display_w"] / 2 - (row_length * 15)) + 30 * x_counter)
                    score_y_axis = ((display_size["display_h"] / 100) * 43 + (50 * counter))
                    new_number = game_objects.NumbersText(int(digit), (score_x_axis, score_y_axis))
                    screen_text.add(new_number)
                    x_counter += 1
                counter += 1
            get_score = False

        # Gets the end text, and adds it to the screen_text group to be printed
        if end_text:
            restart_text = game_objects.RestartText(display_size)
            top_scores_text = game_objects.TopScoresText(display_size)
            screen_text.add(restart_text)
            screen_text.add(top_scores_text)
            end_text = False

        # This gets the key press and passes to the player class
        if alive:
            pressed_keys = pygame.key.get_pressed()
            player.update(pressed_keys, display_size)
            # When the enemies and player collide, kill the player
            # and set save_score to true so that while loop activates
            if pygame.sprite.spritecollide(player, gems, False):
                for gem in pygame.sprite.spritecollide(player, gems, False):
                    if gem.name == "gem1":
                        game_objects.Enemy.score += config_map["gem1_score"]
                    elif gem.name == "gem2":
                        game_objects.Enemy.score += config_map["gem2_score"]
                    elif gem.name == "gem3":
                        game_objects.Enemy.score += config_map["gem3_score"]
                    elif gem.name == "gem4":
                        game_objects.Enemy.score += config_map["gem4_score"]
                    elif gem.name == "gem5":
                        game_objects.Enemy.score += config_map["gem5_score"]
                sprite_removal(gem)

            # Collision logic for the water
            if pygame.sprite.spritecollideany(player, water_drops):
                for water in pygame.sprite.spritecollide(player, water_drops, False):
                    if game_objects.Water.lives < config_map["max_lives"]:
                        game_objects.Water.lives += 1
                    hearts.empty()
                    sprite_removal(water)
            # Collision logic for the fire
            if pygame.sprite.spritecollideany(player, enemies):
                game_objects.Water.lives -= 1
                hearts.empty()
                for enemy in pygame.sprite.spritecollide(player, enemies, False):
                    sprite_removal(enemy)
                if game_objects.Water.lives <= 0:
                    sprite_removal(player)
                    alive = False
                    save_score = True
                    get_score = True
                    end_text = True

            # Checks against the high score to see if you are beating any
            sprite_removal_group(beating_scores)
            amount_of_scores = len(top_scores)
            counter = 1
            while counter <= amount_of_scores:
                if game_objects.Enemy.score > int(top_scores[amount_of_scores - counter]):
                    new_beating_score = game_objects.BeatingScores(display_size, (amount_of_scores - counter))
                    sprite_removal_group(beating_scores)
                    beating_scores.add(new_beating_score)
                counter += 1
            beating_scores.draw(screen)

        # Moves the sprites (except player)
        enemies.update(alive)
        clouds.update()
        gems.update()
        water_drops.update()
        startup.update()

        # This updates the screen so its actually shown
        pygame.display.flip()

        # This ticks the FPS clock
        fps_clock.tick(fps)


# Function to remove sprites from sprite group
def sprite_removal_group(sprite_group):
    for sprite in sprite_group:
        sprite_removal(sprite)


# Function to remove sprites
def sprite_removal(sprite):
    sprite.kill()
    del sprite
