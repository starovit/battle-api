import pygame
import time

def show_map():
    pygame.init()
    window_size = (360, 360)
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    pygame.display.set_caption("Agent-Based Simulation")


    running = True
    while running:
        # Load image from file
        try:
            image_data = pygame.image.load("database/teritory.png")
            image_data = pygame.transform.scale(image_data, window_size)
        except:
            pass
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Update the window size
                window_size = event.size
                screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)

                # Scale the image to new window size
                image_data = pygame.transform.scale(image_data, window_size)

        # Display the scaled image
        screen.blit(image_data, (0, 0))
        pygame.display.flip()

        time.sleep(0.1)  # Short pause

    pygame.quit()

if __name__ == '__main__':
    show_map()
