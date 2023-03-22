import  datetime as dt
from    glob import glob
import  os 
from    time import perf_counter

class Log:
    ''' Handles logging throughout the app. There are 6 levels of logging currently
            - 0: Fatal
            - 1: Error
            - 2: Warn
            - 3: Info
            - 4: Debug
            - 5: Verbose

        Usage: 
            `log = logging.Log(__name__)`
    '''

    log_files_exist = False
    conf = {}

    def __init__(self, src_name: str) -> None:
        self.src_name = src_name

        if not Log.log_files_exist and Log.conf != {}:
            Log.log_files_exist = (self.__check_for_log_folder() and self.__check_for_log_files())
            if not Log.log_files_exist:
                self._init_logs()
                Log.log_files_exist = True
        
    def update_conf(self, conf: dict) -> None:
        ''' Updates the configuration for the logger. 
            This is called from the main app. 
        '''
        Log.conf = conf
        if not Log.log_files_exist:
            Log.log_files_exist = (self.__check_for_log_folder() and self.__check_for_log_files())
            if not Log.log_files_exist:
                self._init_logs()
                Log.log_files_exist = True

    def fatal(self, txt: str) -> None:
        ''' Log level: 0 - FATAL
            This log level is for fatal errors which cause the application to crash or would have
            if they were not in a try: block
        '''
        log = self.__return_log_dict(0,txt)
        self.__log_console_write(log)
        self.__log_file_write(log)
        
    def error(self, txt: str) -> None:
        ''' Log level: 1 - ERROR 
            Use error for significant but recoverable errors
        '''
        log = self.__return_log_dict(1,txt)
        self.__log_console_write(log)
        self.__log_file_write(log)

    def warn(self, txt: str) -> None:
        ''' Log level: 2 - WARN
            Something seems off or some configuration is unsafe
        '''
        log = self.__return_log_dict(2,txt)
        self.__log_console_write(log)
        self.__log_file_write(log)

    def info(self, txt: str) -> None:
        ''' Log level: 3 - INFO
            Things you just might want to know
        '''
        log = self.__return_log_dict(3,txt)
        self.__log_console_write(log)
        self.__log_file_write(log)

    def debug(self, txt: str) -> None:
        ''' Log level: 4 - DEBUG
        
            This should be for development level message. Try not to make it too verbose, 
            there's a level for that.
        '''
        log = self.__return_log_dict(4,txt)
        self.__log_console_write(log)
        self.__log_file_write(log)

    def verbose(self, txt: str) -> None:
        ''' Log level: 5 - VERBOSE      
            Warning: Very noisy
            When you absolutely must know everything that's going on. 
        '''
        log = self.__return_log_dict(5,txt)
        self.__log_console_write(log)
        self.__log_file_write(log)   
    
    def performance(self, func):
        ''' This function is a decorator. At some point it might be worth splitting it into it's own class 
            that way we can include logger performance. 
            Usage:
                `@log.performance`
        '''
        def performance_wrapper(*args, **kwargs):
            ''' Performance testing is an expensive operation and can slow the operation of the system.
                However the knowledge you can gleam from this is worth the expense. But it doesn't need
                to run all the time.  
            ''' 
            if not self.conf.log_performance:
                return func(*args, **kwargs)

            # Setup
            start_time = perf_counter()
            # Function
            result = func(*args, **kwargs)
            # Wrap up
            end_time = perf_counter()
            duration = end_time - start_time
            log = {
                'timestamp': dt.datetime.now(),
                'module': self.src_name,
                'name': func.__name__,
                'duration': duration,
                } 
            

            self.__perf_file_write(log)
            self.__perf_console_write(log)
            return result
        return performance_wrapper


    def _init_logs(self) -> None:
        ''' Ensure that the required folders and files are in place to start logging '''
        if self.__check_for_log_folder() == False:
            os.makedirs(self.conf.log_dir)
        log_list = [self.conf.log_file, self.conf.log_performance_file]
        for log in log_list:
            with open(log, 'a'):
                pass         

    def delete_dot_logs(self) -> None:
        ''' Remove all .log files created '''
        os.remove(f'{self.conf.log_file}')
        os.remove(f'{self.conf.performance_file}')

    # Helper functions

    def __return_log_dict(self, level:int, log_txt:str) -> dict:
        ''' The function helps to reduce error by producing log dictionaries 
            Params: 
                - level: gives the level and text name to the log
                - log_txt: the message to be logged
        '''
        log_names = {0:'FATAL', 1:'ERROR', 2:'WARN', 3:'INFO', 4:'DEBUG', 5:'VERBOSE'}
        return {
            'timestamp': dt.datetime.now(),
            'level': level,
            'name': log_names.get(level),
            'module': self.src_name,
            'log': str(log_txt),
        }

    def __check_for_log_folder(self) -> bool:
        ''' Before we can have a log file there must be a log folder '''
        folder_list = glob(f'{self.conf.current_dir}/**/', recursive=True)
        for folder in folder_list:
            if folder[:-1] == self.conf.log_dir:
                return True
        return False

    def __check_for_log_files(self) -> bool:
        ''' If the log file does not exist, it will may throw and error when accessed. '''
        file_list = glob(f'{self.conf.log_dir}/**/*.*', recursive=True)
        x = [ 1 for file in file_list if file == self.conf.log_file ]
        return sum(x) > 0


    # Output logs
    def __log_console_write(self, log: dict):
        ''' Outputs the log information to terminal. 
            Params:
                - log: a dictionary created from the methods above
        '''
        if log.get('level') <= self.conf.log_console_level:
            log_lines = log.get('log','').split('\n')
            for line in log_lines:
                if line != '': 
                    time = dt.datetime.strftime(log.get('timestamp'), '%H:%M:%S.%f')[:-3]
                    print(f"{time} {log.get('name')}\t{log.get('module'): <35} {line}")
 
    def __log_file_write(self, log: dict): 
        ''' Writes the log to flat file 
        
            Params:
                - log: a dictionary created from the methods above
        '''
        if log.get('level') <= self.conf.log_file_level:
            with open(self.conf.log_file, 'a') as file:
                log_lines = log.get('log','').split('\n')
                for line in log_lines: 
                    file.write(f"{log.get('timestamp')}\t{log.get('name')}\t{log.get('module')}\t{line}\n")

    def __perf_console_write(self, log:dict):
        ''' Outputs the performance log information to terminal.'''
        if self.conf.log_performance_to_console:
            time = dt.datetime.strftime(log.get('timestamp'), '%H:%M:%S.%f')[:-3]
            print(f"{time} PERF\t{log.get('module'): <35} {log.get('name')}\t{log.get('duration'):10.5f} sec")

    def __perf_file_write(self, log:dict):
        ''' Writes the performance log to flat file '''
        if self.conf.log_performance_to_file:
            line = f"{log.get('timestamp')}\t{log.get('module')}\t{log.get('name')}\t{log.get('duration'):10.10f}\n"
            with open(self.conf.log_performance_file, 'a') as file:
                file.write(line)