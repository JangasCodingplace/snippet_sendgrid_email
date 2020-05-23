from django.template.loader import get_template
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

User = get_user_model()

@api_view(['POST',])
def password_forgotten_mail(request):
    if 'email' not in request.data:
        data = {
            'err':'Invalid request data'
        }
        eturn Response(data, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(
            email=request.data['email']
        )
        password_forgotten_mail_body = get_template('password_forgotten.html')
        context = {
            'user':user
        }

        mail = password_forgotten_mail.render(context)

    except User.DoesNotExist:
        pass
    return Response({},status=status.HTTP_200_OK)