"""
Parser for TESTU01 and NIST test outputs.
Checks if random bit streams are compliant by analyzing test results.
Generates an Excel report with categorized results.
"""

import getpass
import json
import os
import re
import math
import socket
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import natsort
import xlsxwriter

from crush_lut import crush_test_iterations, crush_subtests_per_iteration


# ============================================================================
# CONSTANTS
# ============================================================================

# Paths
NIST_PATH = 'nist_results/'
NIST_SUBDIR = '/AlgorithmTesting/finalAnalysisReport.txt'
RABBIT_PATH = 'rabbit_results/'
IID_PATH = 'iid_results/'
RUN_INFO_PATH = 'output_logs/run_info.txt'
RUNTESTS_LOG_PATH = 'output_logs/runtests.log'
BINARIES_DIRS = ('binaries', 'bins')
# Folder of the installed test suite, with the VERSION file written by install.sh
DEFAULT_TEST_LIB = '/usr/local/bin/test_lib'

# Test result markers
FAILED_NIST_MARKER = '*'
INTRO_FAILED_TESTS = '       Test                          p-value\n'
END_FAILED_TESTS = ' ----------------------------------------------\n'
PASSED_TESTS = ' All tests were passed\n'

# Statistical constants
NIST_SIGMA_THRESHOLD = 3.18
NIST_EXPECTATION_RATE = 0.99
NIST_FAILURE_RATE = 0.01

# Excel formatting
EXCEL_COL_WIDTH = 15


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class TestResult:
    """Container for test results"""
    def __init__(self):
        self.failed_details = ''
        self.failed_count = 0
        self.failed_names = ''
        
        # NIST-specific
        self.bad_fails_details = ''
        self.bad_fails_count = 0
        
        # IID-specific
        self.iid_validation = None
        self.min_entropy = None


# ============================================================================
# NIST TEST PARSING
# ============================================================================

def parse_nist_results() -> Dict[str, TestResult]:
    """Parse NIST test results from all directories."""
    if not os.path.isdir(NIST_PATH):
        return {}
    
    results = {}
    nist_dirs = os.listdir(NIST_PATH)
    
    for nist_dir in nist_dirs:
        filepath = os.path.join(NIST_PATH, nist_dir, NIST_SUBDIR.lstrip('/'))
        if not os.path.isfile(filepath):
            continue
            
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        # Extract bin name from file
        bin_name = lines[3].split('/')[-1].split('.')[0] if len(lines) > 3 else nist_dir
        
        result = TestResult()
        
        for line in lines:
            if FAILED_NIST_MARKER in line:
                test_name = line.split(' ')[-1].strip() + '; '
                result.failed_names += test_name
                
                # Check if failure is within statistical fluctuations
                if _is_nist_failure_acceptable(line):
                    result.failed_details += '\t ' + line
                    result.failed_count += 1
                else:
                    # Critical failure - discard bin
                    result.bad_fails_details += '\t ' + line
                    result.bad_fails_count += 1
        
        results[bin_name] = result
    
    return results


def _is_nist_failure_acceptable(line: str) -> bool:
    """
    Check if a NIST failure is within acceptable statistical fluctuations.
    Returns True if acceptable, False if critical.
    """
    matches = re.findall(r'(\d+)\s*/\s*(\d+)', line)
    if not matches:
        return True
    
    num_str, den_str = matches[-1]
    num = int(num_str)
    den = int(den_str)
    
    expectation = den * NIST_EXPECTATION_RATE
    sigma = math.sqrt(den * NIST_EXPECTATION_RATE * NIST_FAILURE_RATE)
    
    lower_bound = expectation - sigma * NIST_SIGMA_THRESHOLD - 2
    upper_bound = expectation + sigma * NIST_SIGMA_THRESHOLD + 2
    
    return lower_bound <= num <= upper_bound


# ============================================================================
# RABBIT TEST PARSING
# ============================================================================

def parse_rabbit_results() -> Dict[str, TestResult]:
    """Parse Rabbit test results from all files."""
    if not os.path.isdir(RABBIT_PATH):
        return {}
    
    results = {}
    file_list = [f for f in Path(RABBIT_PATH).iterdir() if f.is_file()]
    
    for filepath in file_list:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Extract bin name
        bin_name = lines[9].split('/')[-1].split('.')[0] if len(lines) > 9 else filepath.stem
        
        result = TestResult()
        result.failed_details, result.failed_count, result.failed_names = \
            _parse_test_failures(lines)
        
        results[bin_name] = result
    
    return results


# ============================================================================
# IID TEST PARSING
# ============================================================================

def parse_iid_results() -> Dict[str, TestResult]:
    """Parse IID test results from all directories."""
    if not os.path.isdir(IID_PATH):
        return {}
    
    results = {}
    iid_dirs = os.listdir(IID_PATH)
    
    for iid_dir in iid_dirs:
        bin_name = iid_dir.split('@')[0]
        log_path = os.path.join(IID_PATH, iid_dir, f'{iid_dir}.log')
        
        if not os.path.isfile(log_path):
            continue
        
        result = TestResult()
        
        with open(log_path, 'r') as f:
            for line in f:
                if "IID assumption validated" in line:
                    result.iid_validation = "VALIDATED"
                elif "IID assumption rejected" in line:
                    result.iid_validation = "REJECTED"
                elif "RaP min-entropy" in line:
                    result.min_entropy = line.split("INFO     ")[-1]
        
        results[bin_name] = result
    
    return results


# ============================================================================
# CRUSH & ALPHABIT TEST PARSING
# ============================================================================

def parse_crush_results(set_dir: str) -> Tuple[List[TestResult], int]:
    """
    Parse Crush test results from a set directory.
    Returns list of test results and total failure count.
    """
    file_pattern = r'([0-9]|).-output-crush-multi.txt'
    file_list = [f for f in os.listdir(set_dir) if re.match(file_pattern, f)]
    file_list = natsort.natsorted(file_list)
    
    results = []
    total_failures = 0
    
    for filename in file_list:
        filepath = os.path.join(set_dir, filename)
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        result = TestResult()
        result.failed_details, result.failed_count, result.failed_names = \
            _parse_test_failures(lines)
        
        results.append(result)
        total_failures += result.failed_count
    
    return results, total_failures


def parse_alphabit_results(set_dir: str) -> TestResult:
    """Parse Alphabit test results from a set directory."""
    filepath = os.path.join(set_dir, 'alphabit-output.txt')
    
    if not os.path.isfile(filepath):
        return TestResult()
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    result = TestResult()
    # Alphabit uses 5 spaces as separator instead of 6
    result.failed_details, result.failed_count, result.failed_names = \
        _parse_test_failures(lines, separator='     ')
    
    return result


def _parse_test_failures(lines: List[str], separator: str = '      ') -> Tuple[str, int, str]:
    """
    Generic parser for test failures from TestU01 output format.
    Returns: (failed_details, failed_count, failed_names)
    
    Args:
        lines: Output file lines
        separator: String of spaces separating test name from p-value (default: 6 spaces)
    """
    if PASSED_TESTS in lines:
        return '', 0, ''
    
    try:
        index = lines.index(INTRO_FAILED_TESTS)
    except ValueError:
        return '', 0, ''
    
    failed_details = ''
    failed_count = 0
    failed_names = ''
    
    index += 2
    
    while index < len(lines) and lines[index] != END_FAILED_TESTS:
        line = lines[index]
        # Split by whitespace gap to preserve full test name
        test_name = line.split(separator)[0] + '; '
        
        failed_names += test_name
        failed_details += '\t ' + line
        failed_count += 1
        index += 1
    
    return failed_details, failed_count, failed_names


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def deduplicate_test_names(failed_names: str) -> str:
    """
    Deduplicate test names and show count for repeated tests.
    Input: "MaxOft, t = 20; MaxOft, t = 20; MaxOft AD, t = 20; MaxOft AD, t = 20;"
    Output: "MaxOft, t = 20 (2x); MaxOft AD, t = 20 (2x)"
    """
    if not failed_names:
        return ''
    
    # Split by semicolon and clean up
    tests = [t.strip() for t in failed_names.split(';') if t.strip()]
    
    # Count occurrences
    test_counts = {}
    for test in tests:
        test_counts[test] = test_counts.get(test, 0) + 1
    
    # Format output
    result = []
    for test, count in test_counts.items():
        if count > 1:
            result.append(f"{test} ({count}x)")
        else:
            result.append(test)
    
    return '; '.join(result)


# ============================================================================
# RESULT CATEGORIZATION
# ============================================================================

def categorize_bin_results(bins: Dict[str, Dict[str, TestResult]]) -> Dict[str, int]:
    """
    Categorize bins into Gold, Silver, Bronze, and Discarded.
    """
    counts = {'gold': 0, 'silver': 0, 'bronze': 0, 'discarded': 0}
    
    for bin_name, tests in bins.items():
        nist = tests['Nist']
        rabbit = tests['Rabbit']
        
        # Gold: no failures at all
        if not nist.bad_fails_count and not nist.failed_count and not rabbit.failed_count:
            counts['gold'] += 1
        
        # Silver: 1 NIST statistical fail OR 1 Rabbit fail
        elif (not nist.bad_fails_count and nist.failed_count == 1 and not rabbit.failed_count) or \
             (not nist.bad_fails_count and not nist.failed_count and rabbit.failed_count == 1):
            counts['silver'] += 1
        
        # Bronze: 2 NIST statistical fails OR (1 NIST + 1 Rabbit)
        elif (not nist.bad_fails_count and nist.failed_count == 2 and not rabbit.failed_count) or \
             (not nist.bad_fails_count and nist.failed_count == 1 and rabbit.failed_count == 1):
            counts['bronze'] += 1
        
        # Discarded: everything else
        else:
            counts['discarded'] += 1
    
    return counts


def categorize_set_result(crush_failures: int, alphabit_failures: int) -> str:
    """Categorize a set based on Crush and Alphabit failures."""
    if crush_failures == 0 and alphabit_failures == 0:
        return 'Golden'
    elif crush_failures < 6 and alphabit_failures == 0:
        return 'Silver'
    elif crush_failures < 6 and alphabit_failures == 1:
        return 'Bronze'
    else:
        return 'Discarded'


# ============================================================================
# EXCEL REPORT GENERATION
# ============================================================================

def create_excel_formats(workbook: xlsxwriter.Workbook) -> Dict[str, xlsxwriter.format.Format]:
    """Create and return all Excel cell formats."""
    return {
        'merge': workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'blue',
            'font_size': 13
        }),
        'title': workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        }),
        'results': workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'red'
        })
    }


def write_nist_rabbit_sheet(worksheet: xlsxwriter.worksheet.Worksheet,
                            bins: Dict[str, Dict[str, TestResult]],
                            formats: Dict[str, xlsxwriter.format.Format]) -> None:
    """Write the NIST & Rabbit results worksheet."""
    # Header
    worksheet.merge_range(0, 0, 0, 5, 'NIST & RABBIT', formats['merge'])
    
    # Column setup
    worksheet.set_column(0, 5, EXCEL_COL_WIDTH)
    headers = ['File', 'NIST Failed Tests', 'NIST Bad Fails', 
               'NIST Stat. Fails', 'Rabbit Failed Tests', 'Rabbit']
    
    for col, header in enumerate(headers):
        worksheet.write(1, col, header, formats['title'])
    
    # Data rows
    for row, (bin_name, tests) in enumerate(bins.items(), start=2):
        worksheet.write(row, 0, bin_name)
        worksheet.write(row, 1, tests['Nist'].failed_names)
        worksheet.write(row, 2, tests['Nist'].bad_fails_count)
        worksheet.write(row, 3, tests['Nist'].failed_count)
        worksheet.write(row, 4, tests['Rabbit'].failed_names)
        worksheet.write(row, 5, tests['Rabbit'].failed_count)
    
    # Summary statistics
    counts = categorize_bin_results(bins)
    
    summary_row = 5
    worksheet.write(summary_row, 8, 'BIN RESULTS:', formats['results'])
    worksheet.write(summary_row + 1, 8, 'Golden:', formats['results'])
    worksheet.write(summary_row + 2, 8, 'Silver:', formats['results'])
    worksheet.write(summary_row + 3, 8, 'Bronze:', formats['results'])
    worksheet.write(summary_row + 4, 8, 'Discarded:', formats['results'])
    worksheet.write(summary_row + 5, 8, 'TOTAL:', formats['results'])
    
    worksheet.write(summary_row + 1, 9, counts['gold'])
    worksheet.write(summary_row + 2, 9, counts['silver'])
    worksheet.write(summary_row + 3, 9, counts['bronze'])
    worksheet.write(summary_row + 4, 9, counts['discarded'])
    worksheet.write(summary_row + 5, 9, sum(counts.values()))


def write_detailed_analysis_sheet(worksheet: xlsxwriter.worksheet.Worksheet,
                                  set_dirs: List[str],
                                  formats: Dict[str, xlsxwriter.format.Format]) -> None:
    """Write the detailed analysis worksheet with intelligent test summaries."""
    for i, set_dir in enumerate(set_dirs):
        start_col = i * 7
        
        # Header
        worksheet.merge_range(0, start_col, 0, start_col + 6, 
                            f'Set {i + 1} - Crush & Alphabit', formats['merge'])
        
        # Column headers
        worksheet.write(1, start_col, 'Test ID', formats['title'])
        worksheet.write(1, start_col + 1, 'Iterations', formats['title'])
        worksheet.write(1, start_col + 2, 'Subtests', formats['title'])
        worksheet.write(1, start_col + 3, 'Failures', formats['title'])
        worksheet.write(1, start_col + 4, 'Rate %', formats['title'])
        worksheet.write(1, start_col + 5, 'Status', formats['title'])
        worksheet.write(1, start_col + 6, 'Failed Tests (unique)', formats['title'])
        
        worksheet.set_column(start_col, start_col, 10)
        worksheet.set_column(start_col + 1, start_col + 3, 12)
        worksheet.set_column(start_col + 4, start_col + 4, 10)
        worksheet.set_column(start_col + 5, start_col + 5, 15)
        worksheet.set_column(start_col + 6, start_col + 6, 30)
        
        # Parse results
        crush_results, total_crush_failures = parse_crush_results(set_dir)
        alphabit_result = parse_alphabit_results(set_dir)
        
        # Analyze and write Crush results
        for j, result in enumerate(crush_results):
            row = j + 2
            test_id = j + 1
            iterations = crush_test_iterations.get(test_id, 1)
            subtests_per_iteration = crush_subtests_per_iteration.get(test_id, 1)
            
            # Calculate metrics
            if isinstance(iterations, int) and iterations > 0:
                total_possible_failures = iterations * subtests_per_iteration
                
                if total_possible_failures > 0:
                    failure_rate = (result.failed_count / total_possible_failures) * 100
                else:
                    # All tests passed (subtests_per_iteration might be 0 for passed tests)
                    failure_rate = 0.0
                
                # Determine status
                if result.failed_count == 0:
                    status = 'PASSED'
                elif failure_rate >= 80:
                    status = 'CRITICAL'
                elif failure_rate >= 50:
                    status = 'HIGH'
                elif failure_rate >= 20:
                    status = 'MEDIUM'
                else:
                    status = 'LOW'
            else:
                failure_rate = 0
                status = 'N/A'
            
            # Deduplicate test names
            unique_tests = deduplicate_test_names(result.failed_names)
            
            worksheet.write(row, start_col, test_id)
            worksheet.write(row, start_col + 1, iterations)
            worksheet.write(row, start_col + 2, subtests_per_iteration)
            worksheet.write(row, start_col + 3, result.failed_count)
            worksheet.write(row, start_col + 4, f'{failure_rate:.1f}%')
            worksheet.write(row, start_col + 5, status)
            worksheet.write(row, start_col + 6, unique_tests)
        
        # Alphabit analysis
        end_row = len(crush_results) + 2
        worksheet.write(end_row + 1, start_col, 'Alphabit', formats['title'])
        worksheet.write(end_row + 1, start_col + 3, alphabit_result.failed_count)
        
        if alphabit_result.failed_count == 0:
            alphabit_status = 'PASSED'
        elif alphabit_result.failed_count == 1:
            alphabit_status = 'WARNING'
        else:
            alphabit_status = 'FAILED'
        
        worksheet.write(end_row + 1, start_col + 5, alphabit_status)
        
        # Deduplicated Alphabit failures
        unique_alphabit = deduplicate_test_names(alphabit_result.failed_names)
        worksheet.write(end_row + 1, start_col + 6, unique_alphabit)
        
        # Overall summary
        worksheet.write(end_row + 3, start_col, 'OVERALL', formats['results'])
        worksheet.write(end_row + 3, start_col + 1, 'Crush Total:', formats['results'])
        worksheet.write(end_row + 3, start_col + 3, total_crush_failures)
        
        category = categorize_set_result(total_crush_failures, alphabit_result.failed_count)
        worksheet.write(end_row + 4, start_col + 1, 'Category:', formats['results'])
        worksheet.write(end_row + 4, start_col + 3, category, formats['results'])


def write_iid_sheet(worksheet: xlsxwriter.worksheet.Worksheet,
                   bins: Dict[str, Dict[str, TestResult]],
                   formats: Dict[str, xlsxwriter.format.Format]) -> None:
    """Write the IID Details worksheet."""
    # Headers
    worksheet.set_column(0, 2, EXCEL_COL_WIDTH)
    worksheet.write(0, 0, 'File', formats['title'])
    worksheet.write(0, 1, 'IID', formats['title'])
    worksheet.write(0, 2, 'Min Entropy', formats['title'])
    
    # Data rows
    for row, (bin_name, tests) in enumerate(bins.items(), start=1):
        worksheet.write(row, 0, bin_name)
        
        iid = tests.get('IID')
        if iid and iid.iid_validation is not None:
            worksheet.write(row, 1, iid.iid_validation)
            worksheet.write(row, 2, iid.min_entropy or '')
        else:
            worksheet.write(row, 1, "No IID test performed")



# ============================================================================
# RUN INFORMATION (Info sheet)
# ============================================================================

def read_key_values(path: str) -> Dict[str, str]:
    """Read a file of key=value lines (missing file: empty dictionary)."""
    values = {}
    try:
        with open(path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.rstrip('\n').split('=', 1)
                    values[key.strip()] = value.strip()
    except OSError:
        pass
    return values


def test_lib_dir() -> str:
    """Folder of the installed test suite: the folder of this executable when it is the installed binary."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.environ.get('TEST_LIB_DIR', DEFAULT_TEST_LIB)


def read_run_times() -> Tuple[Optional[str], Optional[str]]:
    """Start and end of the tests, from the last run recorded in output_logs/runtests.log."""
    start, end = None, None
    try:
        with open(RUNTESTS_LOG_PATH, 'r') as f:
            for line in f:
                if line.endswith('- Starting runtests.sh\n'):
                    start, end = line.split(' - ')[0], None
                elif line.endswith('- Tests finished\n'):
                    end = line.split(' - ')[0]
    except OSError:
        pass
    return start, end


def find_bin_files() -> List[str]:
    """Paths of the tested .bin files, in natural order."""
    for folder in BINARIES_DIRS:
        if os.path.isdir(folder):
            return natsort.natsorted(os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.bin'))
    return []


def read_iid_configurations() -> Dict[str, dict]:
    """IID configuration (configuration.json) of the last IID run of each file, by bin name."""
    configs = {}
    if not os.path.isdir(IID_PATH):
        return configs
    # The folders are named <bin name>@<date>_<time>: in sorted order the last run of a file comes last
    for iid_dir in sorted(os.listdir(IID_PATH)):
        try:
            with open(os.path.join(IID_PATH, iid_dir, 'configuration.json'), 'r') as f:
                configs[iid_dir.split('@')[0]] = json.load(f)
        except (OSError, ValueError):
            continue
    return configs


def read_nist_parameters() -> Tuple[Optional[int], Optional[int]]:
    """Stream length and number of streams of the NIST tests, from the freq.txt file of the first file."""
    if not os.path.isdir(NIST_PATH):
        return None, None
    for nist_dir in natsort.natsorted(os.listdir(NIST_PATH)):
        try:
            with open(os.path.join(NIST_PATH, nist_dir, 'AlgorithmTesting', 'freq.txt'), 'r') as f:
                lengths = [int(m.group(1)) for m in re.finditer(r'BITSREAD = (\d+)', f.read())]
        except OSError:
            continue
        if lengths:
            return lengths[0], len(lengths)
    return None, None


def collect_run_info(label: str, report_name: str, n_sets: int) -> Dict[str, object]:
    """Collect everything shown in the Info sheet."""
    try:
        user = getpass.getuser()
    except Exception:
        user = ''
    start, end = read_run_times()
    duration = ''
    if start and end:
        seconds = int((datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                       - datetime.strptime(start, '%Y-%m-%d %H:%M:%S')).total_seconds())
        duration = f'{seconds // 3600}h {seconds % 3600 // 60:02d}m {seconds % 60:02d}s'
    nist_length, nist_streams = read_nist_parameters()
    iid_configs = read_iid_configurations()
    iid_any = next(iter(iid_configs.values()), {})
    return {
        'run': [
            ('Label', label),
            ('Report', f'{report_name}.xlsx'),
            ('Workspace', os.getcwd()),
            ('Server', socket.gethostname()),
            ('User', user),
            ('Tests started', start or ''),
            ('Tests finished', end or ''),
            ('Duration', duration),
            ('Report created', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ],
        'versions': list(read_key_values(os.path.join(test_lib_dir(), 'VERSION')).items()),
        'parameters': [
            ('NIST stream length (bits)', nist_length if nist_length is not None else ''),
            ('NIST streams per file', nist_streams if nist_streams is not None else ''),
            ('IID backend', iid_any.get('backend', '')),
            ('IID symbols', iid_any.get('nist', {}).get('n_symbols', '')),
            ('IID permutations', iid_any.get('nist', {}).get('n_permutations', '')),
            ('TestU01 sets (Crush and Alphabit)', n_sets),
        ],
        'files': [
            (os.path.basename(path), os.path.getsize(path),
             iid_configs.get(Path(path).stem, {}).get('input_file_digest', ''),
             iid_configs.get(Path(path).stem, {}).get('seed', ''))
            for path in find_bin_files()
        ],
    }


def write_info_sheet(worksheet: xlsxwriter.worksheet.Worksheet,
                     info: Dict[str, object],
                     formats: Dict[str, xlsxwriter.format.Format]) -> None:
    """Write the Info worksheet: label, workspace, times, versions, parameters and tested files."""
    worksheet.set_column(0, 0, 34)
    worksheet.set_column(1, 1, 60)
    worksheet.set_column(2, 3, 25)
    row = 0
    for title, items in (('RUN', info['run']), ('VERSIONS', info['versions']), ('PARAMETERS', info['parameters'])):
        worksheet.merge_range(row, 0, row, 1, title, formats['merge'])
        row += 1
        if not items:
            worksheet.write(row, 0, 'not available')
            row += 1
        for key, value in items:
            worksheet.write(row, 0, key, formats['title'])
            worksheet.write(row, 1, value)
            row += 1
        row += 1

    worksheet.merge_range(row, 0, row, 3, 'TESTED FILES', formats['merge'])
    row += 1
    for col, header in enumerate(('File', 'Size (bytes)', 'SHA-256', 'IID seed')):
        worksheet.write(row, col, header, formats['title'])
    for name, size, digest, seed in info['files']:
        row += 1
        worksheet.write(row, 0, name)
        worksheet.write(row, 1, size)
        worksheet.write(row, 2, digest)
        # Seeds are 64-bit integers: written as text, Excel would round them
        worksheet.write_string(row, 3, str(seed))

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def generate_report() -> None:
    """Main function to generate the complete Excel report."""
    # Generate report filename
    try:
        current_dir = os.getcwd().replace('\\', '/').split('/')[-1] + "_"
    except:
        current_dir = ""
    
    # Optional label given with raptests -l (e.g. the board ID), at the start of the name.
    # No date in the name: the folder name often is a date already, and the Info sheet has the
    # date of the report. Creating the report again in the same folder replaces it.
    label = read_key_values(RUN_INFO_PATH).get('label', '')
    label_prefix = re.sub(r'[^A-Za-z0-9._-]+', '_', label) + '_' if label else ''
    report_name = f'{label_prefix}{current_dir}report'
    
    # Parse all test results
    nist_results = parse_nist_results()
    rabbit_results = parse_rabbit_results()
    iid_results = parse_iid_results()
    
    # Combine results by bin
    all_bins = set(nist_results.keys()) | set(rabbit_results.keys()) | set(iid_results.keys())
    bins = {}
    
    for bin_name in all_bins:
        bins[bin_name] = {
            'Nist': nist_results.get(bin_name, TestResult()),
            'Rabbit': rabbit_results.get(bin_name, TestResult()),
            'IID': iid_results.get(bin_name, TestResult())
        }
    
    # Find set directories
    set_dirs = [d for d in os.listdir('.') if d.startswith('set') and os.path.isdir(d)]
    
    # Create Excel workbook
    workbook = xlsxwriter.Workbook(f'{report_name}.xlsx')
    formats = create_excel_formats(workbook)
    
    # Generate worksheets. Info is the first one, so it is the sheet shown when the report is opened
    wrks_info = workbook.add_worksheet('Info')
    write_info_sheet(wrks_info, collect_run_info(label, report_name, len(set_dirs)), formats)

    wrks1 = workbook.add_worksheet('NIST & Rabbit')
    write_nist_rabbit_sheet(wrks1, bins, formats)
    
    if set_dirs:
        wrks_analysis = workbook.add_worksheet('Crush & Alphabit')
        write_detailed_analysis_sheet(wrks_analysis, set_dirs, formats)
    
    wrks3 = workbook.add_worksheet('IID Details')
    write_iid_sheet(wrks3, bins, formats)
    
    workbook.close()
    print(f"Report generated: {report_name}.xlsx")


if __name__ == '__main__':
    generate_report()