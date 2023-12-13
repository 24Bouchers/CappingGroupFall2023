from flask import Flask, render_template, request, flash, redirect, url_for
from pytz import timezone
from datetime import datetime, timedelta, date
import pymysql
import math


app = Flask(__name__)
app.secret_key = 'ArchFiber23'

SERVER_ONE_HOST = '10.10.9.43'
SERVER_ONE_USER = 'radius_ui'
SERVER_ONE_PASSWORD = 'ExamplePassword'
SERVER_ONE_DB = 'radius_netelastic'

SERVER_TWO_HOST = '10.10.9.43'
SERVER_TWO_USER = 'radius_ui'
SERVER_TWO_PASSWORD = 'ExamplePassword'
SERVER_TWO_DB = 'radius_netelastic'

#####################
# HOME PAGE DISPLAY #
#####################

@app.route('/')
@app.route('/index.html', methods=['GET'])
def main():

    ###########################
    # Server Two | Static IPs #
    ###########################

    try:
        with (pymysql.connect(host=SERVER_TWO_HOST, user=SERVER_TWO_USER, password=SERVER_TWO_PASSWORD, db=SERVER_TWO_DB) as serverTwoConn, 
            serverTwoConn.cursor(pymysql.cursors.DictCursor) as serverTwocursor):

            #Set the connection status for imgs
            serverTwoConnection = 'online'

            #Static IP
            serverTwocursor.execute('SELECT COUNT(DISTINCT username) AS count_entries FROM radreply WHERE username IS NOT NULL;')
            static_devices_count = serverTwocursor.fetchone().get('count_entries', 0)

            serverTwocursor.execute('SELECT COUNT(DISTINCT username) AS count_entries FROM radreply WHERE username IS NOT NULL;')
            result = serverTwocursor.fetchall()

        if result is not None and len(result) > 0:
            static_devices_count = result[0]['count_entries']
        else:
            static_devices_count = 0

    except pymysql.Error as e:
        print(f"Error connecting to Server Two: {e}")
        static_devices_count = 0
        #Set the connection status for imgs
        serverTwoConnection = 'offline'

    ################
    ## Server One ##
    ################

    try:
        with (pymysql.connect(host=SERVER_ONE_HOST, user=SERVER_ONE_USER, password=SERVER_ONE_PASSWORD, db=SERVER_ONE_DB) as serverOneConn, 
            serverOneConn.cursor(pymysql.cursors.DictCursor) as serverOnecursor):

            # Set the connection status for imgs
            serverOneConnection = 'online'

            #######################
            ## Reachable Devices ##
            #######################
            
            serverOnecursor.execute("SELECT COUNT(DISTINCT username) AS count_entries FROM radacct WHERE acctterminatecause = '';")
            result = serverOnecursor.fetchone()

            if result is not None:
                reachable_device_count = result['count_entries']
            else:
                reachable_device_count = 0

            ######################
            ## Unreachable IP's ##
            ######################

            serverOnecursor.execute("""
                SELECT COUNT(*) AS count_entries
                FROM (
                    SELECT username 
                    FROM radacct r 
                    WHERE acctterminatecause <> '' 
                    AND NOT EXISTS (
                        SELECT * 
                        FROM radacct r2 
                        WHERE r2.username = r.username 
                        AND r2.acctterminatecause = ''
                    )
                    GROUP BY username 
                ) a;
            """)

            unreachable_device_count = serverOnecursor.fetchone().get('count_entries', 0)

            ###################
            ## Total Devices ##
            ###################

            serverOnecursor.execute("SELECT COUNT(*) AS total_devices_count FROM (SELECT 'x' x FROM radacct GROUP BY username) a;")
            result = serverOnecursor.fetchone()

            if result is not None:
                total_devices_count = result['total_devices_count']
            else:
                total_devices_count = 0

            ##################
            ##    GRAPH     ##
            ##################

            # Grab the data
            serverOnecursor.execute('select acctstarttime from radacct order by acctstarttime DESC;')

            # setup date and time for both UTC(for value calculations) and EST(for bottom label of graph)
            stime = serverOnecursor.fetchall()

            # setup date and time for both UTC(for value calculations) and EST(for bottom label of graph)
            todayDate = date.today()
            currentTimeUTC = datetime.now(timezone('UTC')).strftime("%H:%M")
            currentTimeEST = datetime.now(timezone('EST')).strftime("%H:%M")
            yesterdayDate = str(todayDate - timedelta(days = 1))
            todayDate = str(todayDate)
            # convert current time into minutes
            currentTimeSplit = str(currentTimeUTC).split(':')
            currentTimeEST = str(currentTimeEST).split(':')
            # counts down to the nearest 15 minute interval
            close15MinInterval =int(currentTimeSplit[1])
            minIntervalTimeEST = int(currentTimeEST[1])
            sameTime = True
            while close15MinInterval % 15 != 0:
                close15MinInterval -= 1
                minIntervalTimeEST -= 1 
                sameTime = False
            currentTimeMin = close15MinInterval + (int(currentTimeSplit[0])*60)

            # list that will store the 15 minute interval numbers
            # going to be every 15 min for 6 hours
            global intervals
            intervals = [0] * 24
            hoursInMin = 360 # 360 represents 6 hours
            # offset is to adjust the intervals if the first time appering on the graph isn't a 15 minute interval 
            offset = 0
            if not sameTime:
                offset = 1
            # loop through the list of times given from acctstarttime
            for x in stime:
                # separates date and time into 2 separate list elements
                splitDateTime = str(x.get('acctstarttime')).split() 
                if splitDateTime and splitDateTime[0] != 'None':
                    # convert the acctstarttime into minutes
                    splitTime = str(splitDateTime[1]).split(':')
                    totalTimeMin = int(splitTime[1]) + (int(splitTime[0])*60)
                    # since the time were comparing against is the closest 15 minute interval that has already passed
                    # if a time appears that has todays date and is passed the time were checking from
                    # it gets added to the most recent column of the graph
                    if totalTimeMin > currentTimeMin and splitDateTime[0] == todayDate and (totalTimeMin-currentTimeMin) <= 15 :
                        intervals[0] += 1 
                    # check if at least 6 hours have passed since start of day and dates match
                    elif currentTimeMin >= hoursInMin and splitDateTime[0] == todayDate:
                        # first finds out how many 15 minute intervals passed
                        diff = math.ceil(currentTimeMin/15) - math.ceil(totalTimeMin/15)
                        if diff < len(intervals)-offset and diff > -1:
                            intervals[diff+offset] += 1
                    # sees if there was a 6 hour diffrence max between times and thta date matches either today or yesterday
                    elif (1440 - totalTimeMin) + currentTimeMin <= hoursInMin and (splitDateTime[0] == todayDate or splitDateTime[0] == yesterdayDate):
                        if splitDateTime[0] == yesterdayDate:
                            # 1440 is the amount of minutes in a day
                            diff = math.ceil(currentTimeMin/15) + math.ceil((1440 - totalTimeMin)/15)
                            if diff < len(intervals)-offset and diff > -1:
                                intervals[diff+offset] += 1
                        else:
                            diff = math.ceil(currentTimeMin/15) - math.ceil(totalTimeMin/15)
                            if diff < len(intervals)-offset and diff > -1:
                                intervals[diff+offset] += 1
                    # once the date is not today or yesterday and the time has more then a 7 hour gap
                    # code will break out of loop to save resorces and time
                    elif (splitDateTime[0] == todayDate or splitDateTime[0] == yesterdayDate) and (currentTimeMin - totalTimeMin) > (hoursInMin+60):
                        break

            # the bottom labels of the line graph representing 15 minute increments
            global labels
            labels = [''] * 25
            firstgo = True 
            offset = 0
            for x in range(24):
                # if the current time is not a even 15 minunet interval the it will be added as the first place on the graph display
                # it then addes the the closest 15 minute interval that has passed as the second place in the display  
                if x == 0 and not sameTime:
                    format_time(labels, currentTimeEST, currentTimeEST[1], x)
                    format_time(labels, currentTimeEST, str(minIntervalTimeEST), x+1)
                    # adds an offset since two separate labels get added above
                    # only adds if current minute not withen first 15 minuts of an hour since code will auto fix time asignment only for the first 15 minutes 
                    if int(currentTimeEST[1]) > 15:
                        offset = 1
                    firstgo = False
                else:
                    # subtracts 15 minutes form previous time
                    if int(minIntervalTimeEST) - 15 > 0:
                        if not firstgo:
                            minIntervalTimeEST -= 15
                        else:
                            firstgo = False
                        format_time(labels, currentTimeEST, str(minIntervalTimeEST), x+offset)
                    # will be true if the first entry (or x == 0), is on the hour and only then
                    elif firstgo  and str(currentTimeEST[1]) != '00':
                        format_time(labels, currentTimeEST, str(minIntervalTimeEST), x+offset)
                        firstgo = False
                    # adjusts the hour value
                    else: 
                        format_time(labels, currentTimeEST, '00', x+offset)  
                        # reset the minute interval back to one hour
                        minIntervalTimeEST = 60
                        currentTimeEST[0] = str(int( currentTimeEST[0])-1)
                        # reset the hours so it can calculate yesterday time if needed
                        if int(currentTimeEST[0])  < 0:
                            currentTimeEST[0] = '23'
                        firstgo = False

            # 12 am times appear as 0 for 24 hour format, adjusts to 12 hour format for labels
            for x in range(24):
                time = labels[x].split(':')
                if time[0] == '00' or time[0] == '0':
                    labels[x] = '12:' + time[1]

            # reverse the lists so they appear from right to left on webpage 
            del labels[-1]
            intervals.reverse()
            labels.reverse()


    except pymysql.Error as e:
            # Handle the exception (e.g., print an error message)
            print(f"Error connecting to the database: {e}")
            # Set default values
            reachable_device_count = 0
            unreachable_device_count = 0
            total_devices_count = 0
            labels = ''
            intervals = 0
            # Set the connection status for imgs
            serverOneConnection = 'offline'
    finally:
        return render_template('index.html',
            labels=labels,
            values=intervals,
            reachable_device_count=reachable_device_count,
            static_devices_count=static_devices_count,
            unreachable_device_count=unreachable_device_count,
            total_devices_count=total_devices_count,
            serverOneConnection=serverOneConnection,
            serverTwoConnection=serverTwoConnection
            )
    
# takes in the labels list, the currentTimeEST, whatever the minute needs to me assigned, and the index the label is going into
# determins if it needs a am or pm ending and will adjust the hour number since going from 24 to 12 hour format
# converts to int then string again to remove any proceeding zeros (01 becomes 1)
def format_time(labels, timeEST, timeInterval, index):
    if timeEST[0] == '12':
        labels[index] = timeEST[0] + ':' + timeInterval + ' pm'
    elif int(timeEST[0])*60 > 720:
        labels[index] = str(int(timeEST[0])-12) + ':' + timeInterval + ' pm'
    else:
        labels[index] = str(int(timeEST[0])) + ':' + timeInterval + ' am' 

# Add Device
@app.route('/addDevice.html', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        try:
            username = request.form.get('MAC', default=None)
            ipv4 = request.form.get('IPv4', default=None)
            ipv6Prefix = request.form.get('IPv6 Prefix', default=None)
            ipv6 = request.form.get('IPv6', default=None)

            # Check if the username already exists
            with pymysql.connect(host=SERVER_TWO_HOST, user=SERVER_TWO_USER, password=SERVER_TWO_PASSWORD, db=SERVER_TWO_DB) as serverTwoConn, serverTwoConn.cursor(pymysql.cursors.DictCursor) as serverTwocursor:
                serverTwocursor.execute('SELECT username FROM radius_netelastic.radreply WHERE username = %s', (username,))
                existing_user = serverTwocursor.fetchone()

                if existing_user:
                    flash(f'Error: Username {username} already exists!', 'danger')
                    return redirect(url_for('add_device'))

                # Call the stored procedure to add the device entry based on the MAC address
                serverTwocursor.callproc('radius_netelastic.PROC_InsUpRadiusUser', (username, ipv4, ipv6Prefix, ipv6))
                serverTwocursor.execute('INSERT INTO radius_netelastic.logs(username, reason, time) VALUES (%s, %s, NOW())', (username, 'Added'))
                serverTwoConn.commit()
                
            return redirect('/devices.html')

        except pymysql.Error as e:
            flash(f'Database error: {e}', 'danger')
            return redirect('/addDevice.html')

    return render_template('addDevice.html')

# Remove device
@app.route("/removeDevice", methods=["POST"])
def remove_device():
    username = request.form.get('username')

    try:
        # Connect to the radius_netelastic database
        with pymysql.connect(host=SERVER_TWO_HOST, user=SERVER_TWO_USER, password=SERVER_TWO_PASSWORD, db=SERVER_TWO_DB) as serverTwoConn, serverTwoConn.cursor(pymysql.cursors.DictCursor) as serverTwocursor:

            # Call the stored procedure to delete the device entry based on the MAC address
            try:
                serverTwocursor.callproc('radius_netelastic.PROC_DeleteRadiusUser', (username,))
                serverTwocursor.execute('INSERT INTO radius_netelastic.logs(username, reason, time) VALUES (%s, %s, NOW())', (username, 'Removed'))
                serverTwoConn.commit()
            except Exception as e:
                print(f"Error while removing device: {e}")
    except Exception as ex:
        print(f"Error connecting to the database: {ex}")

    return redirect('/devices.html')

# Get the device information to edit
def get_device_data(username):
    try:
        # Establish a connection to the database
        with pymysql.connect(host=SERVER_TWO_HOST, user=SERVER_TWO_USER, password=SERVER_TWO_PASSWORD, db=SERVER_TWO_DB) as serverTwoConn, serverTwoConn.cursor(pymysql.cursors.DictCursor) as serverTwocursor:

            # SQL query to fetch the device data based on the provided username
            sql = '''
                SELECT 
                    username, 
                    MAX(CASE WHEN attribute = 'Framed-IP-Address' THEN value END) AS 'Framed-IP-Address',
                    MAX(CASE WHEN attribute = 'Framed-IPv6-Prefix' THEN value END) AS 'Framed-IPv6-Prefix',
                    MAX(CASE WHEN attribute = 'Framed-IPv6-Address' THEN value END) AS 'Framed-IPv6-Address'
                FROM radreply
                WHERE username = %s
                GROUP BY username;
            '''

            serverTwocursor.execute(sql, (username,))

            # Fetch one record and store it in the device_data dictionary
            device_data = serverTwocursor.fetchone()

        return device_data

    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

# Get The details For edit Page  
@app.route('/editDevice/<username>')
def show_edit_device_page(username):
    try:
        # Fetch the device data from your database based on the username/mac
        current_device_data = get_device_data(username)
        return render_template('editDevice.html', username=username, current_device_data=current_device_data)
    except Exception as e:
        error_message = f"Error while fetching device data: {e}"
        print(error_message)
        return render_template('404.html', error_message=error_message)


from flask import Flask, request, redirect, flash
import pymysql

@app.route('/updateDevice/<path:username>', methods=['POST'])
def update_device(username):
    try:
        # Extract form data
        ipv4 = request.form.get('ipv4_address')
        ipv6Prefix = request.form.get('ipv6_prefix')
        ipv6 = request.form.get('ipv6_address')

        # Connect to the radius_netelastic database
        with pymysql.connect(host=SERVER_TWO_HOST, user=SERVER_TWO_USER, password=SERVER_TWO_PASSWORD, db=SERVER_TWO_DB) as serverTwoConn, serverTwoConn.cursor(pymysql.cursors.DictCursor) as serverTwocursor:

            # Before executing the stored procedure
            print(f"Calling stored procedure with parameters: {username}, {ipv4}, {ipv6Prefix}, {ipv6}")

            # Execute stored procedure and insert into logs
            serverTwocursor.callproc('radius_netelastic.PROC_InsUpRadiusUser', (username, ipv4, ipv6Prefix, ipv6))
            serverTwocursor.execute('INSERT INTO radius_netelastic.logs(username, reason, time) VALUES (%s, %s, NOW())', (username, 'Edited'))

            try:
                # Commit the transaction
                serverTwoConn.commit()
                print("Commit successful")
            except Exception as commit_exception:
                print(f"Error during commit: {commit_exception}")

            # Check if the update was successful
            if serverTwocursor.rowcount > 0:
                flash('Device updated successfully!')
            else:
                flash('No device was updated.')

    except pymysql.MySQLError as e:
        print(f"Error while updating device: {e}")
        flash(f"MySQL Error during update: {e}")
        flash('Failed to update device. Please try again.')
    except Exception as inner_exception:
        print(f"Error during update process: {inner_exception}")
        flash('Failed to update device. Please try again.')

    return redirect('/devices.html')


##################
# DISPLAY TABLES #
##################

# Display Devices
@app.route('/devices.html', methods=['GET', 'POST'])
def devices():
    try:
        with pymysql.connect(host=SERVER_TWO_HOST, user=SERVER_TWO_USER, password=SERVER_TWO_PASSWORD, db=SERVER_TWO_DB) as serverTwoConn, serverTwoConn.cursor(pymysql.cursors.DictCursor) as serverTwocursor:
            query = request.form.get('query') if request.method == 'POST' else None

            if query:
                # Query is searching from the database based on name, mac address, ipv4, or ipv6 address
                serverTwocursor.execute('''SELECT username, 
                                            MAX(CASE WHEN attribute = 'Framed-IP-Address' THEN value END) AS 'Framed-IP-Address',
                                            MAX(CASE WHEN attribute = 'Framed-IPv6-Prefix' THEN value END) AS 'Framed-IPv6-Prefix',
                                            MAX(CASE WHEN attribute = 'Framed-IPv6-Address' THEN value END) AS 'Framed-IPv6-Address'
                                        FROM radreply 
                                        WHERE username LIKE %s 
                                            OR (MAX(CASE WHEN attribute = 'Framed-IP-Address' THEN value END) LIKE %s) 
                                            OR (MAX(CASE WHEN attribute = 'Framed-IPv6-Prefix' THEN value END) LIKE %s) 
                                            OR (MAX(CASE WHEN attribute = 'Framed-IPv6-Address' THEN value END) LIKE %s)
                                        GROUP BY username;''', 
                                    ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))

            else:
                serverTwocursor.execute('''SELECT
                    username,
                    MAX(CASE WHEN `attribute` = 'Framed-IP-Address' THEN value END) AS 'Framed-IP-Address',
                    MAX(CASE WHEN `attribute` = 'Framed-IPv6-Prefix' THEN value END) AS 'Framed-IPv6-Prefix',
                    MAX(CASE WHEN `attribute` = 'Framed-IPv6-Address' THEN value END) AS 'Framed-IPv6-Address'
                    FROM radreply
                    WHERE `attribute` IN ('Framed-IP-Address', 'Framed-IPv6-Prefix', 'Framed-IPv6-Address')
                    GROUP BY username;
                ''')

            rows = serverTwocursor.fetchall()

    except Exception as e:
        print(f"Error while fetching devices data: {e}")
        return render_template('404.html')

    return render_template('/devices.html', rows=rows)


# Display Logs
@app.route('/logs.html', methods=['GET', 'POST'])
def logs():
    try:
        with pymysql.connect(host=SERVER_TWO_HOST, user=SERVER_TWO_USER, password=SERVER_TWO_PASSWORD, db=SERVER_TWO_DB) as serverTwoConn, serverTwoConn.cursor(pymysql.cursors.DictCursor) as serverTwocursor:
            query = request.form.get('query') if request.method == 'POST' else None

            if query:
                # Adjust the fields in the SQL query based on the actual database schema
                serverTwocursor.execute('''SELECT logId, time, username, reason FROM logs 
                           WHERE time LIKE %s OR username LIKE %s OR reason LIKE %s''',
                           ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
            else:
                serverTwocursor.execute('SELECT logID, time, username, reason FROM logs ORDER BY time DESC;')

            rows = serverTwocursor.fetchall()
    except Exception as e:
        print(f"Error while fetching logs data: {e}")
        return render_template('404.html')

    return render_template('logs.html', rows=rows)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)