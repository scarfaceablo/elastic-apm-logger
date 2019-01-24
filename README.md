## Logger and Elastic APM client at the same time:
### Example:


```
from apm_logger import Logger
logger = Logger(file_path_to_log, apm_server_url)
```
```
try:
	func()
except Error as err:
	apm_logger.error(err)
```
