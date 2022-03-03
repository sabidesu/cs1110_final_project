# jed5gpx - final project - a platforming game similar to mario
# REQUIREMENTS
# user input - P1 will use arrow keys. P2 will use wASD
# graphics/images - planning on implementing a sprite sheet? or at least some
#     custom sprites that i make. probably in pixel art form
# start screen -
#     - title???
#     - jed5gpx
#     - move with p1 - arrow keys/p2 - WASD. collect coins. don't touch enemies
# small enough window - it's gonna be 800x600
# OPTIONAL FEATURES
# animation - COMPLETE
# enemies - COMPLETE
# collectibles - COMPLETE
# scrolling level - COMPLETE
# two players - COMPLETE
# GAMEBOX DOCUMENTATION - https://cs1110.cs.virginia.edu/gamebox.html
# GAMEBOX QUICK START - https://cs1110.cs.virginia.edu/gamebox-summary.html

# import the necessary modules
import pygame
import gamebox

# define world vars
screen_w = 800
screen_h = 600
camera = gamebox.Camera(screen_w, screen_h)  # init camera
tile_size = 40  # turns the screen into a 20x15 grid

# speed vars
player_speed = 7
enemy_speed = 5
# acceleration is how fast the players actually move
player1_accel = 0
player2_accel = 0
accel_fast = 1  # acceleration when moving in opposite direction
accel_slow = .5  # acceleration when slowing naturally

# game state vars
p2_enable = False  # is player two playing?
game_start = False  # has the game started?
# global vars for rotation
# used for animation direction. 0 is to the right, 180 to left
FACING_LEFT = 180
FACING_RIGHT = 0

# create players and world vars affecting players
p1_sprite_sheet = gamebox.load_sprite_sheet("assets/p1.png", 1, 3)
p2_sprite_sheet = gamebox.load_sprite_sheet("assets/p2.png", 1, 3)
p1 = gamebox.from_image(360, 300, p1_sprite_sheet[0])
p1.scale_by(1.2)  # make players slightly bigger since sprite sheets small
p1.facing = FACING_RIGHT
p1.curr_frame = 0
p2 = gamebox.from_image(440, 300, p2_sprite_sheet[0])
p2.scale_by(1.2)
p2.facing = FACING_RIGHT
p2.curr_frame = 0
players = []  # put players in list for easier...everything
score = 0  # this is a co-op score, no individual scores
gravity = 3
jump_accel = 40  # a variable for controlling jump height
p1.in_air, p2.in_air = [False] * 2  # lets us know if player is jumping
# also load other sprite sheets because don't wanna do it constantly
coin_sprite_sheet = gamebox.load_sprite_sheet("assets/coin.png", 1, 10)
enemy_sprite_sheet = gamebox.load_sprite_sheet("assets/enemy.png", 1, 3)

# create a level, each level will be 80 by 15, according to our screen grid
# import file containing level data
# . = nothing, 1 = p1 spawn, 2 = p2 spawn, x = platform, o = coin, X = enemy
level = []
platforms = []
coins = []
enemies = []


def level_create():
    """
    redraw the level entirely from the text file 'level.txt'
    :return: N/A
    """
    global level, platforms, coins, enemies
    level.clear()
    platforms.clear()
    coins.clear()
    enemies.clear()

    filename = "level.txt"
    f_stream = open(filename, 'r')

    for line in f_stream:
        line = line.strip('\n')
        level.append(line)
    f_stream.close()  # close the file
    # create gameboxes for level elements
    for y in range(len(level)):  # each line is the y of our grid
        for x in range(len(level[y])):  # each char is the x of our grid
            # create positions based on our grid
            # - tile_size / 2 bc center of gamebox is it's origin
            x_pos = (x + 1) * tile_size - tile_size / 2
            y_pos = (y + 1) * tile_size - tile_size / 2
            if level[y][x] == '.':
                continue  # don't waste resources
            elif level[y][x] == 'x':  # add platforms
                platforms.append(gamebox.from_image(x_pos, y_pos,
                                                    "assets/platform.png"))
            elif level[y][x] == 'o':  # add coins
                coins.append(gamebox.from_image(x_pos, y_pos,
                                                coin_sprite_sheet[0]))
                coins[-1].curr_frame = 0  # set frame for animation
            elif level[y][x] == 'X':  # add enemies
                enemies.append(gamebox.from_image(x_pos, y_pos,
                                                  enemy_sprite_sheet[0]))
                enemies[-1].curr_frame = 0  # set frame for animation
                enemies[-1].facing = FACING_RIGHT
                enemies[-1].scale_by(1.2)
            # change player spawn
            elif level[y][x] == '1':
                p1.x, p1.y = x_pos, y_pos
            elif level[y][x] == '2':
                p2.x, p2.y = x_pos, y_pos


def move_p1(keys):
    """
    moves player 1
    :param keys: list of currently held keys
    :return: N/A
    """
    global player1_accel
    # p1 movement
    # only want them to move if enabled
    if p1 in players:
        if pygame.K_RIGHT in keys:
            if player1_accel < 0:  # if headed left, slow faster
                player1_accel += accel_fast
            else:
                player1_accel += accel_slow
            if player1_accel > player_speed:  # accel can't exceed max speed
                player1_accel = player_speed
        if pygame.K_LEFT in keys:
            if player1_accel > 0:  # if headed right, slow faster
                player1_accel -= accel_fast
            else:
                player1_accel -= accel_slow
            # accel can't exceed max speed
            if abs(player1_accel) > player_speed:
                player1_accel = -player_speed
        # if nothing is being pressed, slow p1 down
        if pygame.K_LEFT not in keys and pygame.K_RIGHT not in keys:
            if player1_accel < 0:
                player1_accel += accel_slow
            elif player1_accel > 0:
                player1_accel -= accel_slow
        p1.x += player1_accel  # move the player according to their acceleration

        # animate the player's movement
        if player1_accel > 0:
            p1.curr_frame += 1
            if p1.curr_frame == 30:
                p1.curr_frame = 0
            p1.image = p1_sprite_sheet[int(p1.curr_frame / 10)]
            # if player facing left, turn them towards right
            if p1.facing == FACING_LEFT:
                p1.facing = FACING_RIGHT
                p1.flip()
        elif player1_accel < 0:
            p1.curr_frame += 1
            if p1.curr_frame == 30:
                p1.curr_frame = 0
            p1.image = p1_sprite_sheet[int(p1.curr_frame / 10)]
            if p1.facing == FACING_RIGHT:
                p1.facing = FACING_LEFT
                p1.flip()


def move_p2(keys):
    """
    moves player 2
    :param keys: list of currently held keys
    :return: N/A
    """
    global player2_accel

    # p2 movement
    # only want them to move if enabled
    if p2 in players:
        if pygame.K_d in keys:
            if player2_accel < 0:  # if headed left, slow faster
                player2_accel += accel_fast
            else:
                player2_accel += accel_slow
            if player2_accel > player_speed:  # accel can't exceed max speed
                player2_accel = player_speed
        if pygame.K_a in keys:
            if player2_accel > 0:  # if headed right, slow faster
                player2_accel -= accel_fast
            else:
                player2_accel -= accel_slow
            # accel can't exceed max speed
            if abs(player2_accel) > player_speed:
                player2_accel = -player_speed
        # if nothing is being pressed, slow p2 down
        if pygame.K_d not in keys and pygame.K_a not in keys:
            if player2_accel < 0:
                player2_accel += accel_slow
            elif player2_accel > 0:
                player2_accel -= accel_slow
        p2.x += player2_accel  # move the player according to their acceleration

        if player2_accel > 0:
            p2.curr_frame += 1
            if p2.curr_frame == 30:
                p2.curr_frame = 0
            p2.image = p2_sprite_sheet[int(p2.curr_frame / 10)]
            # if player facing left, turn them towards right
            if p2.facing == FACING_LEFT:
                p2.facing = FACING_RIGHT
                p2.flip()
        elif player2_accel < 0:
            p2.curr_frame += 1
            if p2.curr_frame == 30:
                p2.curr_frame = 0
            p2.image = p2_sprite_sheet[int(p2.curr_frame / 10)]
            if p2.facing == FACING_RIGHT:
                p2.facing = FACING_LEFT
                p2.flip()


def collisions(keys):
    """
    sets the rules for world collision, and certain player/enemy movement
    :return: N/A
    """
    global score, game_start  # needed for modification

    for player in players:
        p_index = players.index(player)
        for platform in platforms:
            if player.touches(platform, tile_size * 3):
                player.move_to_stop_overlapping(platform)
            # add jumping logic in this function so we're not checking for the
            # same collisions repeatedly
            if player.bottom_touches(platform):
                player.jump_speed = 0
                player.in_air = False
                # determine jump key based on player
                if players[p_index] == p1:  # is equal to player 1 object?
                    jump_key = pygame.K_UP
                else:  # player 2
                    jump_key = pygame.K_w
                if jump_key in keys:
                    player.jump_speed = jump_accel
                    player.y -= player.jump_speed
                    player.in_air = True
                break  # don't check rest of platforms if on ground
            else:
                player.in_air = True  # keep checking if in air
        # if in air, move them back towards ground
        if jump_accel >= player.jump_speed and player.in_air:
            player.jump_speed -= gravity  # accelerate fall speed
            player.y -= player.jump_speed

        for coin in coins:
            if player.touches(coin):
                # padding smaller than coin bc smaller sprite
                coins.remove(coin)
                score += 1
            # control animations
            coin.curr_frame += 1
            if coin.curr_frame == 100:  # wrap back to first frame
                coin.curr_frame = 0
            coin.image = coin_sprite_sheet[int(coin.curr_frame / 10)]
        for enemy in enemies:
            if player.bottom_touches(enemy):
                enemies.remove(enemy)  # kill the enemy
                break  # in case player kills multiple enemies at once
            elif player.left_touches(enemy) or player.right_touches(enemy) \
                    or player.top_touches(enemy):
                players.remove(player)  # kill the player
                break  # in case the player dies to multiple enemies at once

        # technically not a collision, but kill a player if they fall out
        if player.y > camera.y + screen_h / 2:
            players.remove(player)

    # enemies also collide with ground / other enemies
    # uses same logic as player falling
    for i in range(len(enemies)):
        enemy = enemies[i]
        for platform in platforms:
            if enemy.touches(platform):
                enemy.move_to_stop_overlapping(platform)
            if enemy.bottom_touches(platform):
                enemy.in_air = False
                enemy.fall_speed = 0
                break
            else:
                enemy.in_air = True
        if enemy.in_air:
            enemy.fall_speed -= gravity
            enemy.y -= enemy.fall_speed

        # also control enemy movement
        # determine which player to go for first based on who's alive.
        # if both are alive, then whoever is closer
        if p1 not in players:
            if p2.x == enemy.x:
                pass
            elif abs(p2.x - enemy.x) < enemy_speed:
                enemy.x = p2.x
                enemy.curr_frame += 1
            elif p2.x > enemy.x:
                enemy.x += enemy_speed
                enemy.curr_frame += 1
                if enemy.facing == FACING_LEFT:
                    enemy.facing = FACING_RIGHT
                    enemy.flip()
            else:
                enemy.x -= enemy_speed
                enemy.curr_frame += 1
                if enemy.facing == FACING_RIGHT:
                    enemy.facing = FACING_LEFT
                    enemy.flip()
        elif p2 not in players:
            if p1.x == enemy.x:
                pass
            # make sure enemies don't glitch out when directly beneath player
            elif abs(p1.x - enemy.x) < enemy_speed:
                enemy.x = p1.x
                enemy.curr_frame += 1  # bring them closer to next frame
            # otherwise move them normally
            elif p1.x > enemy.x:
                enemy.x += enemy_speed
                enemy.curr_frame += 1
                # if facing to the left, turn them to the right
                if enemy.facing == FACING_LEFT:
                    enemy.facing = FACING_RIGHT
                    enemy.flip()
            elif p1.x < enemy.x:
                enemy.x -= enemy_speed
                enemy.curr_frame += 1
                # if facing to the right, turn them to the left
                if enemy.facing == FACING_RIGHT:
                    enemy.facing = FACING_LEFT
                    enemy.flip()
        elif abs(p1.x - enemy.x) < abs(p2.x - enemy.x):
            if p1.x == enemy.x:
                pass
            # make sure enemies don't glitch out when directly beneath player
            elif abs(p1.x - enemy.x) < enemy_speed:
                enemy.x = p1.x
                enemy.curr_frame += 1  # bring them closer to next frame
            # otherwise move them normally
            elif p1.x > enemy.x:
                enemy.x += enemy_speed
                enemy.curr_frame += 1
                # if facing to the left, turn them to the right
                if enemy.facing == FACING_LEFT:
                    enemy.facing = FACING_RIGHT
                    enemy.flip()
            elif p1.x < enemy.x:
                enemy.x -= enemy_speed
                enemy.curr_frame += 1
                # if facing to the right, turn them to the left
                if enemy.facing == FACING_RIGHT:
                    enemy.facing = FACING_LEFT
                    enemy.flip()
        else:
            if p2.x == enemy.x:
                pass
            elif abs(p2.x - enemy.x) < enemy_speed:
                enemy.x = p2.x
                enemy.curr_frame += 1
            elif p2.x > enemy.x:
                enemy.x += enemy_speed
                enemy.curr_frame += 1
                if enemy.facing == FACING_LEFT:
                    enemy.facing = FACING_RIGHT
                    enemy.flip()
            else:
                enemy.x -= enemy_speed
                enemy.curr_frame += 1
                if enemy.facing == FACING_RIGHT:
                    enemy.facing = FACING_LEFT
                    enemy.flip()
        # reset enemy current frame if max frame reached
        if enemy.curr_frame == 30:
            enemy.curr_frame = 0
        enemy.image = enemy_sprite_sheet[int(enemy.curr_frame / 10)]

        for j in range(len(enemies)):
            enemy2 = enemies[j]
            if enemy != enemy2:  # so the enemy doesn't move from itself
                if enemy.touches(enemy2):
                    enemy.move_to_stop_overlapping(enemy2)

    # let players collide with each other
    if p1.touches(p2):
        p1.move_to_stop_overlapping(p2)
    if p2.touches(p1):
        p2.move_to_stop_overlapping(p1)

    if len(players) == 0:
        game_start = False  # end the game if all players dead


def game(keys):
    """
    defines the main gameplay loop
    :param keys: list of currently held keys
    :return: N/A
    """
    camera.clear("#99ddfc")  # make the sky
    move_p1(keys)  # call the function for moving player 1
    for player in players:  # draw all the players (even if there's just 1)
        camera.draw(player)
    if p2_enable:  # if p2 is enabled, change some mechanics
        move_p2(keys)  # allow their movement
        if p1 in players and p2 in players:
            # move cam to center both players...
            camera.x = (p1.x + p2.x) / 2
        elif p1 in players:
            camera.x = p1.x  # ...unless a player is dead
        elif p2 in players:
            camera.x = p2.x
    else:
        camera.x = p1.x  # move cam to center player 1
    # call function for handling collision events, jumping, and enemy movement
    # all done in same function for sake of performance
    collisions(keys)

    # draw score
    camera.draw(gamebox.from_text(camera.x, 50, str(score), 64, "white"))

    # draw the level
    # only draw the elements if they're onscreen
    hori_bound = screen_w / 2 + 400 + tile_size / 2  # bound for drawing
    for platform in platforms:
        if camera.x + hori_bound > platform.x > camera.x - hori_bound:
            camera.draw(platform)
    for coin in coins:
        if camera.x + hori_bound > coin.x > camera.x - hori_bound:
            camera.draw(coin)
    for enemy in enemies:
        if camera.x + hori_bound > enemy.x > camera.x - hori_bound:
            camera.draw(enemy)


def draw_start_screen(keys):
    """
    draws the initial start screen
    :param keys: list of currently held keys
    :return: N/A
    """
    global game_start, players, p2_enable, score

    camera.clear("black")

    # create a title screen
    title = gamebox.from_text(camera.x, 150, "acceptance", 72, "white")
    author = gamebox.from_text(camera.x, 195, "by jed5gpx", 48, "white")
    instructions = ["press SPACE for 1 player",
                    "press ENTER or RETURN for 2 players",
                    "",
                    "collect coins for score",
                    "touching an enemy kills you",

                    "it's that simple",
                    "p1 - arrow keys",
                    "p2 - WASD"]
    camera.draw(title)
    camera.draw(author)
    # draw the instructions line by line since we want them aligned
    instructions_x = 400
    instructions_y = 275
    for line in instructions:
        camera.draw(line, 36, "white", instructions_x, instructions_y)
        instructions_y += 36

    if pygame.K_SPACE in keys:  # SPACE disables multiplayer
        game_start = True
        players = [p1]  # add player 1
        score = 0  # reset score
        level_create()
    if pygame.K_RETURN in keys:  # ENTER enables multiplayer
        game_start = True
        p2_enable = True
        players = [p1, p2]  # add player 1 and player 2
        score = 0  # reset score
        level_create()


def tick(keys):
    """
    the method that will be called every frame
    :param keys: the list of currently pressed keys
    :return: N/A
    """
    if not game_start:  # on game init, draw title
        draw_start_screen(keys)
    else:  # then enter main game loop
        game(keys)
    camera.display()


ticks_per_second = 60  # buttery smooth game
gamebox.timer_loop(ticks_per_second, tick)
