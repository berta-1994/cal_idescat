# WEEKLY IDESCAT EMAIL

The Statistical Institute of Catalonia (in Catalan: Institut d'Estadística de Catalunya, usually referred to by its acronym IDESCAT) is the official body responsible for collecting, processing, and disseminating statistics in the autonomous community of Catalonia, Spain. The institute comes under the Department of the Economy and Finances of the Generalitat de Catalunya (Government of Catalonia). Its offices are on Via Laietana, Barcelona. It operates under the Ministry of Economy and Finance of the Catalan government and provides data essential for regional planning, economic analysis, and decision-making across various sectors. (wikipedia)

Every week idescat publishes results and statistics which are relevant for my job. 
I am a forgetful person and I although I should check what elements will be published this week, I often forget. 

This code creates a weekly email with the publications from idescat and sends it to a list of contacts. 

The directory contains the following folders:
*.env - containing the email and password to ba able to send emails from a python script
* .gitignore.txt
* requirements.txt with the libraries used
* idescat_calendar - python script 

The code is divided in 3 main parts

Part 1 - Defines the current week to extract from the Idescat Website
Part 2 - Retrieving information from Idescat using their publicly available API
Part 3 - Setting an email to receive the information periodically.
