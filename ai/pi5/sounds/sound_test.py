import pygame

pygame.mixer.init()
sound = pygame.mixer.Sound("left.wav")
sound.play()

# Keep the script running until the sound finishes playing
while pygame.mixer.get_busy():
    pygame.time.delay(10)