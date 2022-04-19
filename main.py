from datetime import datetime
import pygame
import random
import time
import csv

# Pygame constants and necessary code
pygame.init()  # start pygame
mixer = pygame.mixer  # start audio mixer
mixer.init()
resolution = (1920, 1080)  # screen resolution
screen = pygame.display.set_mode(resolution)  # create display
pygame.mouse.set_visible(False)  # hide the mouse
font = pygame.font.SysFont("Arial", 50)  # set font and size
stim = pygame.image.load('circle.png')
fix = pygame.image.load('fixation.png')
err = pygame.image.load('error.png')
black = (0, 0, 0)  # color codes for later use
white = (255, 255, 255)
grey = (127, 127, 127)
#uniqueID = 0


# Draw content to center of screen (currently just text only)
def draw_screen(content, screen_color, content_color):
    center = (screen.get_width() // 2, screen.get_height() // 2)

    screen.fill(screen_color)
    if isinstance(content, str):
        text = font.render(content, True, content_color)
        text_rect = text.get_rect(center=center)
        screen.blit(text, text_rect)
    else:
        rect = content.get_rect(center=center)
        screen.blit(content, rect)

    pygame.display.update()


# Wait for KEY keypress, then return
def wait(key, t):
    pygame.event.clear()
    start = time.time()
    while time.time() - start < t:  # loop until timout t is hit
        # gets a single event from the event queue
        events = pygame.event.get()

        for event in events:
            # captures the 'KEYDOWN'
            if event.type == pygame.KEYDOWN:
                # gets the key name
                if key and pygame.key.name(event.key) == key:
                    return True
                elif not key and key != '5':  # 5 is the emergency stop key
                    return True
            elif event.type == pygame.NOEVENT:  # if we hit the timeout
                return False
            else:  # we don't care about any other event types
                pass


def wipe():
    draw_screen(fix, grey, black)


def intro():
    # Display introductory text
    draw_screen("Press any key to begin the block of trials...", grey, black)
    wait('', 600)  # wait for keypress with basically infinite timeout time
    wipe()
    time.sleep(2 + random.uniform(0.0, 2.0))  # sleep for inter-trial interval


def block(training=False):
    # Generate randomized trial order (currently only one block of 16)
    length = [50, 150, 250, 350]
    condition = ['l', 'r', 'sh', 'sl']

    trials = []
    for l in length:
        for c in condition:  # for each audio file, make an object
            trial = {
                'filename': str(l) + c + '.wav',
                'catch': False
            }
            trials.append(trial)
    random.shuffle(trials)  # shuffle order of trials to be random
    # Sprinkle in 4 catch blocks such that every 4 trials, at least 1 catch occurs
    temp = [trials[i:i+4] for i in range(0, len(trials), 4)]  # new list of 4-element chunks from trials
    for chunk in temp:  # for every chunk,
        catch = {  # pick a random sound file to play and label as a catch trial (True)
            'filename': str(length[random.randrange(4)]) + condition[random.randrange(4)] + '.wav',
            'catch': True
        }
        # place catch in chunk at a random location
        chunk.insert(random.randrange(len(chunk) + 1), catch)
    # Rejoin all chunks into trial array
    trials = sum(temp, [])

    # Begin block of trials
    for trial in trials:
        sound = mixer.Sound(trial['filename'])  # load the sound
        channel = sound.play()  # start playing on a channel
        while channel.get_busy():  # do nothing until the channel is done playing
            pass

        if not trial['catch']:  # if not catch
            draw_screen(stim, grey, black)  # display visual stimulus
        else:    # if this is a catch trial...
            draw_screen(fix, grey, black)  # display nothing

        start = time.time()  # log start of response window
        if wait('', 2):  # wait for reaction time, max 2 seconds
            end = time.time()  # log end of response window
            reaction_time = int(round((end - start) * 1000, 0))  # calculate trial RT in ms, convert it to integer
            if trial['catch']:  # if they responded and it's a catch trial
                draw_screen(err, grey, black)  # display error sign
                wait('', 1)
        else:  # if False, then >2 seconds elapsed
            reaction_time = -1  # set RT to -1, participant did not respond
        print(reaction_time)
        wipe()

        if not training:  # if this is not a training block
            uniqueID = time.time_ns()
            #global uniqueID += 1
            log[(trial['filename'], trial['catch'], uniqueID)] = reaction_time  # create a log: "150l.wav, False: 400"
        time.sleep(2 + random.uniform(0.0, 2.0))  # sleep for inter-trial interval 


log = {}  # data will be saved to a log dictionary object
# Study is composed of 4 sessions, each with 5 blocks
# First, we have one training block
intro()
block(training=True)
# Then we begin the 4 sessions
# intro()
timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")

for sessions in range(0, 4):
    # Each with 5 blocks
    intro()  # prompt the user to begin the block

    for blocks in range(0, 5):
        block(training=False)  # run a non-training block for data collection
        with open(timestamp, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerows(log.items())
# Once we're done, save log dictionary to a local file
# dd_mm_YY_H_M.csv


# then close pygame
pygame.quit()
