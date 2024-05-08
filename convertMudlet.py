#!/usr/bin/python

import json
import sys

def writeRoom(f, room):
    f.write(f'\n') 

    f.write(f'R ')
    for k,v in room.items():
        if k == 'exits':
            continue

        f.write(f'{{{v}}}') 
    f.write(f'\n') 

    for _,ext in room['exits'].items():
        f.write(f'E ')
        for _,v in ext.items():
            f.write(f'{{{v}}}') 
        f.write(f'\n') 

with open('map.json') as mapfile:
    parsed = json.load(mapfile)

nextRoomNum = 0
voidRoomStart = 0
allrooms = {}
for area in parsed['areas']:
    for room in area['rooms']:
        rid = room['id']

        if rid > nextRoomNum: nextRoomNum = rid

        if rid in allrooms: 
            print("Found Duplicate Room Num")
            sys.exit()

        allrooms[rid] = {'coords':room['coordinates'], 'areaid':area['id']} 


voidRoomStart = nextRoomNum
print(f'VoidStart {voidRoomStart}')

crowdcolors = parsed['customEnvColors']
colormapping = parsed['envToColorMapping']

globalRoomCnt = parsed['roomCount']
voidRoomOffset = 0

dirs = {
    "north": "n",
    "northeast": "ne",
    "east": "e",
    "southeast": "se",
    "south": "s",
    "southwest": "sw",
    "west": "w",
    "northwest": "nw",

    "in": "in",
    "out": "out",

    "up": "u",
    "down": "d",
}

#define MAP_EXIT_
dirBits = {
    'n':1,
    'e':2,
    's':4,
    'w':8,
    'u':16,
    'd':32,
    'in':64,
    'out':128,
}

# d is expected to be a 'rdircmd', which is room direction
def reverseDir(d):

    if d == 'n': return (4,'s')
    if d == 's': return (1,'n')
    if d == 'e': return (8,'w')
    if d == 'w': return (2,'e')

    if d == 'nw': return (4|2,'se')
    if d == 'ne': return (4|8,'sw')
    if d == 'sw': return (1|2,'ne')
    if d == 'se': return (1|8,'nw')

    if d == 'in':  return (128,'out')
    if d == 'out': return (64,'in')

    if d == 'u': return (32,'d')
    if d == 'd': return (16,'u')

def colors(mapping):
    if mapping not in colormapping:

        return '<Fffffff>'

    cid = colormapping[mapping]

    bit24 = [255,0,0]
    for color in crowdcolors:
        if color['id'] == cid:
            bit24 = color["color24RGB"]
            break;

    hex1 = hex(bit24[0])[2:]
    hex2 = hex(bit24[1])[2:]
    hex3 = hex(bit24[2])[2:]
    color = "<F"
    color += hex1.zfill(2)
    color += hex2.zfill(2)
    color += hex3.zfill(2)
    color += ">"
    return color

def getRoom(areaId,roomId):
    pass

def getArea(roomId):
    if roomId > voidRoomStart: return -1

    for area in parsed['areas']:
        for room in area['rooms']:
            if roomId == room['id']:
                return area['id']

def getExit(roomId,exitId):
    for area in parsed['areas']:
        for room in area['rooms']:
            if roomId == room['id']:
                for ext in room['exits']:
                    if exitId == ext['exitId']: 
                        return ext;
    #  print(f'room FOUND NOTHING {roomId}, {exitId}')
    return {}

convertedRooms = {}
allshops = {}
with open('world.map', 'w') as f:

    # prepand the header junk
    with open('mapheader') as header:
        for line in header:
            f.write(line)

    areaCount = 0
    for areaIdx,area in enumerate(parsed['areas']):
        areaname = area['name']
        roomCnt =  area['roomCount']
        if roomCnt == 0: continue
        
        areaid = area['id']
        if areaid < 0: continue

        #  print(f'Converting area {areaid}')
        #  print(f'RoomCnt {roomCnt}')

        for roomIdx, room in enumerate(area['rooms']):
            rid = room['id']

            rname = ''
            if 'name' in room: 
                rname = room['name']

            rid = room['id']
            feature = '';gameArea = ''
            if 'userData' in room:
                user = room['userData']

                if 'Game Area' in user: gameArea = user['Game Area']
                if 'feature-stronghold' in user: feature = 'h'
                if 'feature-ferry' in user: feature = 'F'
                if 'feature-news' in user: feature = 'N'
                if 'feature-arena' in user: feature = 'A'
                if 'feature-postoffice' in user: feature = 'O'
                if 'feature-commodityshop' in user: feature = 'C'
                if 'feature-grate' in user: feature = 'G'
                if 'feature-wilderness' in user: feature = 'W'
                if 'feature-harbour' in user: feature = 'H'
                if 'feature-shop' in user: feature = 'S'
                if 'feature-bank' in user: feature = '$'
                if 'feature-locksmith' in user: feature = 'L'

            envi = room['environment']
            color = colors(str(envi))

            coords = room["coordinates"]

            croom = {
                'vnum':rid,
                'flags':0, # hide all room, with 4102, ROOM_FLAG_HIDE
                'color':color,
                'name':rname,
                'sym':feature,
                'desc':gameArea,
                'area':areaname,
                'note':'',
                'terain':'',
                'data':coords,
                'weight':1.00,
                'roomid':areaid,
                'exits':{},
            }
            convertedRooms[rid] = croom

            if feature == 'S':
                if areaid not in allshops:
                    allshops[areaid] = {}

                allshops[areaid][rname] = rid

            for exitIdx, portal in enumerate(room['exits']):
                exitid = portal['exitId']

                # check if this leads to the same area id
                direction = portal['name']

                if portal['name'] not in dirs:
                    #  print(f'Weird portal: {portal["name"]}')
                    direction = 'special'
                    cmd = 0
                    continue
                    #  sys.exit(1)
                else:
                    #TODO need to account for 
                    #   sendAll, send
                    #   script
                    #   push, pull, turn .*here
                    #       figure, idol, jar, vine, carving, callibius, opal, horn
                    #   embrace
                    #   enter
                    #   kneel
                    #   "say .*"
                    rdir = dirs[direction]
                    rdircmd = dirs[direction]

                simplelist = ['n','s','e','w','u','d','in','out']
                orlist = ['nw','ne','se','sw']
                dirbit = 0
                if rdircmd in simplelist: dirbit = dirBits[rdircmd]
                if rdircmd in orlist: dirbit = dirBits[rdircmd[0]] | dirBits[rdircmd[1]]

                if rdir != rdircmd: 
                    color = '<118>'
                    croom['color'] = color

                crexit = {
                    'vnum':exitid,
                    'dir': rdir,
                    'dircmd':rdircmd,
                    'dirbit':dirbit,
                    'flag':'',
                    'data':'',
                    'weight':1.00,
                    'color':'',
                    'delay':0.0,
                }
                croom['exits'][exitid] = crexit
                # done with the current exit.
            
            # done with current room, writ it out.

        # done with the current area
        areaCount += 1
        if False and areaCount > 2:
            break

    # End of loop for areas
    print(f'Done collection rooms')
    for roomid,room in convertedRooms.items():
        if roomid > voidRoomStart: continue

        voidRooms = {}
        for destid, rdest in room['exits'].items():
            if rdest['vnum'] > voidRoomStart: 
                continue

            # temporary
            if destid not in convertedRooms: continue

            exitroom = convertedRooms[destid]

            # in the dict roomid is really AreaID
            # and if they are in different areas, don't bother with void rooms.
            if room['roomid'] != exitroom['roomid']: 
                rdest['dirbit'] = dirBits['in']
                continue

            # some are one way?
            if roomid not in exitroom['exits']: continue
            exitBackToCRoom = exitroom['exits'][roomid]

            # Coords are stored in Data
            ccoords = room['data']
            ecoords = exitroom['data']

            #skip rooms that won't need void rooms
            # TODO add special exits here
            voidList = ['u','d','in','out']
            if rdest['dir'] in voidList: continue

            # Get the deltas
            dx = abs(ccoords[0] - ecoords[0])
            dy = abs(ccoords[1] - ecoords[1])

            # New void rooms to be inserted between this room and the exit.
            #   if more then one is created, each new one will be connected
            #   to this room and push the exit further away
            nextRoom = destid # start off pointing to the original exit

            # getting ready to create a void room.
            while dx > 1 or dy > 1:
                if dx > 0: dx = dx - 1;
                if dx < 0: dx = dx + 1;
                if dy > 0: dy = dy - 1;
                if dy < 0: dy = dy + 1;

                nextRoomNum += 1
                vid = nextRoomNum 

                voidroom = {
                    'vnum':vid,
                    'flags':4104, # void room flag
                    'color':'',
                    'name':'',
                    'sym':'',
                    'desc':'',
                    'area':'',
                    'note':'',
                    'terain':'',
                    'data':'',
                    'weight':0.01,
                    'roomid':'',
                    'exits':{},
                }
                voidRooms[vid] = voidroom

                # exit going back to the current room
                vexit = {
                    'vnum':roomid,
                    'dir': exitBackToCRoom['dir'],
                    'dircmd': exitBackToCRoom['dir'],
                    'dirbit': exitBackToCRoom['dirbit'],
                    'flag':'',
                    'data':'',
                    'weight':0.01,
                    'color':'',
                    'delay':0.0,
                }
                voidroom['exits'][roomid] = vexit
                # point this room to the new void room.
                rdest['vnum'] = vid

                # exit continuing through to the original exit
                vexit = {
                    'vnum': nextRoom,
                    'dir': rdest['dir'],
                    'dircmd': rdest['dir'],
                    'dirbit': rdest['dirbit'],
                    'flag':'',
                    'data':'',
                    'weight':0.01,
                    'color':'',
                    'delay':0.0,
                }
                voidroom['exits'][nextRoom] = vexit

                # have the original exit link to the first void room.
                if nextRoom == destid:
                    exitBackToCRoom['vnum'] = vid
                # update the previous void room how to exit to this one
                else:
                    voidRooms[nextRoom]['exits'][roomid]['vnum'] = vid

                # for the next iteration, tell the upcoming void room how to enter the one that was just finished.
                nextRoom = vid
                # done with potential extra rooms

        # done generating void rooms for the current room.
        writeRoom(f, room)
        for _,vr in voidRooms.items():
            writeRoom(f, vr)

    print(f'Total rooms b4 {globalRoomCnt}, after {globalRoomCnt + len(voidRooms)}, void index {nextRoomNum}')

# #foreach {*shops[49][%*]} shop {#if {{^Golden Dragon's Lair$} == {^$shop$}} {#show found}}
with open('shopRoomNumbers.tt', 'w') as f:
    f.write(f"#var allshops {{\n")
    for areaid,rooms in allshops.items():
        f.write(f"\t{{{areaid}}} {{\n")
        for rname,rid in rooms.items():
            f.write(f"\t\t{{{rname}}} {{{rid}}}\n")
        f.write(f"\t}}\n")
    f.write(f"}}\n")


