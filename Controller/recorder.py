import csv

class Recorder(object):
    """
        records data to a file without opening the file repeatedly
    """
    def __init__(self, **kwargs):
        filename = kwargs['filename']
        self.writer = csv.writer(open(filename, 'a'))
        header = kwargs['header']
        assert isinstance(header, list) # must be a list
        self.writer.writerow(header) 
        
    def __call__(self, record):
        self.writer.writerow(record)

