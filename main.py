import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True
defaultRadius = 100
circleMode = True
lineMode = False

class Line:
    def __init__(self, start_intersection, start_point, end_intersection, end_point):
        self.start_parents = start_intersection  # Fix attribute name
        self.end_parents = end_intersection
        self.original_start = start_point
        self.original_end = end_point
        
    def get_points(self):
        start_points = find_intersections(self.start_parents[0], self.start_parents[1])
        end_points = find_intersections(self.end_parents[0], self.end_parents[1])
        
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
        SNAP_RADIUS = 20
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
        SNAP_RADIUS = 15
        SNAP_TOLERANCE = 1e-10  # Add tolerance for floating point comparison
        
        if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
            return
            
        mouse_x, mouse_y = pygame.mouse.get_pos()
        intersections = find_all_intersections(circles, lines)
        
        for intersection in intersections:
            dist = ((intersection.point[0] - self.x)**2 + (intersection.point[1] - self.y)**2)**0.5
            if dist < SNAP_RADIUS:
                # Snap directly to point without offset calculation
                self.x = intersection.point[0]
                self.y = intersection.point[1]
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
    EPSILON = 1e-10
    dx = circle2.x - circle1.x
    dy = circle2.y - circle1.y
    d = (dx**2 + dy**2)**0.5
    r1 = circle1.radius * circle1.scale
    r2 = circle2.radius * circle2.scale
    if abs(d) < EPSILON:  # Check near-zero with tolerance
        return []
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

def line_line_intersection(line1, line2):
    p1 = line1.get_points()
    p2 = line2.get_points()
    if not p1 or not p2:
        return None
    
    x1, y1 = p1[0]
    x2, y2 = p1[1]
    x3, y3 = p2[0]
    x4, y4 = p2[1]
    
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:  # Check for near-zero denominator
        return None
        
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)
    return None

def find_circle_pair_for_point(pos, circles):
    for i in range(len(circles)):
        for j in range(i+1, len(circles)):
            points = find_intersections(circles[i], circles[j])
            for point in points:
                if ((point[0] - pos[0])**2 + (point[1] - pos[1])**2) < 100:
                    return ((circles[i], circles[j]), point)
    return None
class Intersection:
    def __init__(self, point, parents):
        self.point = point  # (x,y)
        self.parents = parents  # List of parent objects (circles/lines)
    
    def draw(self, is_selected=False):
        color = (255, 0, 0) if is_selected else (0, 0, 0)
        pygame.draw.circle(screen, color, (int(self.point[0]), int(self.point[1])), 3)
        if is_selected:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.point[0]), int(self.point[1])), 2)

def find_all_intersections(circles, lines):
    intersections = []
    
    # Circle-Circle intersections
    for i in range(len(circles)):
        for j in range(i+1, len(circles)):
            points = find_intersections(circles[i], circles[j])
            for point in points:
                intersections.append(Intersection(point, [circles[i], circles[j]]))
                
    # Line-Line intersections
    for i in range(len(lines)):
        for j in range(i+1, len(lines)):
            point = line_line_intersection(lines[i], lines[j])
            # print(f"Line intersection: {point}")  # Debug
            if point:
                intersections.append(Intersection(point, [lines[i], lines[j]]))
    
    # print(f"Total intersections: {len(intersections)}")  # Debug
    return intersections

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
                intersections = find_all_intersections(circles, lines)
                clicked_intersection = None
                for intersection in intersections:
                    if ((intersection.point[0] - event.pos[0])**2 + 
                        (intersection.point[1] - event.pos[1])**2) < 100:
                        clicked_intersection = intersection
                        break
                        
                if clicked_intersection:
                    if selected_point_circles is None:
                        selected_point_circles = clicked_intersection
                    else:
                        start_intersection = selected_point_circles
                        lines.append(Line(start_intersection.parents, start_intersection.point,
                                        clicked_intersection.parents, clicked_intersection.point))
                        selected_point_circles = None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                circles = [c for c in circles if not c.selected]
                lines = [line for line in lines if all(c in circles for c in 
                        [p for p in line.start_parents + line.end_parents if isinstance(p, DraggableCircle)])]

            elif event.key == pygame.K_n and circleMode:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                circles.append(DraggableCircle(mouse_x, mouse_y, defaultRadius))
            elif event.key == pygame.K_c :
                lines = []
                circles = []
                intersections = []   
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
    intersections = find_all_intersections(circles, lines)
    for intersection in intersections:
        intersection.draw(is_selected=(intersection == selected_point_circles))
           
    for i in range(len(circles)):
        for j in range(i+1, len(circles)):
            points = find_intersections(circles[i], circles[j])
            for point in points:
                is_selected = (selected_point_circles and 
                             (circles[i], circles[j]) == selected_point_circles)
                color = (255, 0, 0) if is_selected else (0, 0, 0)
                pygame.draw.circle(screen, color, (int(point[0]), int(point[1])), 3)
    if selected_point_circles:
        selected_point_circles.draw(is_selected=True)
        
    pygame.display.flip()

pygame.quit()