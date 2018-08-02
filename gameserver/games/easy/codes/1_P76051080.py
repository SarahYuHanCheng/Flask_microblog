import pygame, sys
#print(sys.argv[1])
background_colour = (255,255,255)
(width, height) = (300, 200)
BLUE = (0,0,225)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tutorial 1')
screen.fill(background_colour)
pygame.draw.circle(screen, BLUE, (50,50), 20)

pygame.display.flip()
running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False