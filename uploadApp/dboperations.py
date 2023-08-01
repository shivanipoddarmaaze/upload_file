from django.db import connections
import psycopg2

conn = psycopg2.connect(database="falcondbnew2022", user="falconadmin", password="Nta@2022$$!",
                            host="falcondbnew2022.postgres.database.azure.com")
conn.autocommit = True
cur = conn.cursor()


def get_file(file_id):
    dbConnection = connections['default'].cursor()
    query = dbConnection.mogrify("SELECT get_file_data_as_json(%s);", (file_id,))
    dbConnection.execute(query)
    file_data = dbConnection.fetchall()
    return file_data


def get_file_by_id(file_id):
    query = "SELECT get_file_data_as_json(%s);"
    val = (file_id,)
    cur.execute(query, val)
    file_data = cur.fetchall()
    return file_data


def add_file(url, file_type, created_by, receiver, filename):
    group_id_str = ','.join(str(i) for i in receiver)
    query = f"SELECT shivani_add_files(%s, %s, %s, ARRAY[{group_id_str}]::integer[], %s);"
    val = (url, file_type, created_by, filename)
    cur.execute(query, val)
    return 'file added'


def edit_file_url(id, url):
    query = "SELECT shivani_edit_file_url(%s, %s);"
    val = (id, url)
    cur.execute(query, val)
    return 'file url edited'


def edit_file(file_id, name, have_access):
    group_id_str = ','.join(str(i) for i in have_access)
    query = f"SELECT shivani_edit_file_return_name(%s, %s, ARRAY[{group_id_str}]::integer[]);"
    val = (file_id, name)
    cur.execute(query, val)
    row = cur.fetchall()
    return row


def get_all_user(page_number, items_per_page):
    query = "SELECT shivani_get_all_users(%s, %s)"
    val = (page_number, items_per_page)
    cur.execute(query, val)
    row = cur.fetchall()
    return row


def get_all_files(page_number, items_per_page):
    query = "SELECT shivani_get_all_files(%s, %s)"
    val = (page_number, items_per_page)
    cur.execute(query, val)
    row = cur.fetchall()
    return row


def get_user_by_email(email):
    query = "SELECT shivani_get_user_by_email(%s)"
    val = (email,)
    cur.execute(query, val)
    row = cur.fetchall()
    return row


def validate_user_password(id):
    query = "SELECT shivani_validate_user_password(%s)"
    val = (id,)
    cur.execute(query, val)
    row = cur.fetchall()
    return row


def login(userid, pwd):
    # cursor = dbConnection.cursor()
    # cursor = ps_connection.cursor()
    logstatus = ''
    user_dict = {}

    try:
        cur.execute("select udf_user_login(%s, %s);", (userid, pwd))
        rows = cur.fetchall()
        # print(type(rows))
        # print(type(rows[0]))

        if len(rows) > 0:
            logstatus = "SUCCESS"
            user_dict = rows[0][0]
            print(user_dict)

        else:
            logstatus = 'FAILURE'
            # return logstatus


    except (Exception, psycopg2.DatabaseError) as error:

        logstatus = "Internal Server Error with database"
        logstatus = "FAILURE"
        print(error)
        # logstatus=error.__str__
    return logstatus, user_dict


def do_login(userid, password):
    rows = cur.execute("select udf_user_login(%s, %s);", (userid, password))
    result = cur.fetchall()
    print("result", result)
    if result is None:
        raise ValueError('Invalid credentials')
    if len(result) < 1:
        raise ValueError('Invalid credentials')
    return result[0][0]
    # try:
    #     # result = dbconnection.execute("select udf_user_login(%s, %s);", (userid, password))
    #     # dbConnection = connections['default'].cursor()
    #     # dbConnection.execute("select udf_user_login(%s, %s);", (userid, password))
    #     # rows = dbConnection.fetchall()
    #     # result = dbConnection.fetch_one_sp(SP.get('LOGIN'), [userid, password, 'ACCOUNTING'])
    #     dbConnection = connections['default'].cursor()
    #     # result = dbConnection.fetch_one_sp(SP.get('LOGIN'), [userid, password])
    #     # print(userid, password)
    #     rows = dbConnection.execute("select udf_user_login(%s, %s);", (userid, password))
    #     result = dbConnection.fetchall()
    #     print("result", result)
    #     if result is None:
    #         raise ValueError('Invalid credentials')
    #     if len(result) < 1:
    #         raise ValueError('Invalid credentials')
    #     return result[0][0]
    # except ValueError as error:
    #     raise ValueError(str(error))
    # except Exception as error:
    #     print(error)
    #     raise RuntimeError(str(error))


def get_agency_details_db(agency_id):
    # udf_get_liability_base_rate_and_territory_factor_json('107','AZ')
    # dbConnection = ps_connection.cursor()
    dbConnection = connections['default'].cursor()

    agency_info = {"id_name": '', "agency_id": -1, "agency_name": '', "phone": ''}

    try:

        query = dbConnection.mogrify("select udf_get_agency_details(%s);", (agency_id,))
        dbConnection.execute(query)
        rows = dbConnection.fetchall()
        # print(type(rows))
        # print(type(rows[0]))
        # print(rows, ' agency rows')
        if len(rows) > 0:
            id_name = rows[0][0].get('id_name')
            agency_id = rows[0][0].get('agency_id')
            agency_name = rows[0][0].get('agency_name')
            phone = rows[0][0].get('phone')
            # else:
            #    logstatus='FAILURE'
            # return logstatus
            agency_info = {"id_name": id_name, "agency_id": agency_id, "agency_name": agency_name, "phone": phone}


    except (Exception, psycopg2.DatabaseError) as error:

        log_errordata(error, 'test')
        print("err", error)
        agency_info = {"id_name": '', "agency_id": -1, "agency_name": '', "phone": ''}
        u_id = -1

    return agency_info


def log_errordata(exeption, user_logged):
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    line_no = str(line_number)

    log_data = filename + ' - ' + line_no
    remarks = exeption.__str__()
    user_logged = user_logged
    logged_userid = str(user_logged)
    try:
        dbConnection = connections['default'].cursor()
        dbConnection.execute("select udf_add_policy_event_log(%s,%s,%s);", (log_data, logged_userid, remarks,))
        dbConnection.commit()
        dbConnection.close()
    except:
        pass

# def add_user(user):
#     # cursor = dbConnection.cursor()
#     # cursor = ps_connection.cursor()
#     user_id = -1
#
#     u_t_id = get_user_type_id(user.user_type_id)
#
#     res = get_user_email_status(user.email)
#     if res != '':
#         return res
#     try:
#
#         dbConnection = connections['default'].cursor()
#         qry = dbConnection.mogrify('select udf_add_admin_user(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);',
#                                    (user.first_name,
#
#                                     user.middle_name,
#                                     user.last_name,
#                                     user.address,
#                                     user.city,
#                                     user.state,
#                                     user.zipcode,
#                                     user.contact_number_office,
#                                     user.contact_number_mobile,
#                                     user.email,
#                                     str(u_t_id),
#                                     user.password,
#                                     user.gender,
#                                     str(user.agency_id),
#                                     str(user_id)))
#
#         dbConnection.execute(qry.decode('utf-8'))
#
#         # ps_connection.commit()
#         dbConnection.commit()
#         # print("Completed")
#         rows = dbConnection.fetchall()
#         # print("Fetched")
#         # len(rows)
#         if len(rows) > 0:
#             user_id = rows[0][0]
#             if user_id > -1:
#                 res = "SUCCESS"
#             else:
#                 res = "FAILURE"
#
#     except Exception as error:
#
#         print(error)
#         res = "Internal Server Error"
#     return res