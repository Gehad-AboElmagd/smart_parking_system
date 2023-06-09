"""
                          Coder : ENG.Omar | Eng.Asmaa
                          Version : v2.0B
                          version Date :  19 / 5 / 2023
                          Code Type : python | SQLite database=> smart_parking_project
                          Title : Smart Parking System
                          Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
"""
import sqlite3
import numpy as np
import datetime
import time
import math
import os.path
import sys
import random
import string


from database_data import *


###########################################################################
def connect_db():
    """
    connect sqlite3 to python file and ensure ref.integrity enabled .

    best to call build_db() instead calling this function directly
    """

    # Get the absolute path of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
   # Construct a relative path to the 'smart_garage.db' file
    db_path = os.path.join(current_dir, 'data_db', 'smart_garage.db')

    db_path = "./database_data/smart_parking.db"
    connect_obj = None

    try:
        # connect_obj = sqlite3.connect(def_db, autocommit=True) # autocommite doesnt work in this version
        connect_obj = sqlite3.connect(db_path)
        connect_obj.execute("PRAGMA foreign_keys = ON")
        return connect_obj

    except sqlite3.Error as e:
        print(e)


###########################################################################


def create_db(conn):
    ''' don't call This function directly! (only via build_bd() -> whenever you establish new Db only once to build your db structure '''
    cursor = conn.cursor()

    # table 1
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS people_info (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        car_model TEXT,
        car2_model TEXT,
        license_exp_date DATE,
        Gmail TEXT
        );
        """
    )

    # table 2 event type : 0 == occupy a cell , 1 == free a cell
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS event_log(
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id TEXT NOT NULL,
        event_type INTEGER NOt NULL,
        car TEXT NOT NULL,
        cost INTEGER ,
        password_ TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT  NULL,
        FOREIGN KEY (person_id) REFERENCES people_info(id)
        );
        """
    )

    # table 3 status : 0 = available , 1 = full , 2 = maintainance
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS parking_status(
        cell_id INTEGER PRIMARY KEY AUTOINCREMENT,
        taken_by TEXT DEFAULT NULL,
        status INTEGER DEFAULT 0 ,
        FOREIGN KEY (taken_by) REFERENCES people_info(id)
        );
        """
    )

    # table 4 platform
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Platform(
        Cell_id INTEGER,
        FOREIGN KEY (Cell_id) REFERENCES parking_status(cell_id)
        );
        """
    )

    # table 5 id reference image for CV operations
    cursor.execute(
        """
   CREATE TABLE IF NOT EXISTS reference_images (
      ref_id  INTEGER PRIMARY KEY AUTOINCREMENT ,
      img_name TEXT UNIQUE,
      img_data BLOB,
      Extracted_id TEXT,
      FOREIGN KEY (Extracted_id) REFERENCES people_info(id)
   );
   """
    )

    # table 6 email_queue save emails until gmail connection comes again
    cursor.execute(
        """
   CREATE TABLE IF NOT EXISTS email_queue (
      queue_cnt INTEGER PRIMARY KEY AUTOINCREMENT ,
      user_id TEXT,
      user_email TEXT,
      msg_content TEXT,
      push_time DATETIME DEFAULT CURRENT_TIMESTAMP,
      
      FOREIGN KEY (user_id) REFERENCES people_info(id)
   );
   """
    )

# 30 test sample of non real people info ( 1st two records is expired and about to expire license for later use)
    cursor.execute(
        """
        INSERT INTO people_info (id, name, car_model , license_exp_date , Gmail)
        VALUES
      ('51483525410590', 'Ahmed Ali', 'Toyota Camry 2010',
       '2022-12-31', 'hjeklpyf@gmail.com'),
      ('94327645058732', 'Fatima Ahmed', 'Nissan Altima 2014',
       '2024-04-31', 'yqgtrmfa@gmail.com'),
      ('54302518496307', 'Abdullah Hassan', 'Honda Accord 2016',
       '2024-06-30', 'omar22xd@gmail.com'),
      ('11111111111111', 'Omar Rashad', 'Rolls-Royce dawn 2022',
       '2027-05-13', 'omar33xd@gmail.com'),
      ('69301847590631', 'Sara Khalid', 'BMW 750i 2015',
       '2025-05-31', 'omarrashad85@gmail.com'),
      ('59482143698237', 'Hamdy Kamal', 'Mercedes E-Class 2018',
       '2025-07-31', 'hamdy_elminir@hotmail.com'),
      ('57392618347590', 'Hassan Mohammad',
       'Mercedes S-Class 2017', '2025-11-30', 'gxzqywcn@gmail.com'),
      ('43768403502931', 'Nada Abdullah', 'Audi A6 2018',
       '2026-08-31', 'gata3458@hotmail.com'),
      ('48930257301924', 'Yara Khalid', 'Nissan Maxima 2013',
       '2022-07-31', 'vxytqjna@gmail.com'),
      ('82095736204839', 'Yusuf Ali', 'Nissan Altima 2012',
       '2031-07-31', 'wzfqyujc@gmail.com'),
      ('82154763902174', 'Aisha Khalil', 'Porsche 911 2020',
       '2028-04-30', 'pqzynuwm@gmail.com'),
      ('38574820856990', 'Khaled Hassan', 'Toyota RAV4 2021',
       '2029-09-30', 'fymrvzne@gmail.com'),
      ('12092547103826', 'Noor Ahmed', 'Honda Civic 2022',
       '2030-03-31', 'dhtzjybe@gmail.com'),
      ('90584058237584', 'Ali Hassan', 'Toyota Corolla 2017',
       '2023-05-31', 'ongjhtdm@gmail.com'),
      ('76587430965402', 'Mariam Ahmed', 'BMW X5 2016',
       '2024-02-29', 'qjywxibt@gmail.com'),
      ('10756736490582', 'Hassan Ali', 'Audi Q5 2019',
       '2026-05-31', 'zgxtqndm@gmail.com'),
      ('84263049387356', 'Sara Abdullah', 'Tesla Model Y 2020',
       '2027-11-30', 'nxvrluag@gmail.com'),
      ('17593745068247', 'Nora Saad', 'Porsche Panamera 2015',
       '2028-10-31', 'tuzpjydr@gmail.com'),
      ('23570968430879', 'Abdul Rahman Salam',
       'Honda CR-V 2014', '2029-12-31', 'qgwmvhey@gmail.com'),
      ('20968472036847', 'Lina Khalid', 'Toyota Camry 2011',
       '2030-09-30', 'mzydjrnh@gmail.com'),
      ('94375029830610', 'Hassan Abdullah',
       'Tesla Model Y 2020', '2027-11-30', 'kqjzatoh@gmail.com'),
      ('29578406135029', 'Sara Saad', 'Porsche Panamera 2015',
       '2028-10-31', 'zjgulyfm@gmail.com'),
      ('50983740125674', 'Abdul Rahman Ali',
       'Honda CR-V 2014', '2029-12-31', 'apfbsqkx@gmail.com'),
      ('98406270356408', 'Somaia Khalid', 'Toyota Camry 2011',
       '2030-09-30', 'hjyqmcab@gmail.com'),
      ('62970315483745', 'Fatima Ali', 'Nissan Altima 2012',
       '2031-07-31', 'tkpiaxjb@gmail.com'),
      ('41098726395820', 'Yusuf Khalid', 'Honda Accord 2016',
       '2022-08-31', 'xvukqjrg@gmail.com'),
      ('95673402567849', 'Saif Hassan', 'Honda Accord 2016',
       '2022-08-31', 'fblgqmyi@gmail.com'),
      ('94368209865439', 'Saad Khalid', 'BMW 740i 2018',
       '2023-06-30', 'fzglqhvn@gmail.com'),
      ('84759370289347', 'Ali Abdullah', 'Toyota Corolla 2017',
       '2024-05-31', 'yiqkujrg@gmail.com'),
      ('58943270598347', 'Nada Khalid', 'Nissan Altima 2015',
       '2025-10-31', 'ohxgnspl@gmail.com');
            """
    )
    conn.commit()  # some statements need commit / but we enabled auto commit

    # INSERT initial data for parking status table
    cursor.execute(
        """
        INSERT INTO parking_status (cell_id)
        VALUES
        (0),
        (1),
        (2),
        (3),
        (4),
        (5);
        """
    )
    conn.commit()  # some statements need commit / but we enabled auto commit


###########################################################################


def build_db():  # only once to create database
    ''' call This function whenever you establish new Db only once to build your db structure '''

    conn = connect_db()
    # inside create_db() will make the 5 main tables
    # -> people_info , parking_status , event_log , total_available , reference_image
    create_db(conn)

##########################################################################


def is_full():

    with connect_db() as conn:
        cursor = conn.cursor()
        # check if parking is full return parking full err (from available table)
        # we could use select sum() instead also )

        car_counter_query = (
            """ SELECT COUNT(status) FROM parking_status WHERE  status = 0 """)
        cursor.execute(car_counter_query)
        available_cells = (cursor.fetchall())[0][0]

        if available_cells == 0 or available_cells == None:
            conn.close()
            print(" debug message : Fail parking is full!\n")
            return True  # park full
        else:
            return False  # park is not full

###########################################################################


def validate_pass(pass_to_check: str, id, cursor: sqlite3.Cursor) -> bool:

    #  disable_rand_hash_seed()

    #  pass_to_check = str(hash(pass_to_check))
    pass_to_check = str(pass_to_check)

    cursor.execute(
        """
        SELECT  password_ FROM event_log WHERE person_id = ? AND event_type = 0
        ORDER BY event_id DESC;
        """, (id,))

    saved_pass = (cursor.fetchall())[0][0]
    if len(saved_pass) == 0 or pass_to_check == 'None':
        return True

    if saved_pass == pass_to_check:
        return True
    else:
        return False

###########################################################################


def calc_cost(person_id: str, car: str, conn: sqlite3.Connection):
    """
     get diffrence between parking time and free cell time then mul with cost per hour

-----
    return :

    (total_cost_le ,  tot_time_hour)

     """

    cursor = conn.cursor()
    # change_cost_per hour as you wish
    tot_cost_le, tot_time_hour, cost_per_hour = 0, 0, 3

    # use julianday() is slqite3 function that gets time in days
    cursor.execute(
        """
        SELECT  JULIANDAY(timestamp) FROM event_log WHERE person_id = ? AND car = ? AND event_type = 0
        ORDER BY event_id DESC;
        """, (person_id, car))
    last_id_park_event_time = (cursor.fetchone())[0]

    cursor.execute(
        """
        SELECT  JULIANDAY(timestamp) , event_id FROM event_log WHERE person_id = ? AND car = ? AND event_type = 1
        ORDER BY event_id DESC;
        """, (person_id, car))
    last_free_id_info = (cursor.fetchall())[0]
    last_id_free_event_time = last_free_id_info[0]

    time_diff_in_hours = (last_id_free_event_time -
                          last_id_park_event_time) * 24
    tot_time_hour = math.ceil(time_diff_in_hours)
    tot_cost_le = tot_time_hour * cost_per_hour
    # cost per hour = 3 LE ( I know it's cheap ==~ 0.3$)
    # any time less than hour will pay one hour park at least
    # non integer values will be rounded up  ex : 2.2 hours -> 3 hours total to pay

    # update event_log  with the cost  ( park event type has NULL cost)
    event_to_update = last_free_id_info[1]
    cursor.execute(
        """
        UPDATE event_log SET cost = ? WHERE event_id = ? ;
        """, (tot_cost_le, event_to_update))
    conn.commit()
    conn.close()

    # return to get_car_db()
    # ( so that get_car_db() return finally to  main code the : cell_id to free  , total cost  , total parking time )
    # change to list [] if you want to easy overwrite
    return (tot_cost_le, tot_time_hour)


###########################################################################
def park_car_db(conn, cmd, id, temp_pass: str):
    '''park car command to UPDATE database  '

    return : park_cell_no '''

    cursor = conn.cursor()

    if is_full():
        conn.close()
        print(" debug message : Fail parking is full!\n")
        return -1, -1, -1, -1  # -1 == fail park is full

        # if someone called db_cmd(0) -> without putting id
    if (id == "NULL"):
        conn.close()
        print(" debug message : Fail ُEntered Invalid ID!\n")
        return -1, -1, -1, -1

    else:
        # take id  and get all data FROM people_info table ( NO NEED FOR NOW)
        query_personal_data = '''SELECT * FROM people_info WHERE id = ?; '''
        cursor.execute(query_personal_data, (id,))
        person_info = cursor.fetchall()

        if (id == "NULL" or len(person_info) == 0 or person_info is None):
            conn.close()
            print(" debug message : Fail ID is not registered in DB!\n")
            return -1, -1, -1, -1

        # take all persons data and add new event in events log table ( event type : occupy parking cell)
        event_type = cmd
        person_id = id
        person_car = person_info[0][2]
        person_car2 = person_info[0][3]  # no need for now

        # Hash the pass for security before saving in db (temprorality disabled)
      #   disable_rand_hash_seed()
      #   pass_hashed = str(hash(temp_pass))
        pass_hashed = str(temp_pass)
        del temp_pass

        # check: you cant park a car then park it again before freeing it!
        cursor.execute(""" SELECT event_type FROM event_log WHERE person_id = ? AND car = ? ORDER BY event_id DESC
                        """, (person_id, person_car))
        last_event_type = cursor.fetchone()

        if type(last_event_type) == tuple:
            last_event_type = last_event_type[0]

         # if type == 0 the return fail cuz u cant park an already parked car
        if last_event_type == 0:
            conn.close()
            print(" debug message : Fail you can't park an already parked car!\n")
            return -1, -1, -1, -1

        try:
            cursor.execute("""
            INSERT into event_log (person_id , event_type , car , password_ ) VALUES
            (? , ? , ? , ?);
            """, (person_id, event_type, person_car, pass_hashed))
            conn.commit()

        except sqlite3.Error as error:
            conn.close()
            print(" debug message : Failure :) !\n", error)
            return -1, -1, -1, -1

      # Send email to user with pasrking pass
        user_name = person_info[0][1]
        msg_content = f"""
        
        <p>:construction: Hi <em>{user_name}</em>! Thank you for using Smart Parking service :construction:</p>
        								  <br>
                                <p>parking password: {pass_hashed}</p>
                                <br><br>
                           <span style="color:red;">Note:red_exclamation_mark:: </span>
                           <em> (if you parked  using  ID scaner  ignore this message . happy day!) </em>
                           <br>
                           <sub><sub><sub>testing v2.0B</sub></sub></sub>
                         """
        user_email = person_info[0][5]
        state = gmail.main_gmail(
            _to_email=user_email, _msg_title='Parking Passcode :check_mark_button:', _msg_content=msg_content)
        if state != enm.GMAIL_OK:  # issue sending so -> push it to email queue  table -> pop it whne  next get same car cmd  comes
            push_email_query = "INSERT INTO email_queue (user_id , user_email , msg_content) VALUES (? , ? , ?)"
            cursor.execute(push_email_query,
                           (person_id, user_email, msg_content))
            conn.commit()

        # UPDATE parking status table ( take the nearist available parking) and UPDATE total available table
        cursor.execute(
            '''SELECT cell_id FROM parking_status WHERE status = 0 ORDER BY cell_id ASC;''')
        nearest_empty_cell_id = cursor.fetchone()  # returns tuple with only 1 element

        if type(nearest_empty_cell_id) == tuple:
            nearest_empty_cell_id = nearest_empty_cell_id[0]

        # you got the id now change status to 1 (occupied) and  taken by who
        cursor.execute(
            """ UPDATE parking_status SET status = 1 , taken_by = ? WHERE cell_id = ? ;""",
            (id, nearest_empty_cell_id))  # or just pass nearest_empty_cell_id
        conn.commit()

        conn.close()
        # return NOThing important END
        print("debug message : SUCCESS Database has been CHANGED! \n")
        return nearest_empty_cell_id , -1 , -1 , -1 # success
###########################################################################


def send_pop_unsended_emails(conn: sqlite3.Connection, id: str) -> enm:
    cursor = conn.cursor()

    # check if there is unsended email for this id and send them all (last emails first)
    get_emails_query = "SELECT * FROM email_queue  WHERE user_id = ? ORDER BY push_time DESC"
    cursor.execute(get_emails_query, (id,))
    # 2D tuple of : user_id , user_email ,  msg_content , push_time
    user_unsended_emails = cursor.fetchall()
    
   #  queue_cnt INTEGER PRIMARY KEY AUTOINCREMENT ,
   #    user_id TEXT,
   #    user_email TEXT,
   #    msg_content TEXT,
   #    push_time DATETIME DEFAULT CURRENT_TIMESTAMP,
      
   #    FOREIGN KEY (user_id) REFERENCES people_info(id)
   # );

    # now loop on them un send them all
    for email in user_unsended_emails:
        to_email = email[2]
        push_time = email[4]
        msg_content = email[3] + f"<br> <sub><sub> this message is delayed , actual send time was at :  {push_time} </sub></sub>"
        state = gmail.main_gmail(
            _to_email=to_email, _msg_title='Parking Passcode :check_mark_button:',  _msg_content= msg_content)

        if state == enm.GMAIL_OK:
            pop_emails_query = "DELETE FROM email_queue WHERE user_id = ?"
            cursor.execute(pop_emails_query, (id,))
            conn.commit()
        # else : pop them next time ....

        return state
###########################################################################


def get_car_db(conn, cmd, id, pass_to_check: str):
    """
    get car FROM parking command ( free a cell in db )

    Args:

    conn: sqlite3 connection object

    cmd:  zero means a park command, 1 means free cell command ( in this func cmd = 1)

    id : person_id  to get his car




------
    Return :

    cell_number : for arduino to move motors

    is_valid_pass : check given password

    tot_cost_le : cost in le

    tot_time_hour : parking time
    """
    cursor = conn.cursor()

    send_pop_unsended_emails(conn, id)

    # query the parking status table  by id
    cursor.execute(
        """SELECT cell_id , status FROM parking_status WHERE taken_by = ? ; """, (id,))
    cell_data = (cursor.fetchall())

    if cell_data is None or len(cell_data) == 0:
        conn.close()
        print("debug message : FAIL car not found!\n")
        return -1, -1, -1, -1  # fail car not found err

    if type(cell_data) == list:
        cell_data = cell_data[0]

    status = cell_data[1]

    # if car isn't there return no matching id found error
    if status != 1:
        conn.close()
        print("debug message : FAIL car not found!\n")
        return -1, -1, -1, -1  # fail car not found err

    else:
        if validate_pass(pass_to_check, id, cursor) == True:
            del pass_to_check

            # get all personal data FROM personal data table by id ( NO NEED FOR NOW)
            cursor.execute(
                """ SELECT * FROM people_info WHERE id = ?;""", (id,))

            person_data = cursor.fetchall()  # id, name, car_model, license_exp_date
            person_car = person_data[0][2]

            try:
                # register new event in event log table with data you got (event type = free parking cell )
                cursor.execute(""" INSERT into event_log (person_id , event_type ,car)
               VALUES(? , ? , ?);
               """, (id, cmd, person_car))
                conn.commit()

            except sqlite3.Error as error:
                conn.close()
                print("Failed to Insert to  event_log tabel : ", error, "\n")
                return -1, -1, -1, -1  # fail car not found err

            # UPDATE parking status table
            cursor.execute(
                """ UPDATE parking_status SET status = 0 , taken_by = NULL WHERE taken_by = ? ;""", (id,))
            conn.commit()

            # conn.close() will be in calc_cost() function
            # return parking cell number + park cost info
            print("debug message : SUCCESS Database has been CHANGED!\n")
            # change to list [] if you want to easy overwrite
            return (cell_data[0], True, *calc_cost(id, person_car, conn))

        else:
            print("debug message : Wrong password Database has been CHANGED!\n")
            return -1, False, -1, -1  # FAIL PASSWORD DONT MATCH


###########################################################################

def db_check_ai_id(id_to_chk: str) -> bool:  # NOTE : still not tested
    """


    ------
    Returns :

    is_found

    in caller function / GUIyou must check if this found id is valid id in db is actually the right one

    by asking end user in GUI

    """

    is_found = True

    with connect_db() as db:
        cursor = db.cursor()
        cursor.execute(""" 	SELECT id FROM people_info
                           WHERE id = ?;
                     """, (id_to_chk,))

        temp = cursor.fetchall()

        if len(temp) == 0:
            is_found = False

    return is_found
###########################################################################
###########################################################################
# FUNCTIONS FOR OCR


def access_img_table(readOrwrite: bool, img_to_write: np.ndarray = None, img_name: str = "ref_id_img_hassan", ref_id_val: str = '54302518496307'):
    """
    *  readOrwrite == 0 ->read img
    *  readOrwrite == 1 ->write img

    ------
    Returns:

            None 	  => if readOrwrite == 1

            ref_img => if readOrwrite == 0
    """
    with connect_db() as conn:
        cursor = conn.cursor()

        if readOrwrite == 1:  # write
            encoded_img = img_to_write
            cursor.execute(
                """INSERT INTO reference_images  (img_name , img_data , Extracted_id)
                   VALUES (?,? ,?);
                """, (img_name, encoded_img, ref_id_val)
            )
            conn.commit()

        else:  # read
            cursor.execute(
                """ SELECT img_data FROM reference_images WHERE img_name = ?; """, (img_name,))
            ref_img_encoded = cursor.fetchone()[0]

            return ref_img_encoded


##########################################################################
##########################################################################

def db_cmd(cmd: int, id: str = "NULL", temp_password: str = 'None'):
    ''' this is the main database fucntion and what other parts of code will see and use 99% of time

    cmd == 0 => park car

    cmd == 1 => get car

    cmd == 2 => is_full?

    Returns:

    if cmd == 0 => cell_id or -1 if full

    if cmd == 1 => (cell_id , is_pass_ok , cost_le , time_hour) or (-1 , False , -1 , -1) if fail

    if cmd == 2 => True or False
    '''

    conn = connect_db()
    if cmd == 0:  # park car command
        return park_car_db(conn, cmd, id, temp_password)
    elif cmd == 1:  # get car FROM park command ( free a cell )
        return get_car_db(conn, cmd, id, temp_password)
    elif cmd == 2:
        return is_full()


###########################################################################
if __name__ == "__main__":
    # TEST YOUR CODE
   #   build_db()  # build the sqlite3 db for fist time ( IF BUILT BEFORE SQLITE3 ERROR WILL BE raised )

    # Example: is full
   #  print(db_cmd(2))

    # #   Example: park new car with driver id = 54302518496307
    db_cmd(0 , str(54302518496307), "1234")

#     # wait 30 sec so  we can round it up to 1 houre == 3 pounds cost
#    time.sleep(2)

# #  #Example: free a car with driver id = 54302518496307
#    cell_id_pass_cost_time = db_cmd(1, str(54302518496307), "1234")
#    print("CELL_ID TO FREE IS : ", cell_id_pass_cost_time[0])
#    print(" pass is ok? : ", cell_id_pass_cost_time[1])
#    print("Total prking cost : ", cell_id_pass_cost_time[2])
#    print("Total time on parking : ", cell_id_pass_cost_time[3])


