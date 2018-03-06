import pygame
import requests

size = 600, 450


# CODE

pygame.init()
pygame.display.set_mode(size)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    pygame.display.flip()

pygame.quit()
