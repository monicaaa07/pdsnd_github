import time
import pandas as pd
import numpy as np
from statistics import mode
import pprint

# dict to get the right filename based on selection
CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

# lists for months and week_days to select name based on position (index)
months = ['all','january', 'february', 'march', 'april', 'may', 'june']
week_days =  ['all','monday','tuesday','wednesday','thursday','friday','saturday','sunday']

def invalid_input_helper(options, option):
    """
    Helper function for prompt to reenter input when wrong input entered
    Args:
        (list) options - list of valid input options as strings available
        (str)  option  - option entered by the user
    Returns:
        (str) option - valid input
    """
    while option not in options:
        # unpack the "options" list to print all the options
        option = input(("Invalid Input. Please enter one of the following ; "+"{}, "*(len(options)-1)+"{}: ").format(*options)).lower()
    return option

def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.
    Returns:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """
    print('Hello! Let\'s explore some US bikeshare data!')
    try:
        # get user input for city (chicago, new york city, washington). HINT: Use a while loop to handle invalid inputs
        city = input("\nEnter the City (chicago, new york city, washington): ").lower()
        # if cities not chicago, nyc or washignton, enter again
        city = invalid_input_helper(CITY_DATA.keys(), city)

        # check if user wants to filter by month, day or both?
        filter_by = input("\nWould you like to filter by month, day, both or none: ").lower()
        # if user enters invalid option, use helper to run a while loop until user enters the right option
        filter_by = invalid_input_helper(['month','day','both','none'],filter_by)

        # set month filter and/or day filter based on user choice.
        # If user doen't want a filter set both as 0
        if filter_by == 'month':
            month_filter,day_filter = 1,0
        elif filter_by == 'day':
            month_filter,day_filter = 0,1
        elif filter_by == 'none':
            month_filter,day_filter = 0,0
        else:
            month_filter,day_filter = 1,1

        if month_filter:
            # get user input for month (all, january, february, ... , june)
            month = input("\nEnter the month (all, january, february, ... , june): ").lower()
            month = invalid_input_helper(months, month)
        else:
            month = 'all'

        if day_filter:
            # get user input for day of week (all, monday, tuesday, ... sunday)
            day = input("\nEnter the day of week (all, monday, tuesday, ... sunday): ").lower()
            day = invalid_input_helper(week_days, day)
        else:
            day = 'all'
        print('-'*70)

        # Display choices back to user. If incorrect allow user to restart the program
        print("\nYour choices for viewing statistics are \n\tCity: {} \n\tMonth: {} \n\tDay: {}\nIf incorrect, restart the program now by pressing ctrl+c. Else do nothing".format(city.title(), month.title(), day.title()))
        print('-'*70)
        # Sleep timer to allow user to enter choice
        time.sleep(3)
        return city, month, day
    except Exception as e:
        print("Input not recognized. Error: ",e)


def load_data(city, month, day):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        city_data_dataframe - Pandas DataFrame containing city data filtered by month and day
    """
    try:
        # load data file into a dataframe
        city_data_dataframe = pd.read_csv(CITY_DATA[city])

        # convert the Start Time column to datetime
        city_data_dataframe['Start Time'] = pd.to_datetime(city_data_dataframe['Start Time'])

        # extract month and day of week from Start Time to create new columns
        city_data_dataframe['month'] = city_data_dataframe['Start Time'].dt.month
        city_data_dataframe['day_of_week'] = city_data_dataframe['Start Time'].dt.weekday

        # filter by month if applicable
        if month != 'all':
            # use the index of the months list to get the corresponding int
            month = months.index(month)
            # filter by month to create the new dataframe
            city_data_dataframe = city_data_dataframe[city_data_dataframe['month'] == month]

        # filter by day of week if applicable
        if day != 'all':
            day = week_days.index(day)
            # filter by day of week to create the new dataframe
            city_data_dataframe = city_data_dataframe[city_data_dataframe['day_of_week'] == day-1]

        return city_data_dataframe

    except KeyError as e:
        print('Incorrect File Format. Columns "Start Time","month","day_of_week" must be present. '.format(e))
    except Exception as e:
        print("Raised Error: ",e)


def preprocessing(city_data_dataframe, city):
    """
    Renames columns, change to approporiate datatypes
    Args:
        city_data_dataframe - DataFrame to be pre-processed
    Returns:
        city_data_dataframe - cleaner DataFrame
    """
    try:
        city_data_dataframe.fillna(0,inplace = True)
        #changing column datatypes
        city_data_dataframe['End Time'] = pd.to_datetime(city_data_dataframe['End Time'])

        # washington.csv is missing 'Birth Year' column. Adding a dummy column if input file is washington's
        if city == 'washington':
            city_data_dataframe['Birth Year'] = np.zeros(len(city_data_dataframe))
        city_data_dataframe['Birth Year'] = pd.Series(map(lambda x:int(x),city_data_dataframe['Birth Year']))

        # renaming column names to be more readable
        city_data_dataframe.rename(columns = {'Unnamed: 0':'Trip Id'},inplace = True)
        return city_data_dataframe

    except KeyError as e:
        print('Incorrect File Format. Columns "End Time","Birth Year" must be present. '.format(e))
    except Exception as e:
        print("Raised Error: ",e)

def view_data(city_data_dataframe):
    """
    Allows user to view data five rows at a time. User can exit if done viewing data
    """
    try:
        print("\nSelected data contains {} rows.".format(len(city_data_dataframe)))
        view_option = input("\nWould you like to view first 5 rows of data? Enter yes or no: ").lower()
        view_option = invalid_input_helper(['yes','no'], view_option)
        # sindex is start index and lindex is last index incremented by 5 to display 5 rows to the user
        sindex, lindex = 0, 5
        pp = pprint.PrettyPrinter(compact=True)
        while view_option == 'yes':
            pp.pprint(city_data_dataframe[sindex:lindex].to_dict(orient='records'))
            sindex, lindex = lindex, lindex + 5
            view_option = input("\nWould you like to view next 5 rows of data? Enter yes or no: ").lower()
            view_option = invalid_input_helper(['yes','no'], view_option)
        print('-'*70)
    except Exception as e:
        print("Raised Error: ",e)

def time_stats(city_data_dataframe):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    # Sleep timer to display statistics orderly and not all at once
    time.sleep(3)
    start_time = time.time()

    try:
        # display the most common month
        busiest_month_index = city_data_dataframe['month'].mode()[0]
        print("Busiest Month was {}".format(months[busiest_month_index].title()))

        # display the most common day of week
        busiest_dow_index = city_data_dataframe['day_of_week'].mode()[0]
        print("Busiest Day of Week was {}".format(week_days[busiest_dow_index].title()))

        # display the most common start hour
        busiest_start_hour = city_data_dataframe['Start Time'].dt.hour.mode()[0]
        print("Busiest Start Hour was {}:00".format(busiest_start_hour))

        print("\nThis took %s seconds." % (time.time() - start_time))
        print('-'*40)

    except Exception as e:
        print("Raised Error: ",e)


def station_stats(city_data_dataframe):
    """Displays statistics on the most popular stations and trip."""
    print('\nCalculating The Most Popular Stations and Trip...\n')
    # Sleep timer to display statistics orderly and not all at once
    time.sleep(3)
    start_time = time.time()

    try:
        # display most commonly used start station
        popular_start = city_data_dataframe['Start Station'].mode()[0]
        print("Most popular Start Station was {}".format(popular_start))

        # display most commonly used end station
        popular_end = city_data_dataframe['End Station'].mode()[0]
        print("Most popular End Station was {}".format(popular_end))

        # display most frequent combination of start station and end station trip
        routes = city_data_dataframe['Start Station'] + " : " + city_data_dataframe['End Station']
        popular_route = routes.mode()[0]
        print("Most popular Route was {} to {}".format(*popular_route.split(':')))

        print("\nThis took %s seconds." % (time.time() - start_time))
        print('-'*40)

    except KeyError as e:
        print('Incorrect File Format. Columns "Start Station","End Station" must be present.'.format(e))
    except Exception as e:
        print("Raised Error: ",e)


def trip_duration_stats(city_data_dataframe):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    # Sleep timer to display statistics orderly and not all at once
    time.sleep(3)
    start_time = time.time()

    try:
        # display total travel time
        print("Total travel Time is {} hours".format(city_data_dataframe['Trip Duration'].sum()/60))

        # display mean travel time
        print("Average travel Time is {} hours".format(city_data_dataframe['Trip Duration'].mean()/60))

        print("\nThis took %s seconds." % (time.time() - start_time))
        print('-'*40)

    except KeyError as e:
        print('Incorrect File Format. Columns "Total travel Time","Average travel Time" must be present.'.format(e))
    except Exception as e:
        print("Raised Error: ",e)

def user_stats(city_data_dataframe):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    # Sleep timer to display statistics orderly and not all at once
    time.sleep(3)
    start_time = time.time()

    try:
        # Display counts of user types
        print("\nUser Type Distribution")
        print(city_data_dataframe['User Type'].value_counts())

        # Display counts of gender
        print("\nGender Distribution")
        print(city_data_dataframe['Gender'].value_counts())

        # Display earliest, most recent, and most common year of birth
        birth_year = [year for year in city_data_dataframe['Birth Year'] if year > 0]
        print("\nOldest Customer(s) year of birth is {}".format(min(birth_year)))
        print("Youngest Customers(s) year of birth is {}".format(max(birth_year)))
        print("Most Common Birth Year is {}".format(mode(birth_year)))

        print("\nThis took %s seconds." % (time.time() - start_time))
        print('-'*40)

    except KeyError as e:
        print('Incorrect File Format. Columns "User Type","Gender Distribution","Birth Year" must be present.'.format(e))
    except Exception as e:
        print("Raised Error: ",e)


def main():
    while True:
        city, month, day = get_filters()
        city_data_dataframe = load_data(city, month, day)
        city_data_dataframe = preprocessing(city_data_dataframe,city)
        time_stats(city_data_dataframe)
        station_stats(city_data_dataframe)
        trip_duration_stats(city_data_dataframe)
        user_stats(city_data_dataframe)
        view_data(city_data_dataframe)

        restart = input('\nWould you like to restart? Enter yes or no.\n')
        if restart.lower() != 'yes':
            break


if __name__ == "__main__":
	main()
