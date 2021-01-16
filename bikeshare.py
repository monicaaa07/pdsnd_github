import time
import pandas as pd
import numpy as np
from statistics import mode
import pprint

# dict to get the right filename based on selection
CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

# lists for months and weekdays to select name based on position (index)
months = ['all','january', 'february', 'march', 'april', 'may', 'june']
weekdays =  ['all','monday','tuesday','wednesday','thursday','friday','saturday','sunday']

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
            day = invalid_input_helper(weekdays, day)
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
        df - Pandas DataFrame containing city data filtered by month and day
    """
    try:
        # load data file into a dataframe
        df = pd.read_csv(CITY_DATA[city])

        # convert the Start Time column to datetime
        df['Start Time'] = pd.to_datetime(df['Start Time'])

        # extract month and day of week from Start Time to create new columns
        df['month'] = df['Start Time'].dt.month
        df['day_of_week'] = df['Start Time'].dt.weekday

        # filter by month if applicable
        if month != 'all':
            # use the index of the months list to get the corresponding int
            month = months.index(month)
            # filter by month to create the new dataframe
            df = df[df['month'] == month]

        # filter by day of week if applicable
        if day != 'all':
            day = weekdays.index(day)
            # filter by day of week to create the new dataframe
            df = df[df['day_of_week'] == day-1]

        return df

    except KeyError as e:
        print('Incorrect File Format. Columns "Start Time","month","day_of_week" must be present. '.format(e))
    except Exception as e:
        print("Raised Error: ",e)


def preprocessing(df, city):
    """
    Renames columns, change to approporiate datatypes
    Args:
        df - DataFrame to be pre-processed
    Returns:
        df - cleaner DataFrame
    """
    try:
        df.fillna(0,inplace = True)
        #changing column datatypes
        df['End Time'] = pd.to_datetime(df['End Time'])

        # washington.csv is missing 'Birth Year' column. Adding a dummy column if input file is washington's
        if city == 'washington':
            df['Birth Year'] = np.zeros(len(df))
        df['Birth Year'] = pd.Series(map(lambda x:int(x),df['Birth Year']))

        # renaming column names to be more readable
        df.rename(columns = {'Unnamed: 0':'Trip Id'},inplace = True)
        return df

    except KeyError as e:
        print('Incorrect File Format. Columns "End Time","Birth Year" must be present. '.format(e))
    except Exception as e:
        print("Raised Error: ",e)

def view_data(df):
    """
    Allows user to view data five rows at a time. User can exit if done viewing data
    """
    try:
        print("\nSelected data contains {} rows.".format(len(df)))
        view_option = input("\nWould you like to view first 5 rows of data? Enter yes or no: ").lower()
        view_option = invalid_input_helper(['yes','no'], view_option)
        # sindex is start index and lindex is last index incremented by 5 to display 5 rows to the user
        sindex, lindex = 0, 5
        pp = pprint.PrettyPrinter(compact=True)
        while view_option == 'yes':
            pp.pprint(df[sindex:lindex].to_dict(orient='records'))
            sindex, lindex = lindex, lindex + 5
            view_option = input("\nWould you like to view next 5 rows of data? Enter yes or no: ").lower()
            view_option = invalid_input_helper(['yes','no'], view_option)
        print('-'*70)
    except Exception as e:
        print("Raised Error: ",e)

def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    # Sleep timer to display statistics orderly and not all at once
    time.sleep(3)
    start_time = time.time()

    try:
        # display the most common month
        busiest_month_index = df['month'].mode()[0]
        print("Busiest Month was {}".format(months[busiest_month_index].title()))

        # display the most common day of week
        busiest_dow_index = df['day_of_week'].mode()[0]
        print("Busiest Day of Week was {}".format(weekdays[busiest_dow_index].title()))

        # display the most common start hour
        busiest_start_hour = df['Start Time'].dt.hour.mode()[0]
        print("Busiest Start Hour was {}:00".format(busiest_start_hour))

        print("\nThis took %s seconds." % (time.time() - start_time))
        print('-'*40)

    except Exception as e:
        print("Raised Error: ",e)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""
    print('\nCalculating The Most Popular Stations and Trip...\n')
    # Sleep timer to display statistics orderly and not all at once
    time.sleep(3)
    start_time = time.time()

    try:
        # display most commonly used start station
        popular_start = df['Start Station'].mode()[0]
        print("Most popular Start Station was {}".format(popular_start))

        # display most commonly used end station
        popular_end = df['End Station'].mode()[0]
        print("Most popular End Station was {}".format(popular_end))

        # display most frequent combination of start station and end station trip
        routes = df['Start Station'] + " : " + df['End Station']
        popular_route = routes.mode()[0]
        print("Most popular Route was {} to {}".format(*popular_route.split(':')))

        print("\nThis took %s seconds." % (time.time() - start_time))
        print('-'*40)

    except KeyError as e:
        print('Incorrect File Format. Columns "Start Station","End Station" must be present.'.format(e))
    except Exception as e:
        print("Raised Error: ",e)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    # Sleep timer to display statistics orderly and not all at once
    time.sleep(3)
    start_time = time.time()

    try:
        # display total travel time
        print("Total travel Time is {} hours".format(df['Trip Duration'].sum()/60))

        # display mean travel time
        print("Average travel Time is {} hours".format(df['Trip Duration'].mean()/60))

        print("\nThis took %s seconds." % (time.time() - start_time))
        print('-'*40)

    except KeyError as e:
        print('Incorrect File Format. Columns "Total travel Time","Average travel Time" must be present.'.format(e))
    except Exception as e:
        print("Raised Error: ",e)

def user_stats(df):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    # Sleep timer to display statistics orderly and not all at once
    time.sleep(3)
    start_time = time.time()

    try:
        # Display counts of user types
        print("\nUser Type Distribution")
        print(df['User Type'].value_counts())

        # Display counts of gender
        print("\nGender Distribution")
        print(df['Gender'].value_counts())

        # Display earliest, most recent, and most common year of birth
        birth_year = [year for year in df['Birth Year'] if year > 0]
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
        df = load_data(city, month, day)
        df = preprocessing(df,city)
        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)
        view_data(df)

        restart = input('\nWould you like to restart? Enter yes or no.\n')
        if restart.lower() != 'yes':
            break


if __name__ == "__main__":
	main()
