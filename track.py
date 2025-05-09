from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import random
import time

# Window setup
WIN_W = 1000
WIN_H = 800
FOV = 60

# Game state
difficult = "easy"
paused = False
game_over = False
score = 0
lives = 5
camera_mode = "third"
dash_offset = 0
godmode = False
powerup_active = False
powerup_timer = 0
POWERUP_DURATION = 180  # 3 seconds at 60 FPS
powerup_pos = None  # [x, y, z, lane]
POWERUP_SIZE = 50

# Car (player)
LANE_WIDTH = 200
LANES = [-LANE_WIDTH, 0, LANE_WIDTH]
car_lane = 1
car_y = -300
car_z = 50
car_width = 60
car_length = 100

# Obstacles
obstacles = []
OBSTACLE_SPAWN_DIST = 2000
OBSTACLE_SPEED = 6
OBSTACLE_SIZE = 60
OBSTACLE_SPAWN_INTERVAL = 60

# Camera
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, float(WIN_W) / float(WIN_H), 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_mode == "third":
        eye_x = LANES[car_lane]
        eye_y = car_y - 600
        eye_z = 350
        cen_x = LANES[car_lane]
        cen_y = car_y + 300
        cen_z = 0
        gluLookAt(eye_x, eye_y, eye_z, cen_x, cen_y, cen_z, 0, 0, 1)
    else:
        eye_x = LANES[car_lane]
        eye_y = car_y + 120
        eye_z = car_z + 40
        cen_x = LANES[car_lane]
        cen_y = car_y + 400
        cen_z = car_z + 40
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
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.7, 0.2)
    glVertex3f(-1000, -10000, 0)
    glVertex3f(LANES[0] - LANE_WIDTH/2, -10000, 0)
    glVertex3f(LANES[0] - LANE_WIDTH/2, 10000, 0)
    glVertex3f(-1000, 10000, 0)
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.1, 0.7, 0.2)
    glVertex3f(LANES[2] + LANE_WIDTH/2, -10000, 0)
    glVertex3f(1000, -10000, 0)
    glVertex3f(1000, 10000, 0)
    glVertex3f(LANES[2] + LANE_WIDTH/2, 10000, 0)
    glEnd()

    glBegin(GL_QUADS)
    for i in range(-1, 2):
        glColor3f(0.6, 0.6, 0.6)
        glVertex3f(LANES[i+1] - LANE_WIDTH/2, -10000, 0)
        glVertex3f(LANES[i+1] + LANE_WIDTH/2, -10000, 0)
        glVertex3f(LANES[i+1] + LANE_WIDTH/2, 10000, 0)
        glVertex3f(LANES[i+1] - LANE_WIDTH/2, 10000, 0)
    glEnd()

    glLineWidth(6)
    glColor3f(1, 1, 1)
    dash_length = 100
    gap_length = 80
    min_y = -10000
    max_y = 10000
    global dash_offset

    for i in range(1, len(LANES)):
        x = (LANES[i-1] + LANES[i]) / 2
        y = min_y + (dash_offset % (dash_length + gap_length))
        while y < max_y:
            glBegin(GL_LINES)
            glVertex3f(x, y, 1)
            glVertex3f(x, min(y + dash_length, max_y), 1)
            glEnd()
            y += dash_length + gap_length

    glColor3f(1, 1, 0)
    left_edge_x = LANES[0] - LANE_WIDTH / 2
    right_edge_x = LANES[2] + LANE_WIDTH / 2

    glBegin(GL_LINES)
    glVertex3f(left_edge_x, min_y, 2)
    glVertex3f(left_edge_x, max_y, 2)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(right_edge_x, min_y, 2)
    glVertex3f(right_edge_x, max_y, 2)
    glEnd()

def draw_car():
    glPushMatrix()
    glTranslatef(LANES[car_lane], car_y, car_z)

    glPushMatrix()
    glColor3f(0.8, 0.2, 0.2)
    glScalef(car_width, car_length, 40)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.95, 0.95, 0.95)
    glTranslatef(0, 0, 30)
    glScalef(car_width * 0.6, car_length * 0.5, 20)
    glutSolidCube(1)
    glPopMatrix()

    wheel_offset_x = car_width * 0.4
    wheel_offset_y = car_length * 0.4
    wheel_z = -20
    wheel_size = 20

    glColor3f(0.1, 0.1, 0.1)
    for wx in [-wheel_offset_x, wheel_offset_x]:
        for wy in [-wheel_offset_y, wheel_offset_y]:
            glPushMatrix()
            glTranslatef(wx, wy, wheel_z)
            glScalef(wheel_size, wheel_size, wheel_size)
            glutSolidCube(1)
            glPopMatrix()

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
    global obstacles, game_over, score, lives
    for obs in obstacles:
        obs[1] -= OBSTACLE_SPEED
    obstacles[:] = [obs for obs in obstacles if obs[1] > car_y - 400]

    if not godmode:
        for obs in obstacles:
            if obs[3] == car_lane and abs(obs[1] - car_y) < (OBSTACLE_SIZE/2 + car_length/2):
                obstacles.remove(obs)
                lives -= 1
                if lives <= 0 and not game_over:
                    game_over = True
                    print(f"GAME OVER! Final Score: {score}")
                break

    for obs in obstacles:
        if not hasattr(obs, 'scored') and obs[1] < car_y:
            score += 1
            obs.append('scored')

def set_difficulty(level):
    global OBSTACLE_SPEED, OBSTACLE_SPAWN_INTERVAL
    if level == "easy":
        OBSTACLE_SPEED = 4
        OBSTACLE_SPAWN_INTERVAL = 70
    elif level == "medium":
        OBSTACLE_SPEED = 6
        OBSTACLE_SPAWN_INTERVAL = 60
    elif level == "hard":
        OBSTACLE_SPEED = 9
        OBSTACLE_SPAWN_INTERVAL = 45
    else:
        OBSTACLE_SPEED = 4
        OBSTACLE_SPAWN_INTERVAL = 70

set_difficulty(difficult)

def reset_game():
    global game_over, score, car_lane, obstacles, lives
    game_over = False
    score = 0
    car_lane = 1
    lives = 5
    obstacles.clear()
    print("Game reset.")

frame_count = 0
def idle():
    global frame_count, dash_offset
    if not game_over and not paused:
        update_obstacles()
        if frame_count % OBSTACLE_SPAWN_INTERVAL == 0:
            spawn_obstacle()
        if frame_count % 60 == 0:
            print(f"Score: {score}, Lives: {lives}")
        frame_count += 1
        dash_offset += OBSTACLE_SPEED
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
    draw_text(10, WIN_H - 80, f"Lives: {lives}")
    if powerup_active:
        draw_text(10, WIN_H - 110, "POWER-UP: Invincible & Speed!")
    if godmode:
        draw_text(10, WIN_H - 110, "GODMODE: ON")
    if game_over:
        draw_text(WIN_W//2 - 100, WIN_H//2, "GAME OVER! Press R to restart")
    if paused:
        draw_text(WIN_W//2 - 50, WIN_H//2, "PAUSED")
    glutSwapBuffers()

def keyboardListener(key, x, y):
    global car_lane, camera_mode, godmode, paused, difficult
    if game_over:
        if key == b'r':
            reset_game()
        return
    if key == b'p' or key == b'P':
        paused = not paused
        print("Paused" if paused else "Resumed")
        return
    if key == b'a' and car_lane > 0:
        car_lane -= 1
    elif key == b'd' and car_lane < 2:
        car_lane += 1
    elif key == b'r':
        reset_game()
    elif key == b'c' or key == b'C':
        camera_mode = "first" if camera_mode == "third" else "third"
    elif key == b'v' or key == b'V':
        godmode = not godmode
    if key == b'1':
        difficulty = "easy"
        set_difficulty(difficulty)
        print("Difficulty set to EASY")
        reset_game()
    elif key == b'2':
        difficulty = "medium"
        set_difficulty(difficulty)
        print("Difficulty set to MEDIUM")
        reset_game()
    elif key == b'3':
        difficulty = "hard"
        set_difficulty(difficulty)
        print("Difficulty set to HARD")
        reset_game()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b"3D Endless Racing Game")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutMainLoop()

if __name__ == '__main__':
    main()
