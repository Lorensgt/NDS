import os, math,sys,re,datetime,time
from os import listdir
from os.path import isfile, join

"""
TODO:
'''https://gbatemp.net/threads/reading-the-nds-icon-data.45360/'''
'''https://dsibrew.org/wiki/DSi_Cartridge_Header'''
"""

text={
    "es":{
    "INFO_name_language":"Español",
    "INFO_progres":"Progreso",
    "INFO_item_list_found":"Estos son los archivos encontrados:",
    "INFO_erase_rom":"Eliminando %s.",
    "INFO_rom_props":"Las características de la rom:",
    "INFO_no_lang_verbose":"No se ha selecionado idioma",
    "INFO_item_select":"Que imagenes deseas seleccionar:",
    "ERROR_none_verbose_mode":"No se reconoce el modo. Use:",
    "ERROR_type_verbose_mode":"No se reconoce el modo. Use:",
    "ERROR_type_language_mode":"Idioma no reconocido. Use:",
    "INFO_rom_info_error_no_rom":"No se reconoce el formato de la rom. %s",
    "ERROR_index_no_exist":"Uno de los valores introducidos no existe.",
    "INFO_rom_info_finish":"Reducir| Rom:%s Peso:%s Basura:%s Tiempo:%ss\nSalida:%s ",
    "INFO_rom_info_finish_repair":"Reparar| Rom:%s Peso:%s Tiempo:%ss\nSalida:%s",

    "INFO_rom_info_only":(
    """ARCHIVO:        %s \n"""      \
    """PESO:           %s   \n"""      \
    """NOMBRE ROM:     %s   \n"""      \
    """CODIGO:         %s   \n"""      \
    """LOGO:           %s   \n"""      \
    """HEADER CHECK:   %s   """),
    "HELP":"""    NDSX
    Utiles para roms de NDS

    Opciones              Descripción
    -a                    Muestra solo la info de la rom.
    -n                    Cambia el nombre de la rom por el de la base de datos.
    -r                    Recursivo.
    -s                    Seleccionar los archivos a convertir.
    -i                    Ruta de entrada personalizada.
    -o                    Ruta de salida personalizada.
    -d                    Elimina el archivo de origen.
    -f                    Solo reparar la rom.
    -v [mode][Idioma]     Verbose - all|short Idioma

    Para el cambio de Idioma usar '-v código_de_idioma'
    Ej: -v es | Para el español.
    Idiomas disponibles:"""
    }
}

#Utils--------------------------------------------------------------------------
def getDate():
    now = datetime.datetime.now()
    return ("%02i:%02i:%02i")%(now.hour, now.minute, now.second)

def bytesToSize(bytes):
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    if bytes == 0:
       return '0 Byte'
    i = int(math.floor(math.log(bytes) / math.log(1024)))
    return str(round(bytes / math.pow(1024, i), 2)) + ' ' + sizes[i]

def printError(text):
    print(text)

def printInfo(text,verbose,type):
    if verbose == type or verbose == 'all' or type =='info':
        print(text)

def get_terminal_size(fd=sys.stdout.fileno()):
    h,w = os.popen('stty size', 'r').read().split()
    return int(h),int(w)

def update_progress(progress,in_text):
    #Calculate bar len
    barLength = (console_width-len(text[LG]["INFO_progres"]+
                " "+in_text+": 100% []") - 1)
    #Calculate nº blocks
    block = int(round(barLength*progress)) + 1

    #Format text
    out_text = ("\r"+text[LG]["INFO_progres"]+
            " "+in_text+": [{blocks}] {percent:.0f}%".format(
            blocks="■" * block + "-" * (barLength - block),
            times=time,
            percent=progress * 100))

    sys.stdout.write(out_text)
    sys.stdout.flush()

def create_bar(path):
    #Calculate bar len
    barLength = (console_width-len(path) - 1)
    #Format text
    text = (path +"{blocks}".format(
            blocks="-" * barLength))

    return text

def getFile(extension,path_):
    try:
        if path_:
            path=path_
        else:
            path = os.getcwd()
    except:
        path = os.getcwd()

    extension_len=len(extension)
    files_list = []

    if RECURSIVE == True:
        for root, directories, filenames in os.walk(path):
            for filename in filenames:
                if filename[-extension_len:] == extension:
                    files_list.append({"root":root,"filename":filename})

        return len(files_list),files_list

    else:
        for f in listdir(path):
            if isfile(join(path, f)):
                if f[-extension_len:] == extension:
                    files_list.append({"root":path,"filename":f})

        return len(files_list),files_list

def selectFiles(extension):
    nfiles,files =getFile(extension,INPUT_PATH)
    printInfo(text[LG]["INFO_item_list_found"]
             +" "+str(nfiles),VERBOSE_MODE,"info")

    if SELECT_FILES:
        root=""
        while True:
            for index, file in enumerate(files):
                if file["root"] != root:
                    root = file["root"]
                    printInfo(create_bar(root),VERBOSE_MODE,"info")
                printSTR = "  "+str(index)+":  "+file["filename"]
                printInfo(printSTR,VERBOSE_MODE,"info")
            select_indexes = (input(text[LG]["INFO_item_select"])
                              .split())
            selected=[]
            try:
                for index in select_indexes:
                    selected.append(files[int(index)])
                break

            except:
                printInfo(text[LG]["ERROR_index_no_exist"],
                         VERBOSE_MODE,"info")

        for x in selected:
            printInfo(os.path.join(x["root"],x["filename"]),
                     VERBOSE_MODE,"short")
        return selected
    else:
        for index, file in enumerate(files):
            printInfo(str(index)+":  "+
                      os.path.join(file["root"],file["filename"]),
                      VERBOSE_MODE,"short")
        return files



def trimRom(romHeader,OUTPUT_PATH):
    o_file=os.path.join(romHeader['romPath'],romHeader['romFilename'])
    if OUTPUT_PATH == "":
        OUTPUT_PATH = romHeader['romPath']
    if RENAME:
        name_out =os.path.join(OUTPUT_PATH,(" ").join(romHeader['romBannerNameES'].splitlines()[:-1]).replace("\x00","")+".nds")
    else:
        name_out = os.path.join(OUTPUT_PATH,romHeader['romFilename'][:-4]+"_trim.nds")

    start_time = time.time()

    with open(o_file,'rb') as file:
        rom = file.read()[::-1]
        temp_data = file.read()
        trim_size=0
        update_progress(0,"Read file")
        for index,byte in enumerate(rom):
            if (bytes([byte]) == b"\x00" or bytes([rom[index+1]]) == b"\xff"
            and bytes([byte]) == b"\x00" or bytes([rom[index+1]]) == b"\xff"):
                pass
            else:
                trim_size = bytesToSize(index)
                temp_data = rom[index+1:][::-1]
                break
        if romHeader['romLogoChecksum'] == False or romHeader['romCRCChecksum']:
            temp_data = repairRom(temp_data)
        update_progress(0.5,'Write rom')
        if REMOVE and o_file != name_out:
            os.remove(o_file)
        temp_file=open(name_out,'wb')
        temp_file.write(temp_data)
        temp_file.close()
        update_progress(1,'Finished')
        printInfo("",VERBOSE_MODE,"info")
        elapsedTime=math.floor((time.time() - start_time)*10)/10

        return o_file, bytesToSize(romHeader['romSize']), trim_size, elapsedTime, OUTPUT_PATH

ndslogo = [
    b'\x24',b'\xff',b'\xae',b'\x51',b'\x69',b'\x9a',b'\xa2',b'\x21',b'\x3d',
    b'\x84',b'\x82',b'\x0a',b'\x84',b'\xe4',b'\x09',b'\xad',b'\x11',b'\x24',
    b'\x8b',b'\x98',b'\xc0',b'\x81',b'\x7f',b'\x21',b'\xa3',b'\x52',b'\xbe',
    b'\x19',b'\x93',b'\x09',b'\xce',b'\x20',b'\x10',b'\x46',b'\x4a',b'\x4a',
    b'\xf8',b'\x27',b'\x31',b'\xec',b'\x58',b'\xc7',b'\xe8',b'\x33',b'\x82',
    b'\xe3',b'\xce',b'\xbf',b'\x85',b'\xf4',b'\xdf',b'\x94',b'\xce',b'\x4b',
    b'\x09',b'\xc1',b'\x94',b'\x56',b'\x8a',b'\xc0',b'\x13',b'\x72',b'\xa7',
    b'\xfc',b'\x9f',b'\x84',b'\x4d',b'\x73',b'\xa3',b'\xca',b'\x9a',b'\x61',
    b'\x58',b'\x97',b'\xa3',b'\x27',b'\xfc',b'\x03',b'\x98',b'\x76',b'\x23',
    b'\x1d',b'\xc7',b'\x61',b'\x03',b'\x04',b'\xae',b'\x56',b'\xbf',b'\x38',
    b'\x84',b'\x00',b'\x40',b'\xa7',b'\x0e',b'\xfd',b'\xff',b'\x52',b'\xfe',
    b'\x03',b'\x6f',b'\x95',b'\x30',b'\xf1',b'\x97',b'\xfb',b'\xc0',b'\x85',
    b'\x60',b'\xd6',b'\x80',b'\x25',b'\xa9',b'\x63',b'\xbe',b'\x03',b'\x01',
    b'\x4e',b'\x38',b'\xe2',b'\xf9',b'\xa2',b'\x34',b'\xff',b'\xbb',b'\x3e',
    b'\x03',b'\x44',b'\x78',b'\x00',b'\x90',b'\xcb',b'\x88',b'\x11',b'\x3a',
    b'\x94',b'\x65',b'\xc0',b'\x7C',b'\x63',b'\x87',b'\xf0',b'\x3c',b'\xaf',
    b'\xd6',b'\x25',b'\xe4',b'\x8b',b'\x38',b'\x0a',b'\xac',b'\x72',b'\x21',
    b'\xd4',b'\xf8',b'\x07'
    ]


def Crc16(romHeader):
    CRCTABLE = [
        0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
        0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
        0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
        0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
        0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
        0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
        0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
        0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
        0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
        0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
        0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
        0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
        0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
        0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
        0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
        0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
        0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
        0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
        0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
        0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
        0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
        0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
        0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
        0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
        0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
        0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
        0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
        0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
        0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
        0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
        0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
        0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040
    ]
    crc16 = 0xFFFF

    for index in romHeader:
        crc16 = (crc16 >> 8) ^ CRCTABLE[(crc16 ^ index) & 0xFF]

    return crc16.to_bytes(2,byteorder='little')

def getFileSize(file):
    statinfo = os.stat(file)
    return statinfo.st_size

def repairRom(file):
    romStart=file[:192]
    romLogo=(b"").join(ndslogo)
    romLogoChecksum = b'\x56\xcf'
    romChecksumRom= Crc16(file[:350])
    romEnd=file[352:]

    return romStart+romLogo+romLogoChecksum+romChecksumRom+romEnd


def repairRomOnly(romHeader,OUTPUT_PATH):
    o_file=os.path.join(romHeader['romPath'],romHeader['romFilename'])
    if OUTPUT_PATH == "":
        OUTPUT_PATH = romHeader['romPath']
    if RENAME:
        name_out =os.path.join(OUTPUT_PATH,(" ").join(romHeader['romBannerNameES'].splitlines()[:-1]).replace("\x00","")+".nds")
    else:
        name_out = os.path.join(OUTPUT_PATH,romHeader['romFilename'][:-4]+"_fix.nds")

    start_time = time.time()
    with open(o_file,'rb') as file:
        rom = file.read()
        trim_size=0
        update_progress(0,"Read file")
        if romHeader['romLogoChecksum'] == False or romHeader['romCRCChecksum']:
            update_progress(0.5,'Repair Rom')
            rom =repairRom(rom)

            update_progress(0.5,'Write rom')
            if REMOVE and o_file != name_out:
                os.remove(o_file)
            temp_file=open(name_out,'wb')
            temp_file.write(rom)
            temp_file.close()
            update_progress(1,'Finished')
            printInfo("",VERBOSE_MODE,"info")
        elapsedTime=math.floor((time.time() - start_time)*10)/10

        return o_file, bytesToSize(romHeader['romSize']), elapsedTime, OUTPUT_PATH




def readHeader(file):
    open_file = open(file,'rb')
    rom=open_file.read()
    #try:
    romBannerOffset=int.from_bytes(rom[104:108], 'little')
    romBanner = rom[romBannerOffset:romBannerOffset+2112]
    romSize = getFileSize(file)
    romCalcChecksum = Crc16(rom[:350])
    romLogo = rom[192:348]
    romPath = os.path.split(os.path.abspath(file))
    romBannerNameJP = romBanner[576:832].decode('UTF-8')
    romBannerNameEN = romBanner[832:1088].decode('UTF-8')
    romBannerNameFR = romBanner[1088:1344].decode('UTF-8')
    romBannerNameDE = romBanner[1344:1600].decode('UTF-8')
    romBannerNameIT = romBanner[1600:1856].decode('UTF-8')
    romBannerNameES = romBanner[1856:2112].decode('UTF-8')

    romData ={
        'romPath':romPath[0],
        'romFilename':romPath[1],
        'romName':rom[:12].decode('utf-8'),
        'romCode':rom[12:16].decode('utf-8'),
        'romLicensee':rom[16:18].decode('utf-8'),
        'romUnitcode':rom[18:19],
        'romBannerNameJP':romBannerNameJP,
        'romBannerNameEN':romBannerNameEN,
        'romBannerNameFR':romBannerNameFR,
        'romBannerNameDE':romBannerNameDE,
        'romBannerNameIT':romBannerNameIT,
        'romBannerNameES':romBannerNameES,
        'romSize':romSize,
        'romCRC':rom[350:352],
        'romCalCRC':romCalcChecksum,
        'romCRCChecksum':rom[350:352]==romCalcChecksum,
        'romLogo':romLogo,
        'romLogoChecksum':romLogo == (b"").join(ndslogo),
    }

    open_file.close()

    return romData
    #except:
        #return False



LG = 'es'
ONLYREPAIR = False
ONLYINFO = False
RENAME = False
REMOVE = False
RECURSIVE = False
SELECT_FILES = False
RUN = True
VERBOSE_TYPE = {"short":"Short Mode","all":"All Mode"}
VERBOSE_MODE = ""
INPUT_PATH = ""
OUTPUT_PATH = ""
(console_height, console_width) = get_terminal_size()

args = len(sys.argv)
if args <= 1:
    RUN=False
    printError(text[LG]["HELP"])
else:
    for index, arg in enumerate(sys.argv):
        if arg == "-r":     #Recursive files
            RECURSIVE= True
        if arg == "-s":     #Select Files
            SELECT_FILES=True
        if arg == "-f":
            ONLYREPAIR = True
        if arg == "-v":     #Active verbose
            try:
                if sys.argv[index+1]:
                    try:
                        if VERBOSE_TYPE[sys.argv[index+1]]:
                            VERBOSE_MODE = sys.argv[index+1]
                        else:
                            printError(text[LG]["ERROR_type_verbose_mode"])
                            for type in VERBOSE_TYPE:
                                printError("%s - %s"%(type,VERBOSE_TYPE[type]))
                    except:
                        printError(text[LG]["ERROR_type_verbose_mode"])
                        for type in VERBOSE_TYPE:
                            printError("%s - %s"%(type,VERBOSE_TYPE[type]))

            except:
                printError(text[LG]["ERROR_none_verbose_mode"])
                for type in VERBOSE_TYPE:
                    printError("%s - %s"%(type,VERBOSE_TYPE[type]))

            try:
                if sys.argv[index+2]:
                    try:
                        if text[sys.argv[index+2]]:
                            LG = sys.argv[index+1]
                        else:
                            printError(text[LG]["ERROR_type_language_mode"])
                            for lang in text:
                                printError("%s - %s"%(lang,text[lang]["INFO_name_language"]))
                    except:
                        printError("%s - %s"%(lang,text[lang]["INFO_name_language"]))
            except:
                printInfo(text[LG]["INFO_no_lang_verbose"],VERBOSE_MODE,"all")
        if arg == "-i":     #Custom path input
            try:
                if sys.argv[index+1]:
                    if re.match("^/[^%S]*", sys.argv[index+1]):
                        INPUT_PATH = sys.argv[index+1]+"/"
                    else:
                        INPUT_PATH = ""
            except IndexError:
                INPUT_PATH = ""
        if arg == "-o":     #Custom path output
            try:
                if sys.argv[index+1]:
                    if re.match("^/[^%S]*", sys.argv[index+1]):
                        OUTPUT_PATH = sys.argv[index+1]+"/"
                    else:
                        OUTPUT_PATH = ""
            except IndexError:
                OUTPUT_PATH = ""
        if arg == "-d":     #Remove files after compress
            REMOVE = True
        if arg == "-a":     #Only Info
            ONLYINFO = True
        if arg == "-n":     #Change name file for DATA name
            RENAME = True

def main():
    files = selectFiles("nds")
    total_start_time = time.time()
    for index,rom in enumerate(files):
        romPath = os.path.join(rom['root'],rom['filename'])
        romHeader = readHeader(romPath)

        if romHeader != False:
            if ONLYINFO:

                ARCHIVO=os.path.join(romHeader['romPath'],romHeader['romFilename'])
                PESO= bytesToSize(romHeader['romSize'])
                NOMBREROM =(" ").join(romHeader['romBannerNameES'].splitlines()[:-1])
                CODIGO = romHeader['romCode']
                LOGO = romHeader['romLogoChecksum']
                HEADERCHECK = romHeader['romCRCChecksum']
                romInfo = ARCHIVO,PESO,NOMBREROM,CODIGO,LOGO,HEADERCHECK
                printInfo(text[LG]["INFO_rom_info_only"]%(romInfo),
                          VERBOSE_MODE,
                          "info")
            else:
                if ONLYREPAIR:
                    romResult = repairRomOnly(romHeader,OUTPUT_PATH)
                    printInfo(text[LG]["INFO_rom_info_finish_repair"]%(romResult),
                              VERBOSE_MODE,
                              "info")

                else:
                    romResult = trimRom(romHeader,OUTPUT_PATH)
                    printInfo(text[LG]["INFO_rom_info_finish"]%(romResult),
                              VERBOSE_MODE,
                              "info")
        else:
            printInfo(text[LG]["INFO_rom_info_error_no_rom"]%romPath,
                      VERBOSE_MODE,
                      "info")
        total_elapsed_time =  time.time() - total_start_time


if RUN == True:
    main()
