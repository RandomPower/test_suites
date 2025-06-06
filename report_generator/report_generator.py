# Parser function that reads the outputs of the TESTU01 and NIST Tests and
# checks if they were all passed: if the random bit stream is compliant

#pythons
import os
import re
import math
import natsort
import xlsxwriter
from datetime import datetime

from os import listdir
from os.path import isfile, join

nistPath = 'nist_results/'
nistSubDir = '/AlgorithmTesting/finalAnalysisReport.txt'
failedNist = '*'
rabbitPath = 'rabbit_results/'
introFailedTests = '       Test                          p-value\n'
endFailedTests = ' ----------------------------------------------\n'
passedTests = ' All tests were passed\n'
failedTests = ' All other tests were passed\n'

try:
    cur_dir = os.getcwd().replace('\\', '/').split('/')[-1] + "_"
except:
    cur_dir = ""
report_name = cur_dir + datetime.now().strftime("%Y%m%d_%H%M%S") + "_report"
workbook = xlsxwriter.Workbook(f'{report_name}.xlsx')


wrks1 = workbook.add_worksheet('NIST & Rabbit')

nistDirs = os.listdir(nistPath)
binsList = { x: { 'Nist': None, 'Rabbit': None } for x in nistDirs }

#=========================
# --------- NIST ---------
#=========================
if os.path.isdir(nistPath):
    filenames = list(map(lambda x: nistPath + x + nistSubDir, nistDirs))
    filedata = {f: open(f, 'r') for f in filenames}

    for f in filedata.values():
        lines = f.readlines()
        # fails struct per index:
        # 0: whole failed test string (within stats fluctuations)
        # 1: counter for 0
        # 2: whole failed test string (throw away all file)
        # 3: counter for 2
        # 4: only the failed test names in list
        fails = ['', 0, '', 0, '']
        key = lines[3].split('/')[-1].split('.')[0]
        for line in lines:
            if failedNist in line:
                name = line.split(' ')[-1].split('\n')[0] + '; '
                fails[4] += name
                try:
                    tmpNum1 = int(line.split('   ')[1].split('/')[0])
                except ValueError:
                    tmpNum1 = int(line.split(' * ')[1].split('/')[0])
                tmpNum2 = int(line.split('/')[1].split(' ')[0])

                const = 3.18
                expectation = tmpNum2 * 0.99
                sigma = math.sqrt(tmpNum2*0.99*0.01)

                if tmpNum1 < expectation - sigma * const - 2 or tmpNum1 > expectation + sigma * const + 2:
                    # throw away
                    fails[2] += '\t ' + line
                    fails[3] += 1
                else:
                    # failed within statistical fluctuations
                    fails[0] += '\t ' + line
                    fails[1] += 1
        binsList[key]['Nist'] = fails

        f.close()

#=========================
# -------- RABBIT --------
#=========================
if os.path.isdir(rabbitPath):
    fileList = [join(rabbitPath, f) for f in listdir(rabbitPath) if isfile(join(rabbitPath, f))]
    filedata = {f: open(f, 'r') for f in fileList}
    for f in filedata.values():
        lines = f.readlines()

        # fails struct per index:
        # 0: whole failed test string
        # 1: counter
        # 2: only failed test name
        fails = ['', 0, '']
        key = lines[9].split('/')[-1].split('.')[0]
        try:
            index = lines.index(passedTests)
        except ValueError:
            index = -1

        if index < 0:
            try:
                index = lines.index(introFailedTests)
            except ValueError:
                index = -1

            if index >= 0:
                index += 2
                line = lines[index]

                while line != endFailedTests:
                    name = line.split('      ')[0] + '; '
                    fails[2] += name
                    fails[0] += '\t ' + line
                    fails[1] += 1
                    index += 1
                    line = lines[index]
        else:
            allTestsPassed = True

        binsList[key]['Rabbit'] = fails

        f.close()

# ====================================
# ----------- Excel Report -----------
# ====================================

# Create a format to use in the merged range.
merge_format = workbook.add_format({
'bold': 1,
'border': 1,
'align': 'center',
'valign': 'vcenter',
'font_color': 'blue',
'font_size': 13})

title_format = workbook.add_format({
'bold': 1,
'border': 1,
'align': 'center',
'valign': 'vcenter'})

results_format = workbook.add_format({
'bold': 1,
'align': 'center',
'valign': 'vcenter',
'font_color': 'red'})

# Merge cells
startCol = 0
endCol = 5
wrks1.merge_range(0, startCol, 0, endCol, 'NIST & RABBIT', merge_format)

wrks1.set_column(startCol, endCol, 15)
wrks1.write(1, startCol, 'File', title_format)
wrks1.write(1, startCol + 1, 'NIST Failed Tests', title_format)
wrks1.write(1, startCol + 2, 'NIST Bad Fails', title_format)
wrks1.write(1, startCol + 3, 'NIST Stat. Fails', title_format)
wrks1.write(1, startCol + 4, 'Rabbit Failed Tests', title_format)
wrks1.write(1, startCol + 5, 'Rabbit', title_format)

for j, x in enumerate(binsList):
    wrks1.write(2 + j, startCol, x)
    wrks1.write(2 + j, startCol + 1, binsList[x]['Nist'][4])  #Name
    wrks1.write(2 + j, startCol + 2, binsList[x]['Nist'][3])  #Counter
    wrks1.write(2 + j, startCol + 3, binsList[x]['Nist'][1])  #Counter
    wrks1.write(2 + j, startCol + 4, binsList[x]['Rabbit'][2])#Name
    wrks1.write(2 + j, startCol + 5, binsList[x]['Rabbit'][1])#Counter

wrks1.write(3 + 2, startCol + 7, 'BIN RESULTS:', results_format)
wrks1.write(3 + 3, startCol + 7, 'Golden:', results_format)
wrks1.write(3 + 4, startCol + 7, 'Silver:', results_format)
wrks1.write(3 + 5, startCol + 7, 'Bronze:', results_format)
wrks1.write(3 + 6, startCol + 7, 'Discarded:', results_format)
wrks1.write(3 + 7, startCol + 7, 'TOTAL:', results_format)

totalGold = len([j for j in binsList if not binsList[j]['Nist'][3] and not binsList[j]['Nist'][1] and not binsList[j]['Rabbit'][1]])
wrks1.write(3 + 3, startCol + 8, totalGold)
#condition 1 silver
totalSilver = len([j for j in binsList if not binsList[j]['Nist'][3] and binsList[j]['Nist'][1] == 1 and not binsList[j]['Rabbit'][1]])
#condition 2 silver
totalSilver += len([j for j in binsList if not binsList[j]['Nist'][3] and not binsList[j]['Nist'][1] and binsList[j]['Rabbit'][1] == 1])
wrks1.write(3 + 4, startCol + 8, totalSilver)
#condition 1 bronze
totalBronze = len([j for j in binsList if not binsList[j]['Nist'][3] and binsList[j]['Nist'][1] == 2 and not binsList[j]['Rabbit'][1]])
#condition 2 silver
totalBronze += len([j for j in binsList if not binsList[j]['Nist'][3] and binsList[j]['Nist'][1] == 1 and binsList[j]['Rabbit'][1] == 1])
wrks1.write(3 + 5, startCol + 8, totalBronze)
totalDiscarded = len([j for j in binsList if binsList[j]['Nist'][3] > 0 or binsList[j]['Nist'][1] > 2 or binsList[j]['Rabbit'][1] > 1 or (binsList[j]['Nist'][1] == 2 and binsList[j]['Rabbit'][1] == 1)])
wrks1.write(3 + 6, startCol + 8, totalDiscarded)
wrks1.write(3 + 7, startCol + 8, totalGold + totalSilver + totalBronze + totalDiscarded)

dirs = os.listdir('.')
set_dirs = [d for d in dirs if d.startswith("set")]

wrks2 = workbook.add_worksheet('Crush & Alphabit')

for i, set in enumerate(set_dirs):
    fileList = os.listdir(os.path.join('./', set))
    
    startRow = 0
    endRow = 2
    startCol = i * 3
    endCol = startCol + 2

    wrks2.merge_range(0, startCol, 0, endCol, 'Set ' + str(i+1), merge_format)
    wrks2.merge_range(1, startCol, 1, startCol + 1, 'Crush', title_format)
    wrks2.write(1, startCol + 2, 'Alphabit', title_format)
    wrks2.set_column(startCol+1, endCol, 15)

    nameCrush = '([0-9]|).-output-crush-multi.txt'
    tmp = filter(lambda x: re.match(nameCrush, x), fileList)
    
    filenames = list(map(lambda x: set + '/' + x, tmp))
    filenames = natsort.natsorted(filenames)
    filedata = {f: open(f, 'r') for f in filenames}

    count1 = 0
    for j, f in enumerate(filedata.values()):
        lines = f.readlines()
        fails = ['', 0, '']
        try:
            index = lines.index(passedTests)
        except ValueError:
            index = -1

        if index < 0:
            try:
                index = lines.index(introFailedTests)
            except ValueError:
                index = -1

            if index >= 0:
                index += 2
                line = lines[index]

                while line != endFailedTests:
                    name = line.split('      ')[0] + '; '
                    fails[2] += name
                    fails[0] += '\t ' + line
                    fails[1] += 1
                    index += 1
                    line = lines[index]
        else:
            allTestsPassed = True

        f.close()

        count1 += fails[1]

        endRow = j + 2
        wrks2.write(endRow, startCol, j + 1)
        wrks2.write(endRow, startCol + 1, fails[2])

        #=========================
        # ------- ALPHABIT -------
        #=========================
        nameAlphabit = 'alphabit-output.txt'
        filename = os.path.join(set, nameAlphabit)

        with open(filename) as f:
            lines = f.readlines()

            fails = ['', 0, '']
            try:
                index = lines.index(passedTests)
            except ValueError:
                index = -1

            if index < 0:
                try:
                    index = lines.index(introFailedTests)
                except ValueError:
                    index = -1

                if index >= 0:
                    index += 2
                    line = lines[index]

                    while line != endFailedTests:
                        name = line.split('     ')[0] + '; '
                        fails[2] += name
                        fails[0] += '\t ' + line
                        fails[1] += 1
                        index += 1
                        line = lines[index]
            else:
                allTestsPassed = True

            f.close()

    wrks2.write(2, startCol + 2, fails[2])

    wrks2.write(endRow + 4, startCol, 'TOTAL:', results_format)
    wrks2.write(endRow + 4, startCol + 1, count1)
    wrks2.write(endRow + 4, startCol + 2, fails[1])

    wrks2.write(endRow + 5, startCol, 'RESULT:', results_format)

    if not count1 and not fails[1]:
        wrks2.write(endRow + 5, startCol + 1, 'Golden', results_format)
    elif count1 < 6 and not fails[1]:
        wrks2.write(endRow + 5, startCol + 1, 'Silver', results_format)
    elif count1 <6 and fails[1] == 1:
        wrks2.write(endRow + 5, startCol + 1, 'Bronze', results_format)
    else:
        wrks2.write(endRow + 5, startCol + 1, 'Discarded', results_format)

workbook.close()