from random import randrange
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from numpy import floor
from numpy import abs
import time
from perlin_noise import PerlinNoise
from nMap import nMap

app = Ursina()
grass = load_texture('grass.png')
monoTex = load_texture('mono_stroke.png')
wireTex = load_texture('Frame.png')
stoneTex = load_texture('grass_mono.png')
CreeperModel = 'assets/creeper.obj'
creeper = 'assets/creeper.png'


window.color = color.rgb(0, 121, 211)
window.exit_button.visible = False

bte = Entity(model='cube', texture=wireTex)
class BTYPE:
    STONE = color.rgb(255, 255, 255)
    GRASS = color.rgb(0, 255, 0)
    SOIL = color.rgb(255, 80, 100)
    RUBY = color.rgb(255, 0, 0)

BlockType = BTYPE.STONE
buildMode = -1

def buildTool():
    global BlockType
    if buildMode == -1:
        bte.visible = False
        return
    else:
        bte.visible = True
    bte.position = round(player.position + camera.forward * 3)
    bte.y += 2
    bte.y = round(bte.y)
    bte.x = round(bte.x)
    bte.z = round(bte.z)
    bte.color = BlockType

def build():
    e = duplicate(bte)
    e.collider = 'cube'
    e.texture = stoneTex
    e.color = BlockType
    e.shake(duration=0.5, speed=0.01)


def input(key):
    global BlockType, buildMode
    if key == 'q' or key == 'escape':
        exit()
    if key == 'g':
        generateSubset()

    if key == 'f':
        buildMode *= -1

    if buildMode == 1 and key == 'right mouse up':
        build()
    elif buildMode == 1 and key == 'left mouse up':
        e = mouse.hovered_entity
        destroy(e)
    if key == '1':
        BlockType = BTYPE.SOIL
    if key == '2':
        BlockType = BTYPE.GRASS
    if key == '3':
        BlockType = BTYPE.STONE
    if key == '4':
        BlockType = BTYPE.RUBY

prevTime = time.time()


def update():
    global prevZ, prevX, prevTime, amp, freq, player, buildMode
    if player.y < -amp-1:
        player.y = 2 + floor((noise([player.x/freq, player.z/freq])) * amp)

    if abs(player.z - prevZ) > 1 or \
            abs(player.x - prevX) > 1:
        generateShells()

    if time.time() - prevTime > 0.005:
        time.time()
        generateSubset()

    if player.y == -6:
        player.y = 50

    if buildMode == 1:
        buildTool()

    zombie1.look_at(player, 'forward')
    zombie1.rotation_x = 0

noise = PerlinNoise(octaves=4, seed=99)
amp = 32
freq = 100
terrain = Entity(model=None, collider=None)
terrain_width = 40
subWidth = int(terrain_width / 10)
subsets = []
subCubes = []
sci = 0
currentSubset = 0

for i in range(subWidth):
    bud = Entity(model='cube')
    subCubes.append(bud)

for i in range(int((terrain_width * terrain_width) / subWidth)):
    bud = Entity(model=None)
    bud.parent = terrain
    subsets.append(bud)


def generateSubset():
    global sci, currentSubset, freq, amp
    if currentSubset >= len(subsets):
        finishedTerrain()
        return
    for i in range(subWidth):
        x = subCubes[i].x = floor((i + sci) / terrain_width)
        z = subCubes[i].z = floor((i + sci) % terrain_width)
        y = subCubes[i].y = floor(noise([x / freq, z / freq]) * amp)
        subCubes[i].parent = subsets[currentSubset]

        y += randrange(-4, 4)
        r = 0
        g = 0
        b = 0
        if y > amp*0.3:
            b = 255
        if y == 4:
            r = g = b = 255
        else:
            g = nMap(y, 0, amp * 0.5, 0, 255)
        # Red Zone?
        if z > terrain_width*0.5:
            g = 0
            b = 0
            r = nMap(y, 0, amp, 110, 255)
        subCubes[i].texture = grass
        subCubes[i].color = color.rgb(r, g, b)
        subCubes[i].visible = False

    subsets[currentSubset].combine(auto_destroy=False)
    subsets[currentSubset].texture = monoTex
    sci += subWidth
    currentSubset += 1


terrainFinished = False


def finishedTerrain():
    global terrainFinished
    if terrainFinished:
        return
    terrain.texture = grass
    terrain.combine()
    terrainFinished = True
    # terrain.texture = grass

# for i in range(terrain_width*terrain_width):
#    bud = Entity(model='cube',)
#    bud.x = floor(i / terrain_width)
#    bud.z = floor(i % terrain_width)
#    bud.y = floor(noise([bud.x/freq, bud.z/freq]) * amp)

player = FirstPersonController()
player.x = player.z = 5
player.y = 20
prevZ = player.z
prevX = player.x

shellies = []
shellWidth = 3
for i in range(shellWidth * shellWidth):
    bud = Entity(model='cube', collider='box')
    bud.visible = False
    shellies.append(bud)


def generateShells():
    global shellWidth, amp, freq
    for i in range(len(shellies)):
        x = shellies[i].x = floor((i / shellWidth) +
                                  player.x - 0.5 * shellWidth)
        z = shellies[i].z = floor((i / shellWidth) +
                                  player.z - 0.5 * shellWidth)
        y = shellies[i].y = floor(noise([x / freq, z / freq]) * amp)


scene.fog_color = color.white
scene.fog_density = 0.02

zombie1 = Entity(y=-2, x=21, z=14, scale=0.07, model=CreeperModel, texture=creeper, double_sided=True, )
generateShells()

app.run()
