from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout

from .models import CustomUser
from .tokens import generate_token
from EnglishGrammarCheck import settings


def sign_up(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password_confirmation = request.POST["password_confirmation"]

        if CustomUser.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('sign_up')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('sign_up')

        if len(username) > 20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('sign_up')

        if password != password_confirmation:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('sign_up')

        # if not username.isalnum():
        #     messages.error(request, "Username must be Alpha-Numeric!!")
        #     return redirect('sign_up')

        my_user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        my_user.is_active = False
        my_user.save()
        messages.success(request,
                         "Your Account has been created succesfully!! Please check your email to confirm your email "
                         "address in order to activate your account.")

        # Welcome Email
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email EnglishGrammarCheck"
        message2 = render_to_string('email_confirmation.html', {

            'name': my_user.username,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': generate_token.make_token(my_user)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [my_user.email],
        )
        send_mail(email_subject, message2, from_email, to_list, fail_silently=True)

        return redirect('sign_in')

    return render(request, "sign_up.html")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        my_user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        my_user = None

    if my_user is not None and generate_token.check_token(my_user, token):
        my_user.is_active = True
        my_user.save()
        login(request, my_user)
        messages.success(request, "Your Account has been activated!!")
        return redirect('sign_in')
    else:
        messages.success(request, "Your Account has activation failed!!")
        return redirect('sign_up')


def sign_in(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            username = user.username
            return redirect("/")

        else:
            messages.error(request, "Bad Credentials!")
            return redirect("sign_in")
    return render(request, "sign_in.html")


def sign_out(request):
    logout(request)
    return redirect("sign_in")
