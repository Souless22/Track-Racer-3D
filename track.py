from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Window setup
WIN_W = 1000
WIN_H = 800
FOV = 60

# Game state
game_over = False
score = 0

# Car (player)
LANE_WIDTH = 200
LANES = [-LANE_WIDTH, 0, LANE_WIDTH]  # x positions for 3 lanes
car_lane = 1  # start in center lane
car_y = -300  # fixed y
car_z = 50    # fixed z
car_width = 60
car_length = 100

# Obstacles
obstacles = []
OBSTACLE_SPAWN_DIST = 1200
OBSTACLE_SPEED = 15
OBSTACLE_SIZE = 60
OBSTACLE_SPAWN_INTERVAL = 50  # frames

# Camera
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, float(WIN_W) / float(WIN_H), 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Camera follows car from behind and above
    eye_x = LANES[car_lane]
    eye_y = car_y - 600
    eye_z = 350
    cen_x = LANES[car_lane]
    cen_y = car_y + 300
    cen_z = 0
    gluLookAt(eye_x, eye_y, eye_z, cen_x, cen_y, cen_z, 0, 0, 1)

def draw_text(x, y, text):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_game_floor():
    # Draw lanes
    glBegin(GL_QUADS)
    for i in range(-1, 2):
        if i == car_lane:
            glColor3f(0.8, 0.8, 0.8)
        else:
            glColor3f(0.6, 0.6, 0.6)
        glVertex3f(LANES[i+1] - LANE_WIDTH/2, -10000, 0)
        glVertex3f(LANES[i+1] + LANE_WIDTH/2, -10000, 0)
        glVertex3f(LANES[i+1] + LANE_WIDTH/2, 10000, 0)
        glVertex3f(LANES[i+1] - LANE_WIDTH/2, 10000, 0)
    glEnd()

def draw_car():
    glPushMatrix()
    glTranslatef(LANES[car_lane], car_y, car_z)
    glColor3f(0.8, 0.2, 0.2)
    glScalef(car_width, car_length, 40)
    glutSolidCube(1)
    glPopMatrix()

def draw_obstacle(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.2, 0.2, 0.8)
    glScalef(OBSTACLE_SIZE, OBSTACLE_SIZE, OBSTACLE_SIZE)
    glutSolidCube(1)
    glPopMatrix()

def spawn_obstacle():
    lane = random.randint(0, 2)
    x = LANES[lane]
    y = car_y + OBSTACLE_SPAWN_DIST
    z = OBSTACLE_SIZE / 2
    obstacles.append([x, y, z, lane])

def update_obstacles():
    global obstacles, game_over, score
    for obs in obstacles:
        obs[1] -= OBSTACLE_SPEED
    # Remove obstacles that passed the car
    obstacles[:] = [obs for obs in obstacles if obs[1] > car_y - 400]
    # Collision detection
    for obs in obstacles:
        if obs[3] == car_lane and abs(obs[1] - car_y) < (OBSTACLE_SIZE/2 + car_length/2):
            game_over = True
    # Score update: count obstacles passed
    for obs in obstacles:
        if not hasattr(obs, 'scored') and obs[1] < car_y:
            score += 1
            obs.append('scored')

def reset_game():
    global game_over, score, car_lane, obstacles
    game_over = False
    score = 0
    car_lane = 1
    obstacles.clear()

frame_count = 0
def idle():
    global frame_count
    if not game_over:
        update_obstacles()
        if frame_count % OBSTACLE_SPAWN_INTERVAL == 0:
            spawn_obstacle()
        frame_count += 1
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WIN_W, WIN_H)
    setupCamera()
    draw_game_floor()
    draw_car()
    for obs in obstacles:
        draw_obstacle(obs[0], obs[1], obs[2])
    draw_text(10, WIN_H - 50, f"Score: {score}")
    if game_over:
        draw_text(WIN_W//2 - 100, WIN_H//2, "GAME OVER! Press R to restart")
    glutSwapBuffers()

def keyboardListener(key, x, y):
    global car_lane
    if game_over:
        if key == b'r':
            reset_game()
        return
    if key == b'a' and car_lane > 0:
        car_lane -= 1
    elif key == b'd' and car_lane < 2:
        car_lane += 1
    elif key == b'r':
        reset_game()

def specialKeyListener(key, x, y):
    pass  # Not used

def mouseListener(button, state, x, y):
    pass  # Not used

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b"3D Endless Racing Game")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMainLoop()

if __name__ == '__main__':
    main()

