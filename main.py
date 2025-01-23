import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True
defaultRadius = 100;

class DraggableCircle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.dragging = False
        self.scale = 1.0
        self.selected = False
        
    def distance_to_point(self, point):
        return ((self.x - point[0])**2 + (self.y - point[1])**2)**0.5

    def snap_to_closest_circle_edge(self, circles):
        SNAP_RADIUS = 30
        if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
            return
            
        # First check intersections
        for i in range(len(circles)):
            for j in range(i+1, len(circles)):
                if circles[i] != self and circles[j] != self:
                    points = find_intersections(circles[i], circles[j])
                    for point in points:
                        if ((point[0] - self.x)**2 + (point[1] - self.y)**2) < SNAP_RADIUS**2:
                            self.x = point[0]
                            self.y = point[1]
                            return

        # If no intersection points nearby, check circle edges
        for circle in circles:
            if circle != self:
                dx = circle.x - self.x
                dy = circle.y - self.y 
                d = (dx**2 + dy**2)**0.5
                if abs(d - circle.radius * circle.scale) < SNAP_RADIUS:
                    # Normalize and place on edge
                    self.x = circle.x - (dx/d) * circle.radius * circle.scale
                    self.y = circle.y - (dy/d) * circle.radius * circle.scale
                    return
                    
    def snap_to_intersection_points(self, circles):
        SNAP_RADIUS = 30
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT]:
            return
            
        # Get current mouse position for relative movement
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Check all intersection points
        for i in range(len(circles)):
            for j in range(i+1, len(circles)):
                if circles[i] != self and circles[j] != self:
                    points = find_intersections(circles[i], circles[j])
                    for point in points:
                        # Calculate offset to maintain relative movement
                        if self.distance_to_point(point) < SNAP_RADIUS:
                            offset_x = mouse_x - point[0]
                            offset_y = mouse_y - point[1]
                            self.x = mouse_x - offset_x
                            self.y = mouse_y - offset_y
                            return           
    def draw(self):
        if self.selected:
            pygame.draw.circle(screen, (155, 100, 100), 
                         (int(self.x), int(self.y)), 
                         int(self.radius * self.scale),2)
            pygame.draw.circle(screen, (255, 200, 200), 
                         (int(self.x), int(self.y)), 
                         3,2)
        else:
            pygame.draw.circle(screen, (50, 125, 155), 
                            (int(self.x), int(self.y)), 
                            int(self.radius * self.scale),2)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_clicked(event.pos):
                for circle in circles:
                    circle.selected = False
                self.selected = True
                self.dragging = True
            else:
                self.selected = False
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging and self.selected:
            self.x, self.y = event.pos
            self.snap_to_closest_circle_edge(circles)
            self.snap_to_intersection_points(circles)
        elif event.type == pygame.MOUSEWHEEL and self.selected:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if ((mouse_y - self.y)**2 + (mouse_x - self.x)**2)**0.5 < self.radius:
                self.scale += event.y * 0.1
            
    def is_clicked(self, pos):
        return ((self.x - pos[0])**2 + (self.y - pos[1])**2) <= self.radius**2
  
circles = [DraggableCircle(400, 300, defaultRadius),DraggableCircle(40, 30, defaultRadius),DraggableCircle(100, 200, defaultRadius)]
def find_intersections(circle1, circle2):
    dx = circle2.x - circle1.x
    dy = circle2.y - circle1.y
    d = (dx**2 + dy**2)**0.5
    r1 = circle1.radius * circle1.scale
    r2 = circle2.radius * circle2.scale
    if d == 0:
        return []
    # Check if circles intersect
    if d > r1 + r2 or d < abs(r1 - r2):
        return []
    
    # Find intersection points
    a = (r1**2 - r2**2 + d**2)/(2*d)
    h = (r1**2 - a**2)**0.5
    
    x2 = circle1.x + (dx * a)/d
    y2 = circle1.y + (dy * a)/d
    
    # Calculate intersection points
    ix1 = x2 + h*(dy)/d
    iy1 = y2 - h*(dx)/d
    ix2 = x2 - h*(dy)/d
    iy2 = y2 + h*(dx)/d
    
    return [(ix1, iy1), (ix2, iy2)]
while running:

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                circles = [c for c in circles if not c.selected]
            elif event.key == pygame.K_n:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                circles.append(DraggableCircle(mouse_x, mouse_y, defaultRadius))
        for circle in circles:
            circle.handle_event(event)
    screen.fill((200,200,200))
    for circle in circles:
        circle.draw()
    for i in range(len(circles)):
        for j in range(i+1, len(circles)):
            points = find_intersections(circles[i], circles[j])
            for point in points:
                pygame.draw.circle(screen, (0,0,0), (int(point[0]), int(point[1])), 3)
    pygame.display.flip()

pygame.quit()