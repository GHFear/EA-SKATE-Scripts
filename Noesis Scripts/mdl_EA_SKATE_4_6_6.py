#Noesis python importer - Skate 1, 2 and 3 .rx2 files - By Beedy and GHFear - Version 4.6.6
from inc_noesis import *
import noesis
import noewin
import socket, ssl
import time
import random
import json
import math
import paho.mqtt.client as mqtt
from noewin import user32, gdi32, kernel32
from inc_noesis import *
from ctypes import *
#rapi methods should only be used during handler callbacks
import rapi
import struct
#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!



#OPTIONS:
#Use point cloud for Sim / Collision Visualization (It's totally broken for now, but let's work on it)
LOAD_POINT_CLOUD = 0      #Available LOAD_POINT_CLOUD options: 0 | 1                   | ( 0 Default )
GAME_SPECIFIC = "SKATE"   #Available GAME_SPECIFIC options: SKATE | FIFA09
USE_MESH_NAMES = 0        #Available USE_MESH_NAMES options: 0 | 1                     | ( 0 Default ) | Export as DAE if using this option and import as DAE in Blender
USE_MATERIAL_NAMES = 0      #Available USE_MATERIAL_NAMES options: 0 | 1                 | ( 0 Default ) | Export as DAE if using this option and import as DAE in Blender

VERSION = "4.6.6"

def registerNoesisTypes():
                #handle = noesis.registerTool("EA Skate", SKATEToolMethod, "Launch the EA RenderWare4 Tool.")
                #noesis.checkToolMenuItem(handle, 1)
                #handle2 = noesis.registerTool("EA Fifa 2009", SKATEToolMethod, "Launch the EA RenderWare4 Tool.")
                #noesis.checkToolMenuItem(handle2, 0)
                #submenu1 = noesis.setToolSubMenuName(handle, "EA RenderWare4 Tool")
                #submenu2 = noesis.setToolSubMenuName(handle2, "EA RenderWare4 Tool")
                
                
                handle = noesis.register("EA Skate (1,2,3) 3D Models (X360) " + VERSION, ".rx2; .dat")
                noesis.setHandlerTypeCheck(handle, CheckModelType)
                noesis.setHandlerLoadModel(handle, noepyLoadModel)

                handle = noesis.register("EA Skate (1,2,3) 3D Sim (X360) " + VERSION, ".rx2; .dat")
                noesis.setHandlerTypeCheck(handle, CheckSimType)
                noesis.setHandlerLoadModel(handle, noepyLoadSim)

                handle = noesis.register("EA Skate (1,2,3) Textures (X360) " + VERSION, ".rx2; .dat")
                noesis.setHandlerTypeCheck(handle, CheckTextureType)
                noesis.setHandlerLoadRGBA(handle, noepyLoadRGBAXbox)

                handle = noesis.register("EA Skate (1,2,3) Textures (PS3) " + VERSION, ".psg; .dat; .rpsgl")
                noesis.setHandlerTypeCheck(handle, CheckTextureTypePS3)
                noesis.setHandlerLoadRGBA(handle, noepyLoadRGBAPS3Multi)
                
                
                noesis.logPopup()
                #print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
                return 1
#check if it's this type based on the data

def CheckSimType(data):
        bs = NoeBitStream(data)
        Magic = bs.readBytes(7)
        bs.seek(0x58, NOESEEK_ABS)
        rx2TypeID = bs.readBytes(4)
        if Magic != b'\x89\x52\x57\x34\x78\x62\x32':
                return 0
            
        if rx2TypeID == b'\x00\x00\x00\x01':
                print("RX2 TYPE: SIM")
                return 1


        return 0

            
def CheckModelType(data):
        bs = NoeBitStream(data)
        Magic = bs.readBytes(7)
        bs.seek(0x58, NOESEEK_ABS)
        rx2TypeID = bs.readBytes(4)
        if Magic != b'\x89\x52\x57\x34\x78\x62\x32':
                return 0
            
        if rx2TypeID == b'\x00\x00\x00\x04':
                print("RX2 TYPE: EA SKATE MESH")
                return 1
        elif rx2TypeID == b'\x00\x00\x08\x00':
                print("RX2 TYPE: EA NHL LEGACY MESH")
                return 1


        return 0

def CheckTextureType(data):
        bs = NoeBitStream(data)
        Magic = bs.readBytes(7)
        bs.seek(0x58, NOESEEK_ABS)
        rx2TypeID = bs.readBytes(4)
        if Magic != b'\x89\x52\x57\x34\x78\x62\x32':
                return 0
            
        if rx2TypeID == b'\x00\x00\x10\x00':
                print("RX2 TYPE: TEXTURE")
                return 1


        return 0

def CheckTextureTypePS3(data):
        bs = NoeBitStream(data)
        Magic = bs.readBytes(7)
        bs.seek(0xC0, NOESEEK_ABS)
        psgTypeID = bs.readBytes(4)
            
        if Magic != b'\x89\x52\x57\x34\x70\x73\x33':
                return 0
            
        if psgTypeID == b'\x00\x01\x00\x04':
                print("PSG TYPE: TEXTURE")
                return 1

        


        return 0


#Window GUI For EA RenderWare4 Tool START---------------------------------------------------------------------------------------------

def createInterfaceWindow(noeWnd):
    noeWnd.setFont("Arial", 14)

    noeWnd.poseCount = 0
    noeWnd.freshPose = False
    noeWnd.lastPose = None
    noeWnd.trackStartTime = 0.0
    
    standardTextFieldSize = 22
    currentY = 16
    
    noeWnd.createButton("TEST", 16, currentY, 96, 24, buttonSKATE)       
    currentY += 32

def calculateCanvasRect(noeWnd):
    hWnd = noeWnd.hWnd
    rect = noewin.RECT()
    user32.GetClientRect(hWnd, byref(rect))
    
    rectWidth = rect.right - rect.left
    rectHeight = rect.bottom - rect.top
    canvasRect = noewin.RECT()
    return canvasRect


def buttonSKATE(noeWnd, controlId, wParam, lParam):
    GAME_SPECIFIC = "SKATE"
    print("Game specific is: ", GAME_SPECIFIC)

def buttonFIFA09(noeWnd, controlId, wParam, lParam):
    GAME_SPECIFIC = "FIFA09"
    print("Game specific is: ", GAME_SPECIFIC)

def SkateWindowProc(hWnd, message, wParam, lParam):
    if message == noewin.WM_PAINT:
        noeWnd = noewin.getNoeWndForHWnd(hWnd)
        ps = noewin.PAINTSTRUCT()
        hDC = user32.BeginPaint(hWnd, byref(ps))        
        
        canvasRect = calculateCanvasRect(noeWnd)

        user32.EndPaint(hWnd, byref(ps))
    
    return noewin.defaultWindowProc(hWnd, message, wParam, lParam)


def setDefaultWindowPos(noeWnd):
    #offset a bit into the noesis window
    noeWindowRect = noewin.getNoesisWindowRect()
    if noeWindowRect:
        windowMargin = 64
        noeWnd.x = noeWindowRect[0] + windowMargin
        noeWnd.y = noeWindowRect[1] + windowMargin

def SKATEToolMethod(toolIndex):
    noeWnd = noewin.NoeUserWindow("EA RenderWare4 Tool", "SkateWindowClass", 644, 750, SkateWindowProc)
    setDefaultWindowPos(noeWnd)
    if not noesis.getWindowHandle():
        #if invoked via ?runtool, we're our own entity
        noeWnd.becomeStandaloneWindow(0)
    if noeWnd.createWindow():
        noeWnd.hCanvasBmp = None
        noeWnd.dumpFile = None
        createInterfaceWindow(noeWnd)
        noeWnd.doModal()
        destroyCanvasObjects(noeWnd)
    return 0


def destroyCanvasObjects(noeWnd):
    if noeWnd.hCanvasBmp:
        gdi32.DeleteObject(noeWnd.hCanvasDc)
        gdi32.DeleteObject(noeWnd.hCanvasBmp)
        gdi32.DeleteObject(noeWnd.hCanvasMapOnlyDc)
        gdi32.DeleteObject(noeWnd.hCanvasMapOnlyBmp)
        gdi32.DeleteObject(noeWnd.hBgBrush)
        gdi32.DeleteObject(noeWnd.hBorderPen)
        gdi32.DeleteObject(noeWnd.hTrailPen)
        gdi32.DeleteObject(noeWnd.hRoombaPen)
        gdi32.DeleteObject(noeWnd.hRoombaDirPen)
        gdi32.DeleteObject(noeWnd.hRoombaBrush)


#Window GUI For EA RenderWare4 Tool END---------------------------------------------------------------------------------------------

#Load the Xbox 360 textures
def noepyLoadRGBAXbox(data, texList):
    bs = NoeBitStream(data, NOE_BIGENDIAN)
    bs.seek(0x20, NOESEEK_ABS)
    fileCount = bs.read(">i")
    fileCountInt = int(''.join(map(str, fileCount)))
    bs.seek(12, NOESEEK_REL)
    fileTable = bs.read(">i")

    bs.seek(0x44, NOESEEK_ABS)
    TexDataStartOffset = []
    TexDataStartOffset.append(bs.read(">i"))
    TexDataStartOffsetInt = int(''.join(map(str, TexDataStartOffset[0])))

    TexNextStartOffset = []

    TexOffset = []
    TexBufferSize = []
    TexFmtOffset = []
    TexFmt = []
    TexSize = []
    TexInfo = []
    texCount = 0
    sizeHeight = []
    sizeWidth = []

    bs.seek(fileTable[0], NOESEEK_ABS) #Seek to fileTable location in our rx2

    for i in range(0, fileCount[0]):
                        
                        fileInfo = bs.read(">iiiii")
                        fileType = bs.readBytes(4)
                        print(fileType)
                        if fileType == b'\x00\x02\x00\xE8': #EA Skate Support
                                bs.seek(-48, NOESEEK_REL)
                                info = bs.read(">iiiiiiiiiiii")
                                TexNextStartOffset.append([info[0]])
                                TexBufferSize.append([info[2]])
                                TexInfo.append([info[6]])
                                texCount +=1
                        elif fileType == b'\x00\x02\x00\x03': #EA NHL 2010 | NHL Legacy and more
                                bs.seek(-48, NOESEEK_REL)
                                info = bs.read(">iiiiiiiiiiii")
                                TexNextStartOffset.append([info[0]])
                                TexBufferSize.append([info[2]])
                                TexInfo.append([info[6]])
                                texCount +=1



    for k in range(0, texCount):

            bs.seek(TexInfo[k][0], NOESEEK_ABS)
            info = bs.read(">iiiiiiiBBHHb")
            imgFmt = bs.readBytes(1)
            sizeInfo = bs.read(">BBH")
            imgHeight = (sizeInfo[1] + 1) * 8
            imgWidth = (sizeInfo[2] + 1) & 0x1FFF
            print(sizeInfo)
            info2 = bs.read(">iiHH")
            TexFmt.append(imgFmt)
            print("---------------------------------------------------------------")
            print("File: ", k, " / ", texCount)
            print("TexFmt: ", imgFmt)
            print("TexFmt ID 2: ", info2[3])
            print("TexFmt ID 3", info[7])
            print("TexOffset: ",TexDataStartOffsetInt + TexNextStartOffset[k][0])
            print("TexBufferSize: ", TexBufferSize[k])
            print("End of Texture: ", TexDataStartOffsetInt + TexNextStartOffset[k][0] + TexBufferSize[k][0])

            #Backup
            #imgHeight = ((size >> 13) & 0x1FFF) + 1
            #imgWidth  = (size + 1) & 0x1FFF

            print((imgHeight), ":imgHeight")
            print((imgWidth), ":imgWidth")
            bs.seek((TexDataStartOffsetInt + TexNextStartOffset[k][0]), NOESEEK_ABS)
            print(TexBufferSize[k][0])
            
            data = bs.readBytes(TexBufferSize[k][0])
   
            if TexFmt[k][0] == 0x52:
                data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 8)
                TextureFmt = noesis.NOESISTEX_DXT1
            elif TexFmt[k][0] == 0x53:
                data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
                TextureFmt = noesis.NOESISTEX_DXT3
            elif TexFmt[k][0] == 0x54:
                #There seems to be multiple types of DXT5 in some games
                if info[7] == 1 or info[7] == 2 or info[7] == 84:
                    data = rapi.imageDecodeDXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, noesis.FOURCC_DXT5)
                    TextureFmt = noesis.NOESISTEX_RGBA32
                else:
                    data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
                    TextureFmt = noesis.NOESISTEX_DXT5
            elif TexFmt[k][0] == 0x71:
                data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 16)
                data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_ATI2)
                TextureFmt = noesis.NOESISTEX_RGBA32
            elif TexFmt[k][0] == 0x7C:
                data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 83)
                data = rapi.imageDecodeDXT(data, imgWidth, imgHeight, noesis.FOURCC_DXT1NORMAL)
                TextureFmt = noesis.NOESISTEX_RGBA32
            elif TexFmt[k][0] == 0x86:
                data = rapi.imageUntile360Raw(data, imgWidth, imgHeight, 4) #Sometimes you might not need this, keep that in mind if you find one that doesn't work but has 0x86 in the header.
                data = rapi.imageDecodeRaw(data, imgWidth, imgHeight, "a8r8g8b8")
                TextureFmt = noesis.NOESISTEX_RGBA32
            elif TexFmt[k][0] == 0x44:
                data = rapi.imageUntile360Raw(rapi.swapEndianArray(data, 2), imgWidth, imgHeight, 2)
                data = rapi.imageDecodeRaw(data, imgWidth, imgHeight, "b5g6r5")
                TextureFmt = noesis.NOESISTEX_RGBA32
            elif TexFmt[k][0] == 0x02:
                data = rapi.imageUntile360Raw(data, imgWidth, imgHeight, 1)
                data = rapi.imageDecodeRaw(data, imgWidth, imgHeight, "A8")
                TextureFmt = noesis.NOESISTEX_RGBA32
            else:
                print("WARNING: Unhandled image format")
                return None
            texList.append(NoeTexture(rapi.getInputName(), imgWidth, imgHeight, data, TextureFmt))
    
    return 1


#Load the PS3 textures
def noepyLoadRGBAPS3Multi(data, texList):
    bs = NoeBitStream(data, NOE_BIGENDIAN)

    bs.seek(0x20, NOESEEK_ABS)
    fileCount = bs.read(">i")
    fileCountInt = int(''.join(map(str, fileCount)))
    bs.seek(12, NOESEEK_REL)
    fileTable = bs.read(">i")

    bs.seek(0x44, NOESEEK_ABS)
    TexDataStartOffset = []
    TexDataStartOffset.append(bs.read(">i"))
    TexDataStartOffsetInt = int(''.join(map(str, TexDataStartOffset[0])))

    TexOffset = []
    TexBufferSize = []
    TexNextStartOffset = []
    TexFmtOffset = []
    TexFmt = []
    TexSize = []
    TexInfo = []
    texCount = 0
    sizeHeight = []
    sizeWidth = []
    #data = []

    bs.seek(fileTable[0], NOESEEK_ABS) #Seek to fileTable location in our psg / rpsgl

    for i in range(0, fileCount[0]):
                        
                        fileInfo = bs.read(">iiiii")
                        fileType = bs.readBytes(4)
                        print(fileType)
                        if fileType == b'\x00\x02\x00\xE8': #EA Skate Support
                                bs.seek(-48, NOESEEK_REL)
                                info = bs.read(">iiiiiiiiiiii")
                                TexNextStartOffset.append([info[0]])
                                TexBufferSize.append([info[2]])
                                print("BufferSize: ", [info[2]])
                                TexInfo.append([info[6]])
                                texCount +=1
                        elif fileType == b'\x00\x02\x00\x03': #NHL Legacy Support
                                bs.seek(-48, NOESEEK_REL)
                                info = bs.read(">iiiiiiiiiiii")
                                TexNextStartOffset.append([info[0]])
                                TexBufferSize.append([info[2]])
                                print(info[6])
                                TexInfo.append([info[6]])
                                texCount +=1




    for k in range(0, texCount):

            if GAME_SPECIFIC == "SKATE": 
                    bs.seek(TexInfo[k][0], NOESEEK_ABS)
                    imgFmt = bs.readBytes(1)
                    info2 = bs.read(">bbbi")
                    imgWidth = bs.readUShort()
                    imgHeight  = bs.readUShort()
                    TexFmt.append(imgFmt)
                    TexOffset.append(TexInfo[k])
            elif GAME_SPECIFIC == "FIFA09":
                    bs.seek(TexInfo[k][0], NOESEEK_ABS)
                    info2 = bs.read(">iiiiiiiiH")
                    imgFmt = bs.readBytes(2)
                    padding = bs.read(">HHii")
                    imgWidth = bs.readUShort()
                    imgHeight  = bs.readUShort()
                    TexFmt.append(imgFmt)
                    TexOffset.append(TexInfo[k])
                
            print("---------------------------------------------------------------")
            print("File: ", k, " / ", texCount)
            print("TexFmt: ", imgFmt)
            print("TexOffset: ",TexDataStartOffsetInt + TexNextStartOffset[k][0])
            print("TexBufferSize: ", TexBufferSize[k])
            print("End of Texture: ", TexDataStartOffsetInt + TexNextStartOffset[k][0] + TexBufferSize[k][0])
            print((imgHeight), ":imgHeight")
            print((imgWidth), ":imgWidth")
            bs.seek((TexDataStartOffsetInt + TexNextStartOffset[k][0]), NOESEEK_ABS)
            print(TexBufferSize[k][0])
            
            data = bs.readBytes(TexBufferSize[k][0])
                    
            #DXT1
            if imgFmt == b'\xA6' or imgFmt == b'\x86' or imgFmt == b'\x83\xF1':
                texFmt = noesis.NOESISTEX_DXT1
            #DXT3
            elif imgFmt == b'\x87' or imgFmt == b'\x83\xF2':
                texFmt = noesis.NOESISTEX_DXT3
            #DXT5
            elif imgFmt == b'\x88' or imgFmt == b'\x83\xF3':
                texFmt = noesis.NOESISTEX_DXT5
            #RGBA8888
            elif imgFmt == b'\xa5' or imgFmt == b'\x60\x07':
                texFmt = noesis.NOESISTEX_RGBA32
            #A8 Swizzled with PS3 MortonOrder
            elif imgFmt == b'\x81':
                data = rapi.imageFromMortonOrder(data, imgWidth, imgHeight)
                data = rapi.imageDecodeRaw(data, imgWidth, imgHeight, "A8")
                texFmt = noesis.NOESISTEX_RGBA32
            elif imgFmt == b'\x85':
                untwid = bytearray()
                for x in range(0, imgWidth):
                    for y in range(0, imgHeight):
                        idx = noesis.morton2D(x, y)
                        untwid += data[idx*4:idx*4+4]
                data = rapi.imageDecodeRaw(untwid, imgWidth, imgHeight, "a8 r8 g8 b8")
                texFmt = noesis.NOESISTEX_RGBA32
            #unknown, not handled
            else:
                print("WARNING: Unhandled image format")
                return None
            texList.append(NoeTexture(rapi.getInputName(), imgWidth, imgHeight, data, texFmt))
    
    return 1



#load the model
def noepyLoadModel(data, mdlList):
         print("\n")
         print(">>>>>>>>>>>>START OF FILE<<<<<<<<<<<<<")
         print("\n")
         VIndexOffset = []
         VInfo = []
         VOff = []
         VBufferSize = []
         
         FInfo = []   
         FOff = []
         FBufferSize = []

         BoneIndexOffset = []
         BoneInfo = []
         BoneOff = []
         BoneBufferSize = []
         BoneNames = []
         jointList = []
         jointMatrices = []
         jointNames = []
         skeletonCount = 0
         
         MeshInfo = []
         MeshNames = []
         MeshNamesOff = 0
         MeshNameCount = 0
         
         UVpos = []
         UV2pos = []
         UV3pos = []
         UVtype = []
         UV2type = []
         UV3type = []

         MatHeadOff = 0
         MaterialCount = 0
         MatHeaderSize = 0
         MatParamsSize = 0

         DiffuseNames = []
         DiffuseNamesCount = 0
         
         MaterialNames = []
         MaterialTypes = []
         MaterialTypeOffsets = []
         MaterialNameOffsets = []
         
         VertType = []
         VBsize = []
         vertsPresent = 0
         facesPresent = 0

         #Bones = []
         #Bone_Pallet = []
         #Bone_Matrix = []
         #Bone_Name = []
         #Bone_Parent = []

         print("------------GENERAL INFORMATION------------")
         ctx = rapi.rpgCreateContext()
         bs = NoeBitStream(data, NOE_BIGENDIAN)
         bs.seek(0x20, NOESEEK_ABS)
         fileCount = bs.read(">i")
         fileCountInt = int(''.join(map(str, fileCount)))
         bs.seek(12, NOESEEK_REL)
         fileTable = bs.read(">i")
         bs.seek(16, NOESEEK_REL)
         hdrSize = bs.read(">i")
         bs.seek(560, NOESEEK_ABS)
         NamesLocationOffset = int(''.join(map(str, bs.read(">i"))))
         NamesLocation = NamesLocationOffset + 544
         print("Names Location: ", NamesLocation)
         print("File Count: ", fileCountInt)
         
         bs.seek(fileTable[0], NOESEEK_ABS)
         meshCount = 0
         vertFieldCount = 0
         faceFieldCount = 0
         

         print("\n")
         
         
         for i in range(0, fileCount[0]):
                        
                        fileInfo = bs.read(">iiiii")
                        fileType = bs.readBytes(4)
                        print("Seeking for filetypes...")
                        if fileType == b'\x00\x02\x00\xEA': #EA Skate Supported vertices ID in TOC
                                                print("Found Vertex filetype!")
                                                VIndexOffset.append(bs.seek(44, NOESEEK_REL))
                                                NoFacesCheck = bs.readBytes(4)
                                                if NoFacesCheck == b'\x00\x02\x00\xEB': #Some meshes don't have any faces to them, so we check for those instances and bypasses them
                                                        bs.seek(-96, NOESEEK_REL)
                                                        info = bs.read(">iiiiiiiiiiii")
                                                        VOff.append([info[0]])
                                                        VBufferSize.append([info[2]])
                                                        VInfo.append([info[6]])
                                                        meshCount +=1
                                                        vertFieldCount +=1
                                                #vertsPresent = 1
                                                                                                                                                                
                        elif fileType == b'\x00\x02\x00\xEB': #EA Skate Supported Faces ID in TOC
                                                print("Found faces filetype!")
                                                bs.seek(44, NOESEEK_REL)
                                                Skate1FileType = bs.readBytes(4)
                                                bs.seek(-96, NOESEEK_REL)
                                                info = bs.read(">iiiiiiiiiiii")
                                                faceFieldCount +=1
                                                #facesPresent = 1
                                                
                                                if Skate1FileType != b'\x00\x02\x00\xEB': #We go back one TOC step and check if there is 2 face IDs in a row like there is for some meshes in Skate 1. (we bypass these)
                                                        FOff.append([info[0]])
                                                        FBufferSize.append([info[2]])
                                                        FInfo.append([info[6]])                                                                                         
                        elif fileType == b'\x00\x02\x00\xE9':
                                MeshInfo.append([fileInfo[0]])

                        elif fileType == b'\x00\xEB\x00\x0D': #MESH LOD NAME ID in TOC
                                print("Found LOD meshnames filetype!")
                                bs.seek(-24, NOESEEK_REL)
                                info = bs.read(">iiiiii")
                                print("LOD meshnames TOC Offset: ", bs.tell())
                                
                                
                                
                                

                        elif fileType == b'\x00\xEB\x00\x05': #Material ID in TOC
                                print("Found materials filetype!")
                                bs.seek(-48, NOESEEK_REL)
                                info = bs.read(">iiiiiiiiiiii")
                                TOClocation = bs.tell()
                                print("Material TOC Offset: ", bs.tell())
                                MatHeadOff = info[6]
                                bs.seek(MatHeadOff, NOESEEK_ABS)
                                matHeadinfo = bs.read(">iiiiiiii")
                                MaterialCount = matHeadinfo[1]
                                MatHeaderSize = matHeadinfo[3]
                                MatParamsSize = matHeadinfo[4]
                                MatParamsBlockSize = int((MatParamsSize -  MatHeaderSize) / MaterialCount)
                                #MatParamsBlockSize = matHeadinfo[7]
                                bs.seek(MatHeadOff + MatHeaderSize, NOESEEK_ABS)
                                print("Material Header Location: ", bs.tell())
                                print("Material Count: ", MaterialCount)
                                print("MatHeaderSize: ", MatHeaderSize)
                                print("MatParamsSize: ", MatParamsSize)
                                print("MatParamsBlockSize: ", MatParamsBlockSize)
                                nextlocation = bs.tell()


                                if MatParamsBlockSize == 32: #Seems to be used by Skate 3 Materials
                                        for i in range(0, MaterialCount):
                                                matInfo = bs.read(">iiiiiiii")
                                                nextlocation = bs.tell()
                                                MaterialTypeOffsets.append(matInfo[0])
                                                MaterialNameOffsets.append(matInfo[6])
                                                bs.seek(MatHeadOff + MaterialTypeOffsets[i], NOESEEK_ABS)
                                                MaterialTypes.append(bs.readString())
                                                bs.seek(MatHeadOff + MaterialNameOffsets[i], NOESEEK_ABS)
                                                MaterialNames.append(bs.readString())
                                                print("Material Types: ", MaterialTypes[i])
                                                print("Material Names: ", MaterialNames[i])
                                                bs.seek(nextlocation, NOESEEK_ABS)
                                                
                                elif MatParamsBlockSize == 24: # Seems to be used by Skate 1 Materials
                                        print("Second type block size")
                                        for i in range(0, MaterialCount):
                                                matInfo = bs.read(">iiiiii")
                                                nextlocation = bs.tell()
                                                MaterialTypeOffsets.append(matInfo[0])
                                                MaterialNameOffsets.append(matInfo[1])
                                                bs.seek(MatHeadOff + MaterialTypeOffsets[i], NOESEEK_ABS)
                                                MaterialTypes.append(bs.readString())
                                                bs.seek(MatHeadOff + MaterialNameOffsets[i], NOESEEK_ABS)
                                                MaterialNames.append(bs.readString())
                                                print("Material Types: ", MaterialTypes[i])
                                                print("Material Names: ", MaterialNames[i])
                                                bs.seek(nextlocation, NOESEEK_ABS)
                                
                                        
                                bs.seek(TOClocation, NOESEEK_ABS)
                                
                                
                                #MaterialNames = []
                                #MaterialTypes = []

                                
                                

                        elif fileType == b'\x00\xEB\x00\x01': #Bones filetype
                                print("Found bones filetype!")
                                BoneIndexOffset.append(bs.seek(0, NOESEEK_REL))
                                bs.seek(-48, NOESEEK_REL)
                                info = bs.read(">iiiiiiiiiiii")
                                BoneOff.append([fileInfo[0]])
                                BoneBufferSize.append([info[2]])
                                BoneInfo.append([info[6]])
                                skeletonCount +=1

         for i in range(0, MaterialCount):
                 print("SCANNING FOR MESHNAME!!!!!", i)
                 if MaterialTypes[i] == "Name":
                         MeshNames.append(MaterialNames[i])
                 elif MaterialTypes[i] == "diffuse":
                         DiffuseNamesCount +=1
                         DiffuseNames.append(MaterialNames[i])
         for i in MeshNames:
                 MeshNameCount +=1
                 print("MESH NAME: ", i, " | ", MeshNameCount, " / ",  meshCount)
                                
#Read Mesh info
         for i in range(0, meshCount):
                                bs.seek(MeshInfo[i][0], NOESEEK_ABS)
                                info = bs.read(">iiHHi")
                                foundvert = 0
                                foundUV1 = 0
                                foundUV2 = 0
                                foundUV3 = 0
                                for j in range(0, info[2]):
                                                position = bs.read(">i")
                                                type = bs.readBytes(8)
                                                unkn = bs.read(">i")

                                                #Vertex Type

                                                if type == b'\x00\x2A\x23\xB9\x00\x00\x00\x01':
                                                                VertType = 1
                                                                #FLOAT
                                                                
                                                elif type == b'\x00\x1A\x23\x60\x00\x00\x00\x01':
                                                                VertType = 2
                                                                #HALFFLOAT
                                                                
                                                elif type == b'\x00\x1A\x23\xA6\x00\x00\x00\x01':
                                                                VertType = 3
                                                                #USHORT
                                                                
                                                elif type == b'\x00\x1A\x21\x5A\x00\x00\x00\x01':
                                                                VertType = 4
                                                                #SHORT

                                                #UV Position 1

                                                if type == b'\x00\x2C\x23\xA5\x00\x05\x00\x06':
                                                                UVpos.append(position[0])
                                                                UVtype.append(1)
                                                                foundUV1 = 1
                                                                #FLOAT UV1
     
                                                elif type == b'\x00\x1A\x23\x60\x00\x05\x00\x06':
                                                                UVpos.append(position[0])
                                                                UVtype.append(2)
                                                                foundUV1 = 1
                                                                #HALFFLOAT UV1

                                                elif type == b'\x00\x2C\x23\x5F\x00\x05\x00\x06':
                                                                UVpos.append(position[0])
                                                                UVtype.append(3)
                                                                foundUV1 = 1
                                                                #HALFFLOAT UV1
                                                                
                                                elif type == b'\x00\x2C\x21\x59\x00\x05\x00\x06':
                                                                UVpos.append(position[0])
                                                                UVtype.append(4)
                                                                foundUV1 = 1
                                                                #SHORT UV1
                                                                
                                                elif type == b'\x00\x2C\x20\x59\x00\x05\x00\x06':
                                                                UVpos.append(position[0])
                                                                UVtype.append(5)
                                                                foundUV1 = 1
                                                                #USHORT UV1

                                                else:
                                                                if j == (info[2] - 1) and foundUV1 == 0:
                                                                        UVpos.append(position[0])
                                                                        UVtype.append(0)


                                                #UV Position 2

                                                if type == b'\x00\x2C\x21\x59\x00\x05\x01\x07':
                                                                UV2pos.append(position[0])
                                                                UV2type.append(1)
                                                                foundUV2 = 1
                                                                #SHORT UV2
                                                else:
                                                                if j == (info[2] - 1) and foundUV2 == 0:
                                                                        UV2pos.append(position[0])
                                                                        UV2type.append(0)

                                                #UV Position 3

                                                if type == b'\x00\x2C\x23\x5F\x00\x05\x02\x08':
                                                                UV3pos.append(position[0])
                                                                UV3type.append(1)
                                                                foundUV3 = 1
                                                                #HALFFLOAT UV3
                                                else:
                                                                if j == (info[2] - 1) and foundUV3 == 0:
                                                                        UV3pos.append(position[0])
                                                                        UV3type.append(0)





                                size = bs.read(">B")
                                VBsize.append(size[0])
                                
         for i in range(0, meshCount):
                                rapi.rpgClearBufferBinds()
                                if USE_MESH_NAMES == 1:
                                    if MeshNameCount == meshCount:
                                        rapi.rpgSetName(MeshNames[i] + str(i))
                                    else:
                                        rapi.rpgSetName("mesh" + str(i))
                                elif USE_MESH_NAMES == 0:
                                    rapi.rpgSetName("mesh" + str(i))
                                    print("Not using mesh names")

                                if USE_MATERIAL_NAMES == 1:
                                    if DiffuseNamesCount == meshCount:
                                        rapi.rpgSetMaterial(DiffuseNames[i])
                                    else:
                                        print("Not the same amount of diffuse materials as meshes")
                                elif USE_MATERIAL_NAMES == 0:
                                    print("Not using material names")
                                    
                                bs.seek(FInfo[i][0] + 32, NOESEEK_ABS) #Seek to faces info  
                                FCount = bs.read(">i")
                                
                                #Seek to Vertices Start
                                bs.seek(VOff[i][0] + hdrSize[0], NOESEEK_ABS)
                                VertBuff = bs.readBytes(VBufferSize[i][0])
                                VCount = VBufferSize[i][0] / VBsize[i]
                                print("::::::::::::::::::::::NEW MESH:::::::::::::::::::::: ( This information can be used for debugging the script or for modding EA SKATE meshes )")
                                print("Mesh Count: ", i, " / ", meshCount)
                                print("\n")
                                print("------------VERTICES------------")
                                print("Vertex Index Offset: ", VIndexOffset[i])
                                print("Vertex Offset: ", VOff[i][0] + hdrSize[0])
                                print("Vert Field Count: ", vertFieldCount)
                                print("Vertex Count: ", int(VCount))
                                print("Vertex Buffer Size: ", VBufferSize[i][0])
                                rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
                                if VertType == 1:
                                        print("Vertex Type: FLOAT")
                                        rapi.rpgBindPositionBufferOfs(VertBuff, noesis.RPGEODATA_FLOAT, VBsize[i], 0)
                                elif VertType == 2:
                                        print("Vertex Type: HALFFLOAT")
                                        rapi.rpgBindPositionBufferOfs(VertBuff, noesis.RPGEODATA_HALFFLOAT, VBsize[i], 0)
                                elif VertType == 3:
                                        print("Vertex Type: USHORT")
                                        rapi.rpgBindPositionBufferOfs(VertBuff, noesis.RPGEODATA_USHORT, VBsize[i], 0)
                                elif VertType == 4:
                                        print("Vertex Type: SHORT")
                                        rapi.rpgBindPositionBufferOfs(VertBuff, noesis.RPGEODATA_SHORT, VBsize[i], 0)
                                
                                print("\n")
                                print("------------UVs------------")
                                print("UVPosition: ", UVpos[i])
                                if UVtype[i] == 1:
                                                print("UV Type: FLOAT")
                                                rapi.rpgBindUV1BufferOfs(VertBuff, noesis.RPGEODATA_FLOAT, VBsize[i], UVpos[i]) 
                                elif UVtype[i] == 2:
                                                print("UV Type: HALFFLOAT")
                                                rapi.rpgBindUV1BufferOfs(VertBuff, noesis.RPGEODATA_HALFFLOAT, VBsize[i], UVpos[i])
                                elif UVtype[i] == 3:
                                                print("UV Type: HALFFLOAT 2")
                                                rapi.rpgBindUV1BufferOfs(VertBuff, noesis.RPGEODATA_HALFFLOAT, VBsize[i], UVpos[i])
                                elif UVtype[i] == 4:
                                                print("UV Type: SHORT")
                                                rapi.rpgBindUV1BufferOfs(VertBuff, noesis.RPGEODATA_SHORT, VBsize[i], UVpos[i])
                                elif UVtype[i] == 5:
                                                print("UV Type: USHORT")
                                                rapi.rpgBindUV1BufferOfs(VertBuff, noesis.RPGEODATA_USHORT, VBsize[i], UVpos[i])
                                elif UVtype[i] == 0:
                                                #No UV1s
                                                print("UV Type: NO UVs")


                                if UV2type[i] == 1:
                                                print("UV2 Type: SHORT")
                                                rapi.rpgBindUV2BufferOfs(VertBuff, noesis.RPGEODATA_SHORT, VBsize[i], UV2pos[i])
                                elif UV2type[i] == 0:
                                                #No UV2s
                                                print("UV2 Type: NO UVs")
                                                

                                if UV3type[i] == 1:
                                                print("UV3 Type: HALFFLOAT")
                                                rapi.rpgBindUVXBufferOfs(VertBuff, noesis.RPGEODATA_HALFFLOAT, VBsize[i], 2, 2, UV3pos[i])
                                elif UV3type[i] == 0:
                                                #No UV3s
                                                print("UV3 Type: NO UVs")
                                                

                                
                                                
                                                
                                #Seek to Faces Start    
                                bs.seek(FOff[i][0] + hdrSize[0], NOESEEK_ABS)
                                FaceBuff = bs.readBytes(FBufferSize[i][0])
                                print("\n")
                                print("------------FACES------------")
                                print("Faces Offset: ", FOff[i][0] + hdrSize[0])
                                print("Face Field Count: ", faceFieldCount)
                                print("Face Count: ", FCount[0], " | or (for Model Researcher Pro): ", int(FCount[0] / 3))
                                print("Face BufferSize: ", FBufferSize[i][0])
                                print("\n")
                                print("------------BONES------------")
                                print("Skeleton count: ", skeletonCount)
                                for b in range(0, skeletonCount):
                                        bs.seek(BoneOff[b][0], NOESEEK_ABS)
                                        bonesHeaderBuffer = bs.read(">iiiiiiiiiiiiHHHHii")
                                        bonesOffset = bs.seek(0, NOESEEK_REL)
                                        # bonesHeaderBuffer[14] == weight / bones amount | bonesHeaderBuffer[8] == headersize | bonesHeaderBuffer[9] == size of header + bone weights 
                                        # bonesHeaderBuffer[10] == offset to start of bone indices, starting from the header. | bonesHeaderBuffer[11] == Header + Weights + indices size.

                                        BoneWeightsSize = bonesHeaderBuffer[9] - bonesHeaderBuffer[8]
                                        #BoneWeightBuff = bs.readBytes(BoneWeightsSize)

                                        #bs.seek(BoneOff[b][0] + bonesHeaderBuffer[10], NOESEEK_ABS)
                                        
                                        BoneIndexBuffSize = bonesHeaderBuffer[14] * 4
                                        #BoneIndexBuff = bs.readBytes(BoneIndexBuffSize)

                                        print("Bones TOC Index Offset: ", BoneIndexOffset[b])
                                        print("Bones Offset: ", bonesOffset)
                                        print("Bones Buffer Size: ", BoneWeightsSize)
                                        print("Bones count: ", bonesHeaderBuffer[14])
                                        print("Bones Indices Offset: ", BoneOff[b][0] + bonesHeaderBuffer[10])
                                        print("Bones Indices Buffer Size: ", BoneIndexBuffSize)

                                        print("Where are we? ", bs.tell())

                                        for _ in range(bonesHeaderBuffer[14]):
                                                jointMatrices.append(NoeMat44.fromBytes(bs.readBytes(0x40),1).toMat43())
                                        bs.seek(BoneOff[b][0] + bonesHeaderBuffer[11], NOESEEK_ABS)

                                        for i in range(bonesHeaderBuffer[14]):
                                                jointNames.append(bs.readString())
                                                print("Bones Name: ", jointNames[i], i, " / ", bonesHeaderBuffer[14])
    
                                        for i, (name, matrix) in enumerate(zip(jointNames, jointMatrices)):     
                                                joint = NoeBone(i, name, matrix, None, -1)
                                                jointList.append(joint)
                                                
                                        print("\n")
                                        
                                if LOAD_POINT_CLOUD == 0:
                                        rapi.rpgCommitTriangles(FaceBuff, noesis.RPGEODATA_USHORT, FCount[0], noesis.RPGEO_TRIANGLE, 1)
                                elif LOAD_POINT_CLOUD == 1:
                                        rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, int(VCount), noesis.RPGEO_POINTS, 1)
                                

         try:
                mdl = rapi.rpgConstructModel()
         except:
                print('Error')
                
         mdl.setBones(jointList)
         mdlList.append(mdl)         #important, don't forget to put your loaded model in the mdlList
         rapi.rpgClearBufferBinds()
         rapi.rpgReset()
         return 1




#load the Sim / Collision
def noepyLoadSim(data, mdlList):
         print("\n")
         print(">>>>>>>>>>>>START OF FILE<<<<<<<<<<<<<")
         print("\n")

         TotalSimBufferSize = []
         SpawnLocation = []
         
         VIndexOffset = []
         VInfo = []
         VOff = []
         VBufferSize = []
         
         FInfo = []   
         FOff = []
         FBufferSize = []
         
         MeshInfo = []
         
         VertType = []
         VBsize = []
         vertsPresent = 0
         facesPresent = 0

         print("------------GENERAL INFORMATION------------")
         ctx = rapi.rpgCreateContext()
         bs = NoeBitStream(data, NOE_BIGENDIAN)
         bs.seek(0x20, NOESEEK_ABS)
         fileCount = bs.read(">i")
         fileCountInt = int(''.join(map(str, fileCount)))
         bs.seek(12, NOESEEK_REL)
         fileTable = bs.read(">i")
         bs.seek(16, NOESEEK_REL)
         hdrSize = bs.read(">i")
         bs.seek(560, NOESEEK_ABS)
         bs.seek(fileTable[0], NOESEEK_ABS)
         simCount = 0

         

         print("\n")
         
         
         for i in range(0, fileCount[0]):
                        
                        fileInfo = bs.read(">iiiii")
                        fileType = bs.readBytes(4)
                        
                        if fileType == b'\x00\xEB\x00\x0B':
                                        bs.seek(-48, NOESEEK_REL)
                                        info = bs.read(">iiiiiiiiiiii")
                                        SpawnLocation.append([info[0]])
                                        TotalSimBufferSize.append([info[2]])
                                        VInfo.append([info[6]])
                                        MeshInfo.append([fileInfo[0]])
                                        simCount +=1
                                        
                                
#Read Sim info
         for i in range(0, simCount):
                                bs.seek(MeshInfo[i][0], NOESEEK_ABS)
                                info = bs.read(">iiiii")
                                for j in range(0, info[2]):
                                        hello = 0
                                
         for i in range(0, simCount):
                                rapi.rpgClearBufferBinds()
                                rapi.rpgSetName("sim" + str(i))
                                
                                #Seek to Vertices Start
                                bs.seek(SpawnLocation[i][0], NOESEEK_ABS)
                                simHeaderInfo = bs.read(">iiiiiiiiiiii")
                                CollisionFacesAmount = simHeaderInfo[8]
                                SimHeaderSize = simHeaderInfo[9]
                                CollisionVertexArraySize = simHeaderInfo[10]
                                HeaderAndFacesSize = simHeaderInfo[11]
                                FaceBufferSize = HeaderAndFacesSize - SimHeaderSize
                                VertBufferSize = TotalSimBufferSize[i][0] - HeaderAndFacesSize
                                
                                FaceBuff = bs.readBytes(FaceBufferSize)
                                VertBuff = bs.readBytes(VertBufferSize)
                                VCount = VertBufferSize / 4
                                print("::::::::::::::::::::::NEW SIM:::::::::::::::::::::: ( This information can be used for debugging the script or for modding EA SKATE meshes )")
                                print("Sim Count: ", i, " / ", fileCountInt)
                                print("\n")
                                print("------------SIM VERTICES------------")
                                print("Vertex Count: ", int(VCount))
                                rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)

                                rapi.rpgBindPositionBufferOfs(VertBuff, noesis.RPGEODATA_SHORT, 2, 0)
                                


                                rapi.rpgCommitTriangles(None, noesis.RPGEODATA_USHORT, int(VCount), noesis.RPGEO_POINTS, 1)
                                

         try:
                mdl = rapi.rpgConstructModel()
         except:
                print('Error')
                 
         mdlList.append(mdl)         #important, don't forget to put your loaded model in the mdlList
         rapi.rpgClearBufferBinds()
         rapi.rpgReset()
         return 1
