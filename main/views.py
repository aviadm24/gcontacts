from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from django.conf import settings
from .models import User_tokens
from django.contrib.sessions.backends.db import SessionStore
import json
import requests
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
    return redirect(BASE_URI, code=302)


def send_action_to_crm(action_id, action_success, err=''):
    print('action check2: ', action_id)
    data = {'action_id': action_id,
            'action_success': action_success,
            'err': err}
    data_json = json.dumps(data)
    payload = {'json_payload': data_json}
    url = settings.ACTION_URL
    # https: // stackoverflow.com / questions / 8634473 / sending - json - request -with-python
    r = requests.post(url, data=data_json)


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
    return response


@csrf_exempt
def add_contact(request):
    if request.method == 'POST':
        action_id = request.POST.get('action_id')
        print('action check: ', action_id)
        crmuserid = request.POST.get('crmuserid')
        contact_name = request.POST.get('contact_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        try:
            print('create contact function name: ', contact_name)
            people_api = build_people_from_refresh(crmuserid)
            # https: // stackoverflow.com / questions / 46948326 / creating - new - contact - google - people - api
            # http: // www.fujiax.com / stackoverflow_ / questions / 57538504 / google - people - api - in -python - gives - error - invalid - json - payload - received - unknown
            contact = people_api.people().createContact(
                body={"names": [{"givenName": contact_name, "familyName": ""}],
                      "emailAddresses": [{"value": email}],
                      "phoneNumbers": [{"value": phone}]
                      })
            print('==============')
            # print(contact)
            contact.execute()
            send_action_to_crm(action_id, 'true')
            # print('action check: ', action_id)
        except Exception as e:
            send_action_to_crm(action_id, 'false', e)

        return render(request, 'home/gcontacts.html', {'success': contact_name})


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
    print(request)
    if request.method == 'POST':
        # print(json.loads(request.body))

        action = json.loads(request.body.decode("utf-8"))
        # action_success = request.POST.get('action_success')
        err = request.POST.get('err')
        print('action: {} - success: {}'.format(action['action_id'], action['action_success']))
    return render(request, 'home/privacy_policy.html')
