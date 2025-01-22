import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True

class DraggableCircle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.dragging = False
        self.scale = 1.0
        
    def draw(self):
        pygame.draw.circle(screen, (50, 125, 155), 
                         (int(self.x), int(self.y)), 
                         int(self.radius * self.scale),5)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_clicked(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.x, self.y = event.pos
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if ((mouse_y - self.y)**2 + (mouse_x - self.x)**2)**0.5 < self.radius:
                self.scale += event.y * 0.1
            
            
    def is_clicked(self, pos):
        return ((self.x - pos[0])**2 + (self.y - pos[1])**2) <= self.radius**2

circles = [DraggableCircle(400, 300, 50),DraggableCircle(40, 30, 50),DraggableCircle(100, 200, 50)]
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for circle in circles:
            circle.handle_event(event)
    screen.fill((200,200,200))
    for circle in circles:
        circle.draw()
    pygame.display.flip()

pygame.quit()



# # pygame setup
# pygame.init()
# screen = pygame.display.set_mode((1280, 720))
# clock = pygame.time.Clock()
# running = True
# dt = 0

# player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

# while running:
#     # poll for events
#     # pygame.QUIT event means the user clicked X to close your window
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # fill the screen with a color to wipe away anything from last frame
#     screen.fill("white")

#     pygame.draw.circle(screen, "red", player_pos, 40)

#     keys = pygame.key.get_pressed()
#     if keys[pygame.K_w]:
#         player_pos.y -= 300 * dt
#     if keys[pygame.K_s]:
#         player_pos.y += 300 * dt
#     if keys[pygame.K_a]:
#         player_pos.x -= 300 * dt
#     if keys[pygame.K_d]:
#         player_pos.x += 300 * dt

#     # flip() the display to put your work on screen
#     pygame.display.flip()

#     # limits FPS to 60
#     # dt is delta time in seconds since last frame, used for framerate-
#     # independent physics.
#     dt = clock.tick(60) / 1000

# pygame.quit()