import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True
defaultRadius = 100
circleMode = True
lineMode = False

class Line:
    def __init__(self, start_circles, start_point, end_circles, end_point):
        self.start_circles = start_circles  
        self.end_circles = end_circles
        self.original_start = start_point
        self.original_end = end_point
        
    def get_points(self):  # Renamed from get_current_points for consistency
        start_points = find_intersections(self.start_circles[0], self.start_circles[1])
        end_points = find_intersections(self.end_circles[0], self.end_circles[1])
        
        if not start_points or not end_points:
            return None
            
        start = min(start_points, key=lambda p: ((p[0] - self.original_start[0])**2 + 
                                                (p[1] - self.original_start[1])**2))
        end = min(end_points, key=lambda p: ((p[0] - self.original_end[0])**2 + 
                                            (p[1] - self.original_end[1])**2))
        return (start, end)
        
    def draw(self):
        points = self.get_points()
        if points:
            pygame.draw.line(screen, (30, 85, 105), 
                           (int(points[0][0]), int(points[0][1])),
                           (int(points[1][0]), int(points[1][1])), 4)


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.active = False
        
    def draw(self):
        color = (self.color[0]-50, self.color[1]-50, self.color[2]-50) if self.active else self.color
        pygame.draw.rect(screen, color, self.rect)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
        
    def handle_click(self, pos):
        return self.rect.collidepoint(pos)


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
                         int(self.radius * self.scale),3)
            pygame.draw.circle(screen, (255, 200, 200), 
                         (int(self.x), int(self.y)), 
                         3,2)
        else:
            pygame.draw.circle(screen, (50, 125, 155), 
                            (int(self.x), int(self.y)), 
                            int(self.radius * self.scale),3)
        
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


def find_intersections(circle1, circle2):
    dx = circle2.x - circle1.x
    dy = circle2.y - circle1.y
    d = (dx**2 + dy**2)**0.5
    r1 = circle1.radius * circle1.scale
    r2 = circle2.radius * circle2.scale
    
    if d == 0:
        return []
    if d > r1 + r2 or d < abs(r1 - r2):
        return []
    
    a = (r1**2 - r2**2 + d**2)/(2*d)
    h = (r1**2 - a**2)**0.5
    
    x2 = circle1.x + (dx * a)/d
    y2 = circle1.y + (dy * a)/d
    
    ix1 = x2 + h*(dy)/d
    iy1 = y2 - h*(dx)/d
    ix2 = x2 - h*(dy)/d
    iy2 = y2 + h*(dx)/d
    
    return [(ix1, iy1), (ix2, iy2)]

def find_circle_pair_for_point(pos, circles):
    for i in range(len(circles)):
        for j in range(i+1, len(circles)):
            points = find_intersections(circles[i], circles[j])
            for point in points:
                if ((point[0] - pos[0])**2 + (point[1] - pos[1])**2) < 100:
                    return ((circles[i], circles[j]), point)
    return None

circles = [DraggableCircle(400, 300, defaultRadius),DraggableCircle(450, 350, defaultRadius)]
lines = []
circle_button = Button(10, 10, 30, 40, "o", (150, 200, 150))
line_button = Button(60, 10, 30, 40, "/", (150, 200, 150))
circle_button.active = True
selected_point_circles = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if circle_button.handle_click(event.pos):
                circleMode = True
                lineMode = False
                circle_button.active = True
                line_button.active = False
                selected_point_circles = None  # Reset selection when switching modes
                continue
            elif line_button.handle_click(event.pos):
                circleMode = False
                lineMode = True
                circle_button.active = False
                line_button.active = True
                selected_point_circles = None  # Reset selection when switching modes
                continue
                
            if lineMode:
                result = find_circle_pair_for_point(event.pos, circles)
                if result:
                    circle_pair, clicked_point = result
                    if selected_point_circles is None:
                        selected_point_circles = (circle_pair, clicked_point)
                        for i in range(len(circles)):
                            for j in range(i+1, len(circles)):
                                points = find_intersections(circles[i], circles[j])
                                for point in points:
                                    if point == clicked_point:
                                        pygame.draw.circle(screen, (255,0,0), 
                                                         (int(point[0]), int(point[1])), 5)
                    else:
                        start_circles, start_point = selected_point_circles
                        lines.append(Line(start_circles, start_point, circle_pair, clicked_point))
                        selected_point_circles = None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                circles = [c for c in circles if not c.selected]
                # Remove any lines connected to deleted circles
                lines = [line for line in lines if all(c in circles for c in line.circles1 + line.circles2)]
            elif event.key == pygame.K_n and circleMode:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                circles.append(DraggableCircle(mouse_x, mouse_y, defaultRadius))
                
        if circleMode:
            for circle in circles:
                circle.handle_event(event)
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                pygame.quit()
                exit()

    # Remove lines that no longer have valid intersection points
    lines = [line for line in lines if line.get_points() is not None]

    screen.fill((240,240,240))
    
    circle_button.draw()
    line_button.draw()
    
    for circle in circles:
        circle.draw()
    
    for line in lines:
        line.draw()
        
    for i in range(len(circles)):
        for j in range(i+1, len(circles)):
            points = find_intersections(circles[i], circles[j])
            for point in points:
                is_selected = (selected_point_circles and 
                             (circles[i], circles[j]) == selected_point_circles)
                color = (255, 0, 0) if is_selected else (0, 0, 0)
                pygame.draw.circle(screen, color, (int(point[0]), int(point[1])), 3)
    if selected_point_circles:
        saved_circles, saved_point = selected_point_circles
        pygame.draw.circle(screen, (255, 0, 0), (int(saved_point[0]), int(saved_point[1])), 5)
        pygame.draw.circle(screen, (255, 255, 255), (int(saved_point[0]), int(saved_point[1])), 2)            
    pygame.display.flip()

pygame.quit()