from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from django.conf import settings
from .models import User_tokens, User_resourceNames
from django.contrib.sessions.backends.db import SessionStore
import json
import requests
import traceback
# about ssl in django
# https://stackoverflow.com/questions/7610394/how-to-setup-ssl-on-a-local-django-server-to-test-a-facebook-app

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

# AUTHORIZATION_SCOPE = 'openid email profile'
AUTHORIZATION_SCOPE = settings.AUTHORIZATION_SCOPE

AUTH_REDIRECT_URI = settings.FN_AUTH_REDIRECT_URI
BASE_URI = settings.FN_BASE_URI
CLIENT_ID = settings.FN_CLIENT_ID
CLIENT_SECRET = settings.FN_CLIENT_SECRET

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'


def home(request):
    return render(request, 'home/home.html')


def is_logged_in(request):
    return True if AUTH_TOKEN_KEY in request.session else False


def build_credentials(s_key):
    # if not is_logged_in(request):
    #     raise Exception('User must be logged in')
    s = SessionStore(session_key=s_key)
    oauth2_tokens = s['auth_tokens']
    # oauth2_tokens = request.session[AUTH_TOKEN_KEY]
    print('refresh token: ', oauth2_tokens['refresh_token'])
    return google.oauth2.credentials.Credentials(
        oauth2_tokens['access_token'],
        refresh_token=oauth2_tokens['refresh_token'],
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=ACCESS_TOKEN_URI)


def build_credentials_from_refresh(refresh_token):
    return google.oauth2.credentials.Credentials(
        None,
        refresh_token=refresh_token,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=ACCESS_TOKEN_URI)


def get_user_info(s_key):
    credentials = build_credentials(s_key)

    oauth2_client = googleapiclient.discovery.build(
        'oauth2', 'v2',
        credentials=credentials)

    return oauth2_client.userinfo().get().execute()



def login(request):
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)

    uri, state = session.create_authorization_url(AUTHORIZATION_URL)
    request.session[AUTH_STATE_KEY] = state
    # s = SessionStore()
    # s['auth_state'] = state
    # s.create()
    # s_key = s.session_key
    # request.session['s_key'] = s_key
    # print('session2: ', request.session['crmuserid'])

    # print('----------------------')
    # print(request.session[AUTH_STATE_KEY])
    # print('----------------------')
    # request.session.permanent = True

    return redirect(uri, code=302)


def google_auth_redirect(request):
    try:
        req_state = request.GET.get('state')
        # print('----------------------')
        # print('req s_key: ', request.session['s_key'])
        # print('----------------------')
        # s_key = request.session['s_key']
        # s = SessionStore(session_key=s_key)
        #
        # if req_state != s['auth_state']:
        #     response = HttpResponse('no state key', code=401)
        #     return response
        session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                                scope=AUTHORIZATION_SCOPE,
                                # state=s['auth_state'],
                                state=req_state,
                                redirect_uri=AUTH_REDIRECT_URI)

        oauth2_tokens = session.fetch_access_token(
            ACCESS_TOKEN_URI,
            authorization_response=request.get_full_path())
        # request.session[AUTH_TOKEN_KEY] = oauth2_tokens
        s = SessionStore()
        s['auth_tokens'] = oauth2_tokens
        s.create()
        s_key = s.session_key

        user_info = get_user_info(s_key)
        print('user info: ', user_info['given_name'])
        print('session: ', request.session.items())
        # crmuserid = request.session["crmuserid"]
        # print('crmuserid info: ', crmuserid)

        # crmuserid = request.COOKIES.get('crmuserid')
        # print('crmuserid cookie: ', crmuserid)
        with open('crmuserid.txt', 'r') as f:
            crmuserid = f.read()
            print('crmuserid in file: ', crmuserid)
        user = User_tokens.objects.get(crmuserid=crmuserid)
        user.name = user_info['given_name']
        user.refresh_token = oauth2_tokens['refresh_token']
        # action_id = user.state_key
        user.save()
        # send_action_to_crm(action_id, 'true')
    except Exception as e:
        print(e)
        # with open('crmuserid.txt', 'r') as f:
        #     crmuserid = f.read()
        # user = User_tokens.objects.get(crmuserid=crmuserid)
        # action_id = user.state_key
        # send_action_to_crm(action_id, 'false', e)
    # return redirect(BASE_URI, code=302)
    return redirect('privacy_policy')


def get_client_ip(request):
    ip = request.META.get('REMOTE_ADDR')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # print('x_forwarded_for: ', x_forwarded_for)
    # data = {'REMOTE_ADDR': ip,
    #         'x_forwarded_for': x_forwarded_for}
    # r = requests.post("https://api.lavida.co.il:444/google/jiswy7t5i9hdeghe4dehujkgfu839i9idej37gaa2hdia3u8", json=data)
    # r = requests.post("https://hookb.in/VGO0EYRayqHX9Lm3gjJG", json=data)
    return x_forwarded_for

    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    #     ip = request.META.get('REMOTE_ADDR')
    #     print(ip)
    # return ip


def send_action_to_crm(action_id, action_success, err=None):
    # print('action check2: ', action_id)
    data = {'action_id': action_id,
            'action_success': action_success,
            'err': err}
    data_json = json.dumps(data)
    # print('data json: ', data_json)
    payload = {'json_payload': data_json}
    url = settings.ACTION_URL
    # https: // stackoverflow.com / questions / 8634473 / sending - json - request -with-python
    # https: // hookbin.com
    r = requests.post(url, json=data)
    r = requests.post("https://hookb.in/kxPe0mM6jdCma6pwz7qZ", json=data)


# def build_people_api_v1(request):
#
#     credentials = build_credentials(request)
#     return googleapiclient.discovery.build('people', 'v1', credentials=credentials)


def build_people_from_refresh(crmuserid):
    user = User_tokens.objects.get(crmuserid=crmuserid)
    refresh_token = user.refresh_token
    credentials = build_credentials_from_refresh(refresh_token)
    return googleapiclient.discovery.build('people', 'v1', credentials=credentials)


# def create_new_contact(request):
#     people_api = build_people_api_v1(request)
#     # https: // stackoverflow.com / questions / 46948326 / creating - new - contact - google - people - api
#     # http: // www.fujiax.com / stackoverflow_ / questions / 57538504 / google - people - api - in -python - gives - error - invalid - json - payload - received - unknown
#     contact1 = people_api.people().createContact(
#         body={"names": [{"givenName": "John", "familyName": "Doe"}],
#               "emailAddresses": [{"value": "jenny.doe@example.com"}],
#               "phoneNumbers": [{"value": "0547573120"}]
#               })
#     print('==============')
#     print(contact1)
#     # "phoneNumbers": [{"phoneNumber": "0547573120"}]
#     contact1.execute()
#     return {"names": [{"givenName": "John", "familyName": "Doe"}]}
    # people_api.people().createContact(contactToCreate).execute()



def google_contacts_app(request):
    crmuserid = request.GET.get('crmuserid')
    # action_id = request.GET.get('action_id')
    response = render(request, 'home/gcontacts.html')
    if crmuserid is not None:
        # user = User_tokens()
        user, created = User_tokens.objects.get_or_create(crmuserid=crmuserid)
        # user.state_key = action_id
        # user.crmuserid = crmuserid
        user.save()
        print('created: ', created)

        with open('crmuserid.txt', 'w') as f:
            f.write(crmuserid)
        request.session['crmuserid'] = crmuserid
        # response.set_cookie(key='crmuserid', value=crmuserid)
        # crmuserid = request.COOKIES.get('crmuserid')
        print('check1: ', crmuserid)
    # return redirect('login')
    return render(request, template_name='home/gcontacts.html')


def check_equal_phone(posted_phone, saved_phone):
    posted_phone = ''.join(filter(str.isdigit, posted_phone))
    saved_phone = ''.join(filter(str.isdigit, saved_phone))
    if posted_phone == saved_phone:
        return True
    else:
        return False


@csrf_exempt
def add_contact(request):
    if request.method == 'POST':
        client_ip = get_client_ip(request)
        # print('client_ip: ', client_ip)
        if client_ip == None or client_ip in settings.SAFE_IP:
            # print("safe ip: ", client_ip)

            try:
                data = json.loads(request.body.decode("utf-8"))
                action_id = data['action_id']
                # print('try action check: ', action_id)
                crmuserid = data['crmuserid']
                contact_name = data['contact_name']
                phone = data['phone']
                # email = data['email']
            except:
                action_id = request.POST.get('action_id')
                # print('except action check: ', action_id)
                crmuserid = request.POST.get('crmuserid')
                contact_name = request.POST.get('contact_name')
                phone = request.POST.get('phone')
                # email = request.POST.get('email')

            # try:
            print('crmuserid: ', crmuserid)
            people_api = build_people_from_refresh(crmuserid)



            #     user = User_tokens.objects.get(crmuserid=crmuserid)
            #     resourceName = user.state_key
            #     etag = user.email
            #     aContact = people_api.people().get(
            #         resourceName=resourceName,
            #         personFields='phoneNumbers'
            #     ).execute()
            #     print('aContact: ', aContact)
            #     if phone in aContact:
            #         contact = people_api.people().updateContact(
            #             resourceName=resourceName,
            #             body={
            #                   "etag": etag,
            #                   "names": [{"givenName": contact_name, "familyName": ""}],
            #                   "emailAddresses": [{"value": email}],
            #                   "phoneNumbers": [{"value": phone}]
            #                   },
            #             updatePersonFields="names,emailAddresses,phoneNumbers"
            #         )
            #         dict_resourceName = contact.execute()
            #         print('dict_resourceName: ', dict_resourceName)
            #         resourceName = dict_resourceName['resourceName']
            #         etag = dict_resourceName['etag']
            #         user.state_key = resourceName
            #         user.email = etag
            #         user.save()
            #         print('=====update======')
            #         # print(contact)
            # except Exception as e:
            #     print('exeption: ', e)
            # https: // stackoverflow.com / questions / 46948326 / creating - new - contact - google - people - api
            # http: // www.fujiax.com / stackoverflow_ / questions / 57538504 / google - people - api - in -python - gives - error - invalid - json - payload - received - unknown
            try:
                user = User_tokens.objects.get(crmuserid=crmuserid)
                # try:
                #     resourceNames = User_resourceNames.objects.filter(user=user).values_list('resource_name', flat=True)
                #     update_contact = people_api.people().getBatchGet(
                #         resourceNames=resourceNames,
                #         personFields='phoneNumbers'
                #     ).execute()
                #     print('update_contact: ', update_contact)
                #     if phone in str(update_contact):
                #         update_resource_name_dict = update_contact['responses']['person']
                #         resourceName = update_resource_name_dict['resourceName']
                #         etag = update_resource_name_dict['etag']
                #         contact = people_api.people().updateContact(
                #                         resourceName=resourceName,
                #                         body={
                #                               "etag": etag,
                #                               "names": [{"givenName": contact_name, "familyName": ""}],
                #                               },
                #                         updatePersonFields="names"
                #                     )
                #         dict_resourceName = contact.execute()
                #         print('dict_resourceName: ', dict_resourceName)
                # except Exception as e:
                #     print('e: ', e)
                connections = people_api.people().connections().list(resourceName='people/me', personFields='phoneNumbers', pageSize=2000).execute()
                # total = connections['totalItems']
                # if total<100:
                #     total =100
                phone_list = []
                # for _ in range(total//100):
                for d in connections['connections']:
                    etag = d['etag']
                    res_name = d['resourceName']
                    try:
                        c_phone = d['phoneNumbers'][0]['value']
                        phone_list.append(c_phone)
                        # if phone == c_phone:
                        if check_equal_phone(phone, c_phone):
                            contact = people_api.people().updateContact(
                                resourceName=res_name,
                                body={
                                    "etag": etag,
                                    "names": [{"givenName": contact_name, "familyName": ""}],
                                },
                                updatePersonFields="names"
                            )
                            dict_resourceName = contact.execute()
                            user_resource_name, created = User_resourceNames.objects.get_or_create(resource_name=res_name,
                                                                                                   user=user,
                                                                                                   defaults={'etag': etag})
                            # user_resource_name.user = user
                            # user_resource_name.resource_name = res_name
                            # user_resource_name.etag = etag
                            # user_resource_name.save()
                            print('=====update======')
                            # print('dict_resourceName: ', dict_resourceName)
                            send_action_to_crm(action_id, True)
                            return render(request, 'home/gcontacts.html')

                    except KeyError:
                        pass

                # print('len:', len(connections['connections']))
                # print('len:', len(phone_list))



                contact = people_api.people().createContact(
                    body={"names": [{"givenName": contact_name, "familyName": ""}],
                          "phoneNumbers": [{"value": phone}]
                          })
                print('=====new======')
                dict_resourceName = contact.execute()
                resourceName = dict_resourceName['resourceName']
                etag = dict_resourceName['etag']

                user_resource_name = User_resourceNames()
                user_resource_name.user = user
                user_resource_name.resource_name = resourceName
                user_resource_name.etag = etag
                user_resource_name.save()
                send_action_to_crm(action_id, True)
            except Exception as e:
                traceback.print_exc()
                send_action_to_crm(action_id, False, str(e))
            # send_action_to_crm('good ip', True, str(client_ip))
        else:
            return render(request, 'home/privacy_policy.html')
            # send_action_to_crm('bad ip', False, str(client_ip))

        return render(request, 'home/gcontacts.html')
    else:
        return render(request, 'home/gcontacts.html')


def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')


@csrf_exempt
def send_mail(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        message = request.POST.get('message')
        email = EmailMessage('sent from '+name, message + ' ' + str(phone), to=[email])
        email.send()
    return HttpResponse("")


@csrf_exempt
def action_check(request):
    # print(request)
    if request.method == 'POST':
        # print(json.loads(request.body))

        action = json.loads(request.body.decode("utf-8"))
        # action_success = request.POST.get('action_success')
        err = request.POST.get('err')
        # print('action: {} - success: {}'.format(action['action_id'], action['action_success']))
        # print('action: ', action)
    return render(request, 'home/privacy_policy.html')
