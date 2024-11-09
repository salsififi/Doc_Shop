from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import HttpRequest
from django.shortcuts import render, redirect

from accounts.forms import UserForm
from accounts.models import Shopper

User = get_user_model()


def login_user(request: HttpRequest) -> HttpRequest:
    """Login view"""
    context = {"error": False}
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            context["error"] = True

    return render(request,
                  template_name="accounts/signin.html",
                  context=context)


def logout_user(request: HttpRequest) -> HttpRequest:
    """Logout view"""
    logout(request)
    return redirect("index")


def signup(request: HttpRequest) -> HttpRequest:
    """Signup view"""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = User.objects.create_user(email=email, password=password)
        login(request, user)
        return redirect('index')

    return render(request,
                  template_name="accounts/signup.html")


@login_required
def profile(request: HttpRequest) -> HttpRequest:
    """View to change personnal informations"""
    if request.method == "POST":
        is_valid = authenticate(email=request.POST.get("email"),
                                password=request.POST.get("password"))
        if is_valid:
            user: Shopper = request.user  # type: ignore
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.save()
            messages.add_message(request, level=messages.INFO,
                                 message="Les changements ont bien été enregistrés.")
        else:
            messages.add_message(request, level=messages.ERROR,
                                 message="Mot de passe non valide.")
        return redirect(profile)

    form = UserForm(initial=model_to_dict(request.user, exclude="password"))  # type: ignore
    addresses = request.user.addresses.all()
    return render(request,
                  template_name="accounts/profile.html",
                  context={"form": form, "addresses": addresses})
