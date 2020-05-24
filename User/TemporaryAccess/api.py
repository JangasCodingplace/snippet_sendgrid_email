from django.template.loader import get_template
from django.contrib import auth

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
User = get_user_model()

from User.User.serializers import BaseUserSerializer

from .models import TemporaryAccess
from .serializers import TemporaryAccessSerializer

class RecreateActivationKeyAPI(GenericAPIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    serializer_class = TemporaryAccessSerializer

    def post(self, request):
        #t@active1.de
        # # #
        # Entry Data Validation
        #
        required_fields = [
            'email',
            'group'
        ]
        if [field for field in required_fields if field not in request.data] != []:
            data = {
                'err':'Invalid request data'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        if request.data['group'] != 'a':
            data = {
                'err':'Invalid request data'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        # 
        # ./Entry Data Validation
        # # #

        # # #
        # Query Validation
        #
        try:
            user = User.objects.get(
                email=request.data['email']
            )
            request.data['user'] = user.id
        except User.DoesNotExist:
            data = {
                'err':'Invalid User!'
            }
            return Response(data,status=status.HTTP_404_NOT_FOUND)
        
        if user.account_activated_by_key:
            data = {
                'err':'User Alreade activated by Email!'
            }
            return Response(data,status=status.HTTP_400_BAD_REQUEST)
        # 
        # ./Query Validation
        # # #



        temporary_access_serializer = self.get_serializer(
            data=request.data
        )

        if temporary_access_serializer.is_valid(raise_exception=True):
            access = temporary_access_serializer.save()

        return Response({},status=status.HTTP_200_OK)

@api_view(['POST',])
def create_access(request):
    """
    Required fields: email, group

    - - Required Field Documentation - - 
    email is a string which identify the user.

    group is a string which is responsable for access-key creation type.
    Take a look at .choices > ACCESS_GROUPS to see the key possibilities.
    Take also a look at .serializers > TemporaryAccessSerializer to see
    which keys are accepted at this method

    - - Validation & Success - - 

    Invalid Response can be created by
    - missing data
    - wrong group (currentely not accepted groups: a (Account activation))
    - not existing User

    Success Events:
    - Access Key gets created. By creation of a key a signal get triggered which sends
    a mail to user. In dependency which Email Service you use, take a look at
    the signals of your used email app for seeing the sended mail

    successfull Response:
    - Empty Response
    The current goal is not sending some validated data to the Frontend.
    By creating a key a email should be sended to the user the key is related to.
    """
    # # #
    # Entry Data Validation
    #
    required_fields = [
        'email',
        'group'
    ]
    if [field for field in required_fields if field not in request.data] != []:
        data = {
            'err':'Invalid request data'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    
    if request.data['group'] not in ['pw','l']:
        data = {
            'err':'Invalid request data'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    # 
    # ./Entry Data Validation
    # # #



    # # #
    # Query Validation
    #
    try:
        user = User.objects.get(
            email=request.data['email']
        )
        request.data['user'] = user.id
    except User.DoesNotExist:
        data = {
            'err':'Invalid User!'
        }
        return Response(data,status=status.HTTP_404_NOT_FOUND)
    # 
    # ./Query Validation
    # # #



    temporary_access_serializer = TemporaryAccessSerializer(
        data=request.data
    )

    if temporary_access_serializer.is_valid(raise_exception=True):
        access = temporary_access_serializer.save()

    return Response({},status=status.HTTP_200_OK)

@api_view(['POST',])
def get_access_by_key(request):
    """
    Required Fields: key, expected_group
    
    - - Required Field Documentation - - 

    key is a string which refers to the access model

    expected_group is a secure parameter. There are different access types.
    The access validation for each access type should be done by the different 
    frontend urls.
    That means that it should not be possible to validate an account activation 
    access from a password forgotten URL. It should only be possible to validate
    the account activation key from a section where account activation
    is expected.


    - - Validation & Success - - 

    Invalid Response can be created by
    - missing data
    - invalid expected keys
    - outdated keys

    Success Events:
    - user gets authenticated
    - key gets delete
    - response gets a session cookie

    successfull Response:
    - Baseuserserializer with user data and token
    - session cookie
    """
    # # #
    # Entry Data Validation
    #
    if 'key' not in request.data or 'expected_group' not in request.data:
        data = {
            'err':'Missing request data'
        }
        return Response(data,status=status.HTTP_400_BAD_REQUEST)
    # 
    # ./Entry Data Validation
    # # #


    # # #
    # Query Validation
    #
    try:
        access = TemporaryAccess.objects.get(key=request.data['key'])
    except TemporaryAccess.DoesNotExist:
        data = {
            'err':'Invalid access key!'
        }
        return Response(data,status=status.HTTP_404_NOT_FOUND)
    
    if not access.is_valid:
        access.delete()
        data = {
            'err':'Outdated access key!'
        }
        return Response(data,status=status.HTTP_406_NOT_ACCEPTABLE)

    if request.data['expected_group'] != access.group:
        data = {
            'err':'Invalid access key!'
        }
        return Response(data,status=status.HTTP_406_NOT_ACCEPTABLE)
    # 
    # ./Query Validation
    # # #



    # # #
    # Authentication + Cookie
    #
    auth.authenticate(
        request,
        user=access.user
    )

    # #
    # >> AccessKey get deleted
    access.delete()

    data = {
        'user':BaseUserSerializer(access.user).data
    }

    response = Response(data,status=status.HTTP_200_OK)

    max_age = int(settings.ENV['SESSION_COOKIE_VALIDATION_TIME'])
    expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=max_age)
    response.set_cookie(
        key='sessionid',
        value=request.session.session_key,
        expires=expires.strftime("%a, %d-%b-%Y %H:%M:%S UTC"),
        httponly=True,
        samesite='lax',
        path='/'
    )

    return response
