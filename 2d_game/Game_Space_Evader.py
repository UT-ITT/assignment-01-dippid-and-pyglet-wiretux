import pyglet
import random
from DIPPID import SensorUDP

PORT = 5700
sensor = SensorUDP(PORT)

window = pyglet.window.Window(width=1024, height=900, caption="Space Evader")

border = 10
timeSinceLastSpawn = 0
timeSinceLastLevelup = 0
level = 1

# menu states
gameover = False
started = False

# Load Images
bgImg = pyglet.image.load('bg.png')
playerImg = pyglet.image.load('player.png')
enemyImg = pyglet.image.load('enemy.png')
enemy2Img = pyglet.image.load('meteor.png')
enemy3Img = pyglet.image.load('meteorGrey.png')

# Create Sprites
bgSprite1 = pyglet.sprite.Sprite(img=bgImg, x=0, y=0)
bgSprite2 = pyglet.sprite.Sprite(img=bgImg, x=0, y=bgImg.height)
playerSprite = pyglet.sprite.Sprite(img=playerImg, x=window.width / 2 , y=window.height/2)

# Label for current Level in a game
levelLabel = pyglet.text.Label('Level: 0',
                          font_name='Times New Roman',
                          font_size=24,
                          x=window.width//2, y= window.height - 50,
                          anchor_x='center', anchor_y='top')
# Labels for Start screen
startScreenTitleLabel = pyglet.text.Label('Space Evader',
                          font_name='Times New Roman',
                          font_size=48,
                          x=window.width//2, y=window.height//2+50,
                          anchor_x='center', anchor_y='center')

startScreenStartLabel = pyglet.text.Label('Press Button 1 on the phone to start',
                          font_name='Times New Roman',
                          font_size=24,
                          x=window.width//2, y=window.height//2 - 150,
                          anchor_x='center', anchor_y='center')

startScreenDescriptionLabel = pyglet.text.Label('Move your spaceship by tilting your phone and evade the objects',
                          font_name='Times New Roman',
                          font_size=24,
                          x=window.width//2, y=window.height//2 - 50,
                          anchor_x='center', anchor_y='center')
# Labels for Restart screen
gameOverLabel = pyglet.text.Label('Game Over',
                          font_name='Times New Roman',
                          font_size=48,
                          x=window.width//2, y=window.height//2+50,
                          anchor_x='center', anchor_y='center')
gameOverlevelLabel = pyglet.text.Label('',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2 - 50,
                          anchor_x='center', anchor_y='center')
restartLabel = pyglet.text.Label('Press Button 1 to Restart',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2 - 120,
                          anchor_x='center', anchor_y='center')

# Dimlayer shape for menus
dimmLayer = pyglet.shapes.Rectangle(x = 0, y = 0, width = window.width, height = window.height, color=(0, 0, 0))
dimmLayer.opacity = 180

enemies = []

# Spawns a new enemy
def spawnEnemy():
    global border

    enemyKinds = [enemyImg, enemy2Img, enemy3Img]

    # We only spawn at top, left, right to make the game easier
    side = random.randint(0,2)

    enemyKind = random.choice(enemyKinds)

    # The random direction component is precalculated and has a small bias towards 0
    randomDirection = random.choice([-1,1]) * random.uniform(0,1) ** 2

    match side:
        case 0:
            spawnX = random.randint(border,window.width - border - enemyKind.width)
            spawnY = window.height
            vx, vy = randomDirection, -1
        case 1:
            spawnX = -enemyKind.width
            spawnY = random.randint(border, window.height - border - enemyKind.height)
            vx, vy = 1, randomDirection
        case 2:
            spawnX = window.width
            spawnY = random.randint(border, window.height - border - enemyKind.height)
            vx, vy = -1, randomDirection

    enemySprite = pyglet.sprite.Sprite(img=enemyKind, x=spawnX, y=spawnY)
    
    # normalize velocity
    length = (vx**2 + vy**2) ** 0.5
    vx = vx / length
    vy = vy / length

    enemySprite.vx = vx
    enemySprite.vy = vy

    enemies.append(enemySprite)

# Scrolls the background
def backgroundScrolling(speed, delta):
    bgSprite1.y -= speed * delta
    bgSprite2.y -= speed * delta

    # Move the bg sprite up if it is out of the window
    if bgSprite1.y <= -bgImg.height:
        bgSprite1.y = bgSprite2.y + bgImg.height
    elif bgSprite2.y <= -bgImg.height:
        bgSprite2.y = bgSprite1.y + bgImg.height

# Adds Gyro Controlls to the player
def playerController(delta, playerSpeed):
    accelerometerValueX = 0
    accelerometerValueY = 0

    #Get Sensor Value
    if(sensor.has_capability('accelerometer')):
        accelerometerValueX = sensor.get_value('accelerometer')['x']
        accelerometerValueY = sensor.get_value('accelerometer')['y']

    # Apply Deadzones
    deadzone = 0.07
    if abs(accelerometerValueX) < deadzone:
        accelerometerValueX = 0

    if abs(accelerometerValueY) < deadzone:
        accelerometerValueY = 0

    # Apply movement
    playerSprite.x += delta * playerSpeed * accelerometerValueX * -1
    playerSprite.y += delta * playerSpeed * accelerometerValueY * -1

    # Keep Player inside the game area
    global border
    if playerSprite.x < border:
        playerSprite.x = border
    elif playerSprite.x > window.width - border - playerSprite.width:
        playerSprite.x = window.width - border - playerSprite.width

    if playerSprite.y < border:
        playerSprite.y = border
    elif playerSprite.y > window.height - border - playerSprite.height:
        playerSprite.y = window.height - border - playerSprite.height

# Moves all enemies
def moveEnemy(enemySpeed, delta):
    global enemies
    for enemy in enemies[:]:
        enemy.x += enemy.vx * enemySpeed * delta
        enemy.y += enemy.vy * enemySpeed * delta

        if (enemy.y <= -enemyImg.height or
            enemy.x <= -enemy.width or
            enemy.x >= window.width + enemy.width
            ):
            enemies.remove(enemy)

# Checks if the player colides with an object
def collisionCheck():
    global enemies, gameover
    for enemy in enemies:
        offsetx = 5
        offsety = 5

        playerLeft = playerSprite.x + offsetx
        playerRight = playerSprite.x + playerSprite.width - offsetx
        playerBottom = playerSprite.y + offsety
        playerTop = playerSprite.y + playerSprite.height - offsety

        enemyLeft = enemy.x + offsetx
        enemyRight = enemy.x + enemy.width - offsetx
        enemyBottom = enemy.y + offsety
        enemyTop = enemy.y + enemy.height - offsety

        # Lose Condition
        if (playerLeft < enemyRight
        and playerRight > enemyLeft
        and playerBottom < enemyTop
        and playerTop > enemyBottom):
            gameOverlevelLabel.text = f"You made it until level {level}"
            gameover = True

# Resets the most important game values to start a new game
def resetGame():
    global timeSinceLastSpawn, timeSinceLastLevelup, level
    level = 1
    timeSinceLastSpawn = 0
    timeSinceLastLevelup = 0
    enemies.clear()
    playerSprite.x = window.width / 2
    playerSprite.y = window.height / 2

# Handels the button press in the menus
def handle_button_press(data):
    global gameover, started
    if int(data) == 1 and (gameover or not started):
        resetGame()
        gameover = False
        started = True

sensor.register_callback('button_1', handle_button_press)

# Main update Loop to process changes
def update(delta):
    global minBorder, maxBorder, timeSinceLastSpawn, timeSinceLastLevelup, level, gameover, started

    backgroundScrollingSpeed = 300

    # no updates beside the par in a gameover state or when the game has not started
    if gameover or not started:
        backgroundScrolling(backgroundScrollingSpeed, delta)
        return

    levelLabel.text = f"Level: {level}"
    min_speed = 0.4
    spawnTime = 5
    playerSpeed = 1500
    enemyBaseSpeed = 500
    maxBackgroundScrollingSpeed = 1500

    playerController(delta, playerSpeed)

    # Dificulty Increase
    timeSinceLastLevelup += delta
    if timeSinceLastLevelup > 15 * 0.95 ** level:
        timeSinceLastLevelup = 0
        level += 1

    #Enemy spawn logic
    timeSinceLastSpawn += delta
    currenteSpawnTime = spawnTime * (0.7 ** (level - 1))
    if timeSinceLastSpawn > currenteSpawnTime:
        timeSinceLastSpawn = 0
        spawnEnemy()

    # Enemy movement logic
    speedLevel = random.uniform(1,1.3)
    moveEnemy(enemyBaseSpeed * speedLevel, delta)

    # Background Scolling gets faster every 3 levels
    currentBackgroundScrollingSpeed = backgroundScrollingSpeed + (150 * (level // 3))
    if(currentBackgroundScrollingSpeed > maxBackgroundScrollingSpeed):
        currentBackgroundScrollingSpeed = backgroundScrollingSpeed
    backgroundScrolling(currentBackgroundScrollingSpeed, delta)

    # Collision check
    collisionCheck()

pyglet.clock.schedule_interval(update, 1/60.)

@window.event
def on_draw():
    window.clear()
    bgSprite1.draw()
    bgSprite2.draw()
    if started:
        playerSprite.draw()
        for enemy in enemies:
            enemy.draw()
        levelLabel.draw()
    else:
        dimmLayer.draw()
        startScreenTitleLabel.draw()
        startScreenStartLabel.draw()
        startScreenDescriptionLabel.draw()

    if gameover:
        dimmLayer.draw()
        gameOverLabel.draw()
        gameOverlevelLabel.draw()
        restartLabel.draw()

pyglet.app.run()
