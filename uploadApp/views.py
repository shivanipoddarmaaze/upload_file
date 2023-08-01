from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import json
from .dboperations import *
from rest_framework.response import Response
from rest_framework import status
from .jwt import *
import requests
from django.http import HttpResponse


def get_file_extension(file_name):
    _, file_extension = os.path.splitext(file_name)
    return file_extension


def get_user(request):
    page_number = int(request.GET.get('page', 1))
    items_per_page = int(request.GET.get('item', 10))
    row = get_all_user(page_number, items_per_page)
    # paginator = Paginator(row[0][0], items_per_page)
    # result = paginator.get_page(page_number)
    # data = {
    #     'results': result.object_list,
    #     'total_records': paginator.count,
    #     'total_pages': paginator.num_pages,
    #     'page': result.number,
    #     'has_next': result.has_next(),
    #     'has_prev': result.has_previous()
    # }
    return JsonResponse({
        'current_page': page_number,
        'users': row,
    })


def upload_files(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        # names = ['1.pdf', '2.xlsx']
        for file in files:
            base_url = request.scheme + "://" + request.get_host()
            url = base_url + '/media/' + file.name
            name = file.name
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(name, file)
            file_type = get_file_extension(file.name)
            # user_data = json.loads(request.user_info['user'])
            created_by = 2
            have_access = [3, 5, 7]
            add_file(url, file_type, created_by, have_access, filename)
    return render(request, 'index.html')


def files(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        for file_data in data['data']:
            file = file_data['files']
            name = file_data['name'] if file_data['name'] != 'null' else file.name
            have_access = ast.literal_eval(file_data['access_by'])
            base_url = request.scheme + "://" + request.get_host()
            url = base_url + '/media/' + name
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(name, file)
            file_type = get_file_extension(file.name)
            user_data = json.loads(request.user_info['user'])
            created_by = user_data['user_id']
            add_file(url, file_type, created_by, have_access, filename)
        return JsonResponse({"result": 'file added'})
    elif request.method == 'PUT':
        data = json.loads(request.body.decode("utf-8"))
        file_id = data['id']
        new_file_name = data['name']
        have_access = ast.literal_eval(data['access_by'])
        file_data = edit_file(file_id, new_file_name, have_access)
        rename_file(file_data[0][0], new_file_name)
        base_url = request.scheme + "://" + request.get_host()
        url = base_url + '/media/' + new_file_name
        edit_file_url(file_id, url)
        return JsonResponse({"result": 'file edited'})
    page_number = int(request.GET.get('page', 1))
    items_per_page = int(request.GET.get('item', 10))
    row = get_all_files(page_number, items_per_page)
    # paginator = Paginator(row[0][0], items_per_page)
    # result = paginator.get_page(page_number)
    # data = {
    #     'results': result.object_list,
    #     'total_records': paginator.count,
    #     'total_pages': paginator.num_pages,
    #     'page': result.number,
    #     'has_next': result.has_next(),
    #     'has_prev': result.has_previous()
    # }
    return JsonResponse({
        'current_page': page_number,
        'users': row,
    })


def rename_file(old_file_name, new_file_name):
    old_file_path = os.path.join(settings.MEDIA_ROOT, old_file_name)
    new_file_path = os.path.join(settings.MEDIA_ROOT, new_file_name)

    try:
        os.rename(old_file_path, new_file_path)
        return True
    except FileNotFoundError:
        # Return a response if the old file does not exist
        return HttpResponse("Old file not found.", status=404)
    except Exception as e:
        # Return a response for any other errors
        return HttpResponse(str(e), status=500)


def userlogin(request):
    if request.method == 'POST':
        response = Response()
        data = json.loads(request.body.decode("utf-8"))
        # res,user_dict=login(data["user_id"],data["password"])
        print('"' + data['user_id'] + '"', '"' + data['password'] + '"')
        try:
            res = do_login(data['user_id'], data['password'])
            print("res", res)
            if res.get('status') == 0:
                data = {"message": res.get('msg'), 'status': 0, 'account_locked': 1}
                return Response(data, status=status.HTTP_200_OK)
            else:
                if res['agency_id'] is not None:
                    agency = get_agency_details_db(res["agency_id"])
                else:
                    agency = {"id_name": "", "agency_id": -1, "agency_name": "", "phone": ""}
                print("res", res)
                payload = {"uid": res['user_id'], "email": res['email'], "user": json.dumps(res),
                           "agency": json.dumps(agency)}
                print("payload", payload)

                access_token = create_jwt_token(settings.SECRET_KEY, payload, settings.TOKEN_EXP)
                refresh_token = create_jwt_token(settings.SECRET_KEY, payload, settings.TOKEN_EXP)
                response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
                dt = {
                    'status': 1,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': res,
                    'agency': agency
                }
            response.data = dt
        except ValueError as error:
            print("err", error)
            data = {"message": "Unauthorized access", 'status': 0, 'account_locked': 0}
            return Response(data, status=status.HTTP_200_OK)
        except RuntimeError as error:
            print(error)
            data = {"message": "Something went wrong.", 'status': 0, 'account_locked': 0}
            return Response(data, status=status.HTTP_200_OK)
        return JsonResponse(response.data)



        # response = Response()
        # data = json.loads(request.body.decode("utf-8"))
        # access_token = ''
        # refresh_token = ''
        # res = login(data["user_id"], data["password"])
        #
        # if res != "FAILURE":
        #     access_token = create_jwt_token(settings.SECRET_KEY, data["user_id"], 30)
        #     refresh_token = create_jwt_token(settings.SECRET_KEY, data["user_id"], 30)
        #     response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
        #
        # print(access_token, " ***** ")
        # response.data = {
        #     'access_token': access_token,
        #     'message': res,
        # }
        # # else :
        # #    data ={ "message":res }
        # #    return   Response(data, status=status.HTTP_200_OK)
        # return JsonResponse(response.data)


# return render(request, 'login.html')


# def register(request):
#     if request.method == 'POST':
#         # user_name = request.POST['uname']
#         # user_password = request.POST['upassword']
#         # data = json.loads(request.body.decode("utf-8"))
#         data = request.POST
#         print(type(data))
#         first_name = data["first_name"]
#         middle_name = data["middle_name"]
#         last_name = data["last_name"]
#         address = data["address"]
#         city = data["city"]
#         state = data["state"]
#         zipcode = data["zipcode"]
#         contact_number_office = data["contact_number_office"]
#         contact_number_mobile = data["contact_number_mobile"]
#         email = data["email"]
#         user_type_id = data["user_type_id"]
#         gender = data["gender"]
#         password = data["password"]
#
#         usr = User(first_name, middle_name, last_name, address, city, state, zipcode, contact_number_office,
#                    contact_number_mobile, email, user_type_id, gender, password)
#         res = add_user(usr)
#         # print(res)
#         data = {"message": res}
#         return Response(data, status=status.HTTP_200_OK)
#
#     return render(request, 'register.html')