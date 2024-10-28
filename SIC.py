f = open("2.txt", 'r',encoding="utf-8")
LISTFILE = open("LISTFILE", 'w',encoding="utf-8")
OBJFILE = open("OBJFILE", 'w',encoding="utf-8")

line=f.readline()

label=line[:7].strip().upper()
opcode=line[9:14].strip().upper()
operand=line[17:34].strip().upper()
LOC = 0
Data = {}

DataCount = 0
objectCode = ''
SYMTAB = {}
OPTAB = {
    'ADD' : '18','AND': '40','COMP': '28','DIV': '24',
    'J'   : '3C','JEQ': '30','JGT' : '34','JLT': '38',
    'JSUB': '48','LDA': '00','LDCH': '50','LDL': '08',
    'LDX' : '04','MUL': '20','OR'  : '44','RD' : 'D8',
    'RSUB': '4C','STA': '0C','STCH': '54','STL': '14',
    'STSW': 'E8','STX': '10','SUB' : '1C','TD' : 'E0',
    'TIX' : '2C','WD' : 'DC',
}

def readline():
    global line,label,opcode,operand
    line=f.readline()
    label=line[:7].strip().upper()
    opcode=line[9:14].strip().upper()
    operand=line[17:34].strip().upper()

def ifComment():#過濾註解跟空白行
    global label,opcode,operand
    if (len(label)!=0 and label[0]=='.') or line=='': #( label=='' and opcode==''and operand=='')
        #print(str(LOC) + " this is comment")
        return True
    return False

def storeData():
    global Data,DataCount,opcode,operand,label,LOC,line
    line=line.replace('\n', '').replace('\r', '')
    if ifComment()==True:
        IntermediateData = {'LOC': '', 'label': '', 'opcode': '', 'operand': '','line': line}
    else:
        newline = label.ljust(8) + ' ' + opcode.ljust(6) + '  ' + operand.ljust(18) + line[34:]
        IntermediateData = {'LOC':hex(LOC)[2:].upper().zfill(6), 'label': label, 'opcode': opcode, 'operand': operand ,'line': newline}
    Data[DataCount] = IntermediateData
    DataCount += 1

def readData():
    global Data, DataCount, LOC, label, opcode, operand, line
    LOC = Data[DataCount]['LOC']
    label = Data[DataCount]['label']
    opcode = Data[DataCount]['opcode']
    operand = Data[DataCount]['operand']
    line = Data[DataCount]['line']
    DataCount += 1
#pass1==============================================================
if opcode == "START":
    startAddress = int(operand,16)
    LOC = startAddress
    storeData()
    readline()
else:
    startAddress = 0
    LOC = 0
while opcode != "END":
    LOCTEMP = LOC
    if not ifComment():
        if label !='':
            if label in SYMTAB:
                #error
                print(LOC + " label " + label + "Error: 重複的Label")
            else:
                SYMTAB[label] = hex(LOC)[2:].upper()
        if opcode in OPTAB:
            LOCTEMP += 3
        elif opcode == "WORD":
            LOCTEMP += 3
        elif opcode == "RESW":
            LOCTEMP += 3*int(operand)
        elif opcode == "RESB":
            LOCTEMP += int(operand)
        elif opcode == "BYTE":
            if operand[0] == 'C':
                LOCTEMP += (len(operand)-3)
            elif operand[0] == 'X':
                LOCTEMP += int((len(operand)-3)/2)
            else: #Decimal
                LOCTEMP += int((len(operand)-3)/2)
        else:# error
            print(LOC + ' ' + opcode + "Error: 錯誤的指令")
    storeData()
    LOC = LOCTEMP
    readline()
    #end while============
storeData()
programLength = LOC - startAddress
#end pass1

#pass2
DataCount = 0
readData()

if opcode == "START":
    LISTFILE.write('%6s %-6s %s\n' %( LOC, ' ', line))
    OBJFILE.write('H%-6s%6s%6s\n' % (label, hex(startAddress)[2:].upper().zfill(6), hex(programLength)[2:].upper().zfill(6)))
    readData()
#TEXT RECORD
TEXTLOC = 'T' + LOC
TEXT = ''
while opcode != "END":
    if not ifComment():
        if opcode in OPTAB:
            if opcode == 'AND' or opcode == 'OR':
                objectCode = OPTAB[opcode] + operand.zfill(4)
            elif operand in SYMTAB:
                objectCode = OPTAB[opcode] + str(SYMTAB[operand])
            else:
                objectCode = OPTAB[opcode] + '0000'
                print(LOC + ' ' + operand + ' Error: 搜尋不到此operand')
                #error
        elif opcode == 'BYTE':
            if operand[0] == 'C':
                objectCode = ''
                for i in range(2, len(operand) - 2):
                    objectCode = objectCode + hex(ord(operand[i]))[2:].upper()
            elif operand[0] == 'X':
                objectCode = operand[2:-1]
            else: #Decimal
                objectCode = hex(int(operand))[2:].upper()
        elif  opcode == 'WORD':
            if operand[0] == '-':
                objectCode = 'fff' + hex(4096 - int(operand[1:]))[2:].upper()
            else:
                objectCode = hex(int(operand))[2:].zfill(6)
        else:
            objectCode = ''
            # error
        if len(TEXT) + len(objectCode) > 60 or opcode == 'RESB' or opcode == 'RESW':
            if len(TEXT) > 0:
                OBJFILE.write('%7s%2s%s\n' % (TEXTLOC, hex(int(len(TEXT) / 2))[2:].upper().zfill(2), TEXT))
            TEXTLOC = 'T' + LOC
            TEXT = ''
        TEXT = TEXT + objectCode
        LISTFILE.write('%6s %-6s %s\n' % ( LOC, objectCode, line))
    else:
        objectCode=''
        LISTFILE.write('%6s %-6s %s\n' % ('', objectCode, line))
    readData()
#while end================================================================
OBJFILE.write('%7s%2s%s\n' %( TEXTLOC, hex(int(len(TEXT)/2))[2:].upper().zfill(2), TEXT))
if label == '':
   OBJFILE.write('E%s\n' % (hex(startAddress)[2:].upper().zfill(6)))
else:
    OBJFILE.write('E%s\n' %( hex(SYMTAB[label])[2:].upper().zfill(6)))
LISTFILE.write('%6s %-6s %s\n' % ( LOC, '', line))
#end pass2

print('done')
import os
os.system("PAUSE")
