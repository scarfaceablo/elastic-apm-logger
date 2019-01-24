import sys
import logging
from logging.handlers import WatchedFileHandler
from elasticapm import Client
import os
import __main__
import time

logging.getLogger("elasticapm").setLevel(logging.ERROR)

verbose=False
def determine_logger_type():
    # print("determined type")
    try:
        u_in=sys.argv[1]

        if u_in=="-v" or u_in=="--verbose":
            verbose=True
        elif u_in=="-h" or u_in=="--help":
            print("""
  ___   ___  ____ _____   _     ___   ____  ____ _____ ____  
 / _ \ / _ \/ ___|___ /  | |   / _ \ / ___|/ ___| ____|  _ \ 
| | | | | | \___ \ |_ \  | |  | | | | |  _| |  _|  _| | |_) |
| |_| | |_| |___) ___) | | |__| |_| | |_| | |_| | |___|  _ < 
 \__\_\\___/|____|____/  |_____\___/ \____|\____|_____|_| \_\

MAINTAINER: Klemen Kolesa
-h or --help for help
======================LOGGER=================================
        For logging exceptions in QOS3 ETL scripts. 
        And also enables to display errors on std out.
        Arguments:
            1. use none => exception logging is written only to log file
            2. -v or --verbose => exception logging is written to log file & and to stdout
            3. -h or --help => you just pressed this one
        Example:
            in your script:

                Logger.from loggerqos3.logger import Logger
                qos3_logger=Logger(your_log_path)
                try:
                    try something here
                except Error as error:
                    qos3_logger.logger.error(error)

=========APM (Aplication performance monitoring)==============
        Exposes decorator @time_with_apm to simplify timing of functions within a script
        Exposes error, info methods for capturing errors and info messages
            - error
            - info
            - ...
            - More info about elasticapm: https://www.elastic.co/guide/en/apm/agent/python/master/api.html
        
        Initialize:

            # Service name is name of script where you have imported this module
            apm_helper=ApmHelper(url)

            # Custom service name, if you dont want to be equal to the name of script
            apm_helper=ApmHelper(url, "<service_name>")

        Example

            # Transaction name is name of the function you have decorated with @apm_helper.timeit
            @apm_helper.timeit
            def calculate_something():
                ...

        Example with custom naming:

            @apm_helper.timeit_custom_naming("<name>")
            def calculate_something():
                ...
            """)
        elif not u_in!="-v" or  not u_in=="--verbose" or not u_in=="-h" or not u_in=="--help":
            raise ValueError
    except:
        pass

determine_logger_type()

class ApmHelper():
    """
        Exposes decorator @apm_helper.time_with_apm to simplify timing of functions within a script
    """
    def __init__(self, server_url, service_name=None):
        self.server_url=server_url
        self.service_name=service_name

        # in case of APM server not reachable log to file this
        self.apm_server_reachable=True

        self.connect_to_apm_server()

    def connect_to_apm_server(self):
        """
            connect to apm server
        """
        
        try:
            if self.service_name==None:
                self.service_name = str(os.path.basename(__main__.__file__)).split(".")[0]
        except:
            raise ValueError("file name string/service name is incorrect for elastic apm module")


        try:
            self.client = Client({'SERVICE_NAME':self.service_name ,"SERVER_URL":self.server_url})
        except:
            self.apm_server_reachable = False
        finally:
            # continue normallly even if APM server cant be connected 
            pass





class Logger(ApmHelper):
    """
        For logging exceptions in QOS3 ETL scripts. 
        And also enables to display errors on std out.

        Arguments:
            1. use none => exception logging is written only to log file
            2. -v => exception logging is written to log file & and to stdout
        Example:
            in your script:

                Logger.from loggerqos3.logger import Logger
                qos3_logger=Logger(your_log_path)
                try:
                    try something here
                except Error as error:
                    qos3_logger.logger.error(error)
    """
    def __init__(self,logging_dir,server_url, service_name=None):

        super().__init__(server_url, service_name)

        self.logging_dir=logging_dir

        #set logger level
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s')

        # file log handler
        handler_file = WatchedFileHandler(self.logging_dir)
        handler_file.setFormatter(formatter)
        self.logger.addHandler(handler_file)

        if verbose:
            # std out handler
            handler_std_out = logging.StreamHandler(sys.stdout)
            handler_std_out.setFormatter(formatter)
            self.logger.addHandler(handler_std_out)
    
    def error(self, message, exception):
        if type(message) != str:
            raise ValueError("error message must be a string")
        self.logger.error(message)
        self.client.capture_exception()

    def warning(self, message):
        if type(message) != str:
            raise ValueError("warning message must be a string")
        self.logger.info(message)
        self.client.capture_message("WARNING {}".format(message))

    def info(self, message):
        if type(message) != str:
            raise ValueError("info message must be a string")
        self.logger.info(message)
        self.client.capture_message("INFO {}".format(message))
    

    # # # @staticmethod
    def timeit(self,func):
        def wrapper(*args, **kwargs):
            time_start = time.time()
            
            try:
                self.client.begin_transaction(func.__name__)
            except:
                self.logger.error("APM (transaction start) function not timed {}".format(func.__name__))
            finally:
                pass

            result = func(*args, **kwargs)

            try:
                self.client.end_transaction(func.__name__)
            except:
                self.logger.error("APM (transaction end) function not timed {}".format(func.__name__))
            finally:
                pass

            time_end = time.time()
            self.logger.info("Time for: {} is {} seconds".format(func.__name__,time_end-time_start))
            return result
        return wrapper


    # @staticmethod
    def timeit_name(self,func_name):
        """
            - use as decorator
            - user specifies name for this function
        """
        assert isinstance(func_name, str)
        def decorator(func):
            def wrapper(*args, **kwargs):
                time_start = time.time()
                try:
                    self.client.begin_transaction(func_name)
                except:
                    self.logger.error("APM (transaction start) function not timed {}".format(func_name))
                finally:
                    pass

                result = func(*args, **kwargs)

                try:
                    self.client.end_transaction(func_name)
                except:
                    self.logger.error("APM (transaction end) function not timed {}".format(func_name))
                finally:
                    pass
                time_end = time.time()
                self.logger.info("Time for: {} is {} seconds".format(func_name,time_end-time_start))
                return result
            return wrapper
        return decorator

