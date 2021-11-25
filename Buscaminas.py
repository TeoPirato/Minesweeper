from pygame.locals import *
import sys, pygame, random, math, numpy

def Lerp(start, end, t):
  return (1 - t) * start + t * end

def OutOfGridBounds(x, y):
    return x < 0 or x >= gridWidth or y < 0 or y >= gridHeight

def ScreenToGrid(screenPosition):
    return (screenPosition[0] // nodeSize, screenPosition[1] // nodeSize)

def GridToScreen(gridPosition):
    return ((gridPosition[0] + .5) * nodeSize, gridRect.y + (gridPosition[1] + .5) * nodeSize)

def RandomBool(percentage):
    return random.randint(1, 100) <= percentage

def WaitSeconds(seconds):
    miliseconds = seconds * 1000    
    msTimer = 0
    while msTimer < miliseconds:
        EventHandling()
        deltaTime = clock.tick(60)
        msTimer += deltaTime

def WaitForClick():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: 
                return

def Reset():
    global clicks
    clicks = 0

    for y in range(gridHeight):
        for x in range(gridWidth):
            grid[x][y].reset(RandomBool(porcentageOfBombs))
    
    for y in range(gridHeight):
        for x in range(gridWidth):
            grid[x][y].setupNumberOfBombs()
                

playing = True
def GameOver():
    global playing
    playing = False
    
    RevealTilesAnimation()
    
    StartFadeInText("You Lost...")
    WaitForClick()
    
    Reset()
    playing = True

def Win():
    global playing
    playing = False
    
    RevealTilesAnimation()

    StartFadeInText("You Won!") 
    WaitForClick() 
    
    Reset()
    playing = True

def WinCondition():
    for y in range(gridHeight):
        for x in range(gridWidth):
            tile = grid[x][y]
            if not tile.visited and not tile.bomb:
                return False
    
    return True 

def StartFadeInText(text):
    global fadeInTime
    fadeInTime = fadeInTotalTime

    while True:
        deltaTime = PerFrameProcedures()
        if not FadeInText(deltaTime, text): break

def RevealTilesAnimation():
    
    for y in range(gridHeight):
        for x in range(gridWidth):
            if not grid[x][y].visited: 
                if grid[x][y].bomb:
                    grid[x][y].visited = True
                    PerFrameProcedures()

    for y in range(gridHeight):
        for x in range(gridWidth):
            if not grid[x][y].visited: 
                grid[x][y].visited = True
    
    PerFrameProcedures()
    
def FadeInText(deltaTime, text):
    global fadeInTime
    fadeInTime -= deltaTime

    alpha = 1 - (fadeInTime / fadeInTotalTime)
    if alpha <= 1:
        a = int(alpha * 255)
        invertedA = 255 - a
        DrawText(text, (255, 255, 255, a), (invertedA, invertedA, invertedA, a), gridRect.center)
        return True
    else: 
        return False
    
                
def PerFrameProcedures():     
    EventHandling()
    pygame.display.update()
    deltaTime = clock.tick(60)
    DrawGrid()
    return deltaTime

def ShiftGrid(x, y, objectiveX, objectiveY):
    global grid
    grid = numpy.roll(grid, (x, y), axis= (0, 1))

    for y in range(gridHeight):
        for x in range(gridWidth):
            current = grid[x][y]
            current.x = x
            current.y = y
            current.setupVecinos()  

def GetStartingEmptySpace():
    maxEmptyTile = None
    maxEmpty = 0

    for y in range(gridHeight):
        for x in range(gridWidth):
            current = grid[x][y]
            if current.bombasVecinas == 0:
                currentEmptys = current.emptyVecinos()
                if currentEmptys > maxEmpty:
                    maxEmpty = currentEmptys
                    maxEmptyTile = current
    
    return maxEmptyTile

def ShiftToStartingSpot(currentTile):

    startingTile = GetStartingEmptySpace()
    
    if startingTile is None: 
        startingTile = currentTile

    x = currentTile.x - startingTile.x
    y = currentTile.y - startingTile.y

    ShiftGrid(x, y, startingTile.x, startingTile.y)


clicks = 0
middleButton = False
def EventHandling():    
    global clicks, middleButton
    mouse = pygame.mouse.get_pos()

    gridPos = ScreenToGrid(mouse)
    tileInMousePos = grid[gridPos[0]][gridPos[1]]

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and playing:

            if event.button == 1 and not tileInMousePos.flag: 
                if clicks == 0:

                    ShiftToStartingSpot(tileInMousePos)

                    gridPos = ScreenToGrid(mouse)
                    tileInMousePos = grid[gridPos[0]][gridPos[1]]   
                else:
                    tileInMousePos.visited = True
                
                if tileInMousePos.bomb:
                    GameOver()
                    return
                elif tileInMousePos.bombasVecinas == 0:                    
                    tileInMousePos.visitVecinos()                            

                clicks += 1

            if event.button == 2:
                middleButton = True

            if WinCondition():
                Win()
                return

            if event.button == 3 and not tileInMousePos.visited:
                tileInMousePos.flag = not tileInMousePos.flag
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                middleButton = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                Reset()
        
    if playing:
        for y in range(gridHeight):
            for x in range(gridWidth):
                grid[x][y].highlight = False
        if middleButton:
            if tileInMousePos.flagVecinas() == tileInMousePos.bombasVecinas and tileInMousePos.visited:
                tileInMousePos.revealNotFlags()
            else:
                tileInMousePos.highlightVecinos()

class Node():
    def __init__(self, pos, bomb):
        self.x = pos[0]
        self.y = pos[1]     
        self.reset(bomb)   
    
    def reset(self, bomb):
        self.bomb = bomb
        self.visited = False
        self.flag = False
        self.highlight = False
    
    def setupVecinos(self):
        self.vecinos = []
        m = (-1, 0, 1)
        for x in m:
            for y in m:
                if (x, y) == (0, 0): continue
                i = self.x + x
                j = self.y + y
                if not OutOfGridBounds(i, j):
                    self.vecinos.append(grid[i][j])
        
        self.setupNumberOfBombs()
            
    def emptyVecinos(self):
        emptyVecinos = 0

        for vecino in self.vecinos:
            if vecino.bombasVecinas == 0:
                emptyVecinos += 1
        
        return emptyVecinos

    def setupNumberOfBombs(self):
        self.bombasVecinas = 0
        if not self.bomb:
            for vecino in self.vecinos:
                self.bombasVecinas += int(vecino.bomb)
    
    def visitVecinos(self):
        for vecino in self.vecinos:
            if not vecino.visited and not vecino.bomb:
                vecino.visited = True
                if vecino.bombasVecinas == 0:
                    vecino.visitVecinos()
    
    def flagVecinas(self):
        flagVecinas = 0
        for vecino in self.vecinos:
            flagVecinas += int(vecino.flag)
        
        return flagVecinas
    
    def revealNotFlags(self): 
        lost = False  
        if self.visited:
            for vecino in self.vecinos:
                if not vecino.flag:
                    vecino.visited = True
                    if vecino.bomb:
                        lost = True
                    elif vecino.bombasVecinas == 0:
                        vecino.visitVecinos()                    
        
        if lost: GameOver()

    def highlightVecinos(self):
        if not self.visited: self.highlight = True

        for vecino in self.vecinos:
            if not vecino.visited and not vecino.flag:
                vecino.highlight = True

def DrawGrid():
    pygame.draw.rect(screen, gridBackgroundColor, gridRect)

    for y in range(gridHeight):
        for x in range(gridWidth):
            current = grid[x][y]
            currentScreenPos = GridToScreen((x, y))

            rect = pygame.Rect(x * nodeSize, gridRect.y + y * nodeSize, nodeSize, nodeSize)
            pygame.draw.rect(screen, gridLinesColor, rect, 1)
            
            if current.visited:
                DrawEmptyTile(rect)
                if current.bomb: 
                    DrawBomb(currentScreenPos)
                elif current.bombasVecinas > 0: 
                    DrawNumber(current.bombasVecinas, currentScreenPos)
            if current.flag:
                DrawFlag(currentScreenPos)
            
            if current.highlight:
                s = pygame.Surface((rect.width - 2, rect.height - 2), pygame.SRCALPHA) 
                s.fill((255,255,255,85))   
                screen.blit(s, (rect.x + 1, rect.y + 1))

def DrawEmptyTile(rect):
    rect.width -= 2
    rect.height -= 2
    rect.centerx += 1
    rect.centery += 1
    pygame.draw.rect(screen, gridEmptyTileColor, rect, 0)

def DrawFlag(currentScreenPos):
    poleWidth = nodeSize / 8
    poleHeight = nodeSize - 2 * poleWidth

    poleX = currentScreenPos[0] - poleWidth / 2
    poleY = currentScreenPos[1] - poleHeight / 2
    poleRect = Rect(poleX, poleY, poleWidth, poleHeight)    

    flagTop = [poleX, poleY]
    flagBottom = [poleX, currentScreenPos[1]]
    flagTip = [currentScreenPos[0] - nodeSize * 0.4 , currentScreenPos[1] - poleHeight / 4]
    flagPoints = (flagTop, flagBottom, flagTip)

    pygame.draw.rect(screen, poleColor, poleRect, 0)
    pygame.draw.polygon(screen, flagColor, flagPoints, 0)

def DrawBomb(currentScreenPos):
    points = []
    for i in range(numberOfSpikes):
        points.append((math.cos(i * rotationAngle) * outerRadius + currentScreenPos[0],
                       math.sin(i * rotationAngle) * outerRadius + currentScreenPos[1]))
        points.append((math.cos(i * rotationAngle + halfRotationAngle) * innerRadius + currentScreenPos[0],
                       math.sin(i * rotationAngle + halfRotationAngle) * innerRadius + currentScreenPos[1]))
    
    pygame.draw.polygon(screen, bombColor, points, 0)

def DrawNumber(bombasVecinas, currentScreenPos):  
    s = 78  
    v = 92

    textColor = Color(0, 0, 0, 255)
    textColor.hsva = (Lerp(0, 360, (bombasVecinas - 1) / 7), s, v, 100)

    DrawText(str(bombasVecinas), textColor, (0, 0, 0, 255), currentScreenPos)

def DrawText(text, textColor, outlineColor, currentScreenPos):  
    textObject = textFont.render(text, True, textColor)
    textObject.set_alpha(textColor[3])
    textRect = textObject.get_rect()

    DrawTextOutline(currentScreenPos, text, outlineColor)

    screen.blit(textObject, (currentScreenPos[0] - textRect.width / 2, currentScreenPos[1] - textRect.height / 2)) 

def DrawTextOutline(currentScreenPos, text, outlineColor):
    outlineObject = textFont.render(text, True, outlineColor)
    outlineObject.set_alpha(outlineColor[3])
    outlineRect = outlineObject.get_rect()

    x = currentScreenPos[0] - outlineRect.width / 2
    y = currentScreenPos[1] - outlineRect.height / 2

    m = (-1, 0, 1)
    for i in m:
        for j in m:
            if (i, j) == (0, 0): continue
            screen.blit(outlineObject, (x + outlineOffset * i, y + outlineOffset * j))

def SetupColors():
    global gridBackgroundColor, gridEmptyTileColor, gridLinesColor, bombColor, poleColor, flagColor
    image = pygame.image.load('color_palette.bmp').convert()    
    
    gridBackgroundColor = image.get_at((0, 0))
    gridEmptyTileColor = image.get_at((1, 0))
    gridLinesColor = image.get_at((2, 0))
    
    flagColor = image.get_at((3, 0))
    poleColor = image.get_at((4, 0))
    bombColor = image.get_at((5, 0))

if __name__ == "__main__":
    
    pygame.init()
    clock = pygame.time.Clock()

    nodeSize = 70
    gridSize = gridWidth, gridHeight = 19, 10
    size = width, height = gridWidth * nodeSize, gridHeight * nodeSize
    gridRect = Rect(0, 0, width, height)

    screen = pygame.display.set_mode(size)
    SetupColors()
    
    porcentageOfBombs = 15
    
    grid = [[Node((x, y), RandomBool(porcentageOfBombs)) for y in range(gridHeight)] for x in range(gridWidth)]   

    for y in range(gridHeight):
        for x in range(gridWidth):
            grid[x][y].setupVecinos() 

    # text drawing
    textFont = pygame.font.SysFont('myriadprosemibolditopentype', nodeSize)
    outlineOffset = 1
    
    # bomb drawing
    outerRadius = nodeSize / 2.75
    innerRadius = outerRadius * 0.65
    numberOfSpikes = 8
    rotationAngle = math.pi * 2 / numberOfSpikes
    halfRotationAngle = math.pi * 1 / numberOfSpikes    

    # fade in text animation    
    fadeInTime = 0
    fadeInTotalTime = 600

    while True:                   
        PerFrameProcedures()