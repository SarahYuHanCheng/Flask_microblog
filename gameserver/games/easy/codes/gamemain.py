from p76051080 import p1
import multiprocessing,time

global numbers
import pygame, sys, time
#print(sys.argv[1])
def __init__():
    numbers = [1,2,3]
    result = multiprocessing.Array('i',3)
    mp1=multiprocessing.Process(target=p1, args=(numbers, result))
    mp1.start()
    mp1.join()
    game(result)

def game(result):
    print("call game")
    background_colour = (255,255,255)
    (width, height) = (300, 200)
    BLUE = (0,0,225)
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Tutorial 1')
    screen.fill(background_colour)
    pygame.draw.circle(screen, BLUE, (50,50), 20)

    # pygame.display.flip()
    running = True
    for idx, n in enumerate(result):
                result[idx] = n+1
                print(result[idx])
    # while running:
    #     for idx, n in enumerate(result):
    #             result[idx] = n+1
    #     print('in main:',result)
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #         time.sleep(1)

__init__()