import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 400  # Height is half to make it 2:1 aspect ratio (equirectangular)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("360 Degree Image Viewer")

# Load the equirectangular image (path to your stitched 360 image)
image_path = '/home/mdkfahim30/Downloads/Images/360_degree_image.jpg'
image = pygame.image.load(image_path)

# Scale the image to fit the window (optional)
image = pygame.transform.scale(image, (WIDTH, HEIGHT))

# Rotation control
rotation = 0
dragging = False
last_x = 0

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                dragging = True
                last_x = event.pos[0]
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                dx = event.pos[0] - last_x
                rotation += dx  # Adjust rotation based on mouse movement
                last_x = event.pos[0]

    # Clear the screen
    screen.fill((0, 0, 0))

    # Rotate the image
    rotated_image = pygame.transform.rotate(image, rotation)

    # Draw the rotated image
    # To fit the 360-degree image, we need to center it
    new_rect = rotated_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(rotated_image, new_rect.topleft)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
