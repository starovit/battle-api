import pygame
import time

def show_map():
    pygame.init()
    window_size = (600, 600)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Simulation Plot")

    # Load image from file
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Display the image
        try:
            image_data = pygame.image.load("database/teritory.png")
        except:
            pass
        screen.blit(image_data, (0, 0))
        pygame.display.flip()

        time.sleep(0.1)  # Pause for 5 seconds

    pygame.quit()


if __name__ == '__main__':
    show_map()
