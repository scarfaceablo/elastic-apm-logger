Logger and Elastic APM client at the same time:
Example:
 * try:
	func()
   except Error as err:
	apm_logger.error(err)
	
	
