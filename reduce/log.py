import json
import sys
import re
import os

class Log:
    def __init__(self, log_filename, exclusions_filename, entries=None, exclusions=None, excluded_sessions=None, good_sessions=None):
        self.log_filename = log_filename
        self.exclusions_filename = exclusions_filename
        self.entries = self.read_entries()
        self.exclusions = self.read_exclusions()
        self.excluded_sessions = self.find_exclusion_sessions()
        self.good_sessions = self.find_good_sessions()
    
    def read_entries(self):
        with open(self.log_filename, 'r') as f:
            log = f.read().splitlines()
        return [json.loads(entry) for entry in log]
    
    def read_exclusions(self):
        with open(self.exclusions_filename, 'r') as f:
            return f.read().splitlines()
    
    def find_exclusion_sessions(self):
        excluded_sessions = []
        for exclusion in self.exclusions:
            for entry in self.entries:
                if entry['eventid'] == 'cowrie.command.input':
                        if re.match(exclusion, entry['message']):
                            excluded_sessions.append((entry['session']))
        return excluded_sessions
    
    def find_good_sessions(self):
        good_sessions = []
        for entry in self.entries:
            if entry['eventid'] == 'cowrie.login.success' and entry['session'] not in self.excluded_sessions:
                good_sessions.append(entry['session'])
        return good_sessions
    
def write_report(log_filename, exclusions, good_sessions, entries, output_dir):
    log_filename = os.path.basename(log_filename)
    with open(output_dir + 'report_' + log_filename, 'w') as f:
        f.write(f'---------exclusions---------\n')
        f.write("\n".join(exclusions))
        f.write(f'\n---------exclusions---------\n\n')

        for session in good_sessions:
            f.write(f'---------{session}---------\n')
            for entry in entries:
                if entry['session'] == session:
                    message = entry['message']
                    if message != []:
                        f.write(entry['message'] + '\n')
            f.write(f'---------{session}---------\n\n')