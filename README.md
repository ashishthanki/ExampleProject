This project was created part of task I was given from a company.

The project's objective was to deduplicate the data within the excel file given a set criteria. Each row in the data represents an airline quote that was requested, where the Sale_Flag column either represents 0 or 1, 1 being the a successful sale of the airline quote.

Based on the criteria, the task was to calculate the close ratio of the airline quote data. I have removed the powerpoint presentation from the commit and the company name to avoid others using this project.

The project uses poetry as a package manager with initial data exploration carried out in jupyter notebooks. I then moved these steps into native python files so that it is adaptable to other datasets, furthermore, additional steps can be added to the data pipeline in those files. It also allows us to control parameters and change them for the task at hand, for example, `flight_date_window_size` can be changed to 14 days instead of the default of 28.

