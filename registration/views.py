from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from chat.models import UserProfile


def SignUp(request):
    """
    This view handles the sign-up process.
    It validates the form data, creates a new user and user profile, and logs the user in.

    :param request: HttpRequest object
    :return: HttpResponse object
    """
    # Initialize an empty list to store error messages
    message = []

    # Check if the request method is POST
    if request.method == "POST":
        # If it is, instantiate the SignUpForm with the POST data
        form = SignUpForm(request.POST)

        # Check if the form data is valid
        if form.is_valid():
            # If it is, get the cleaned data
            name = form.cleaned_data.get('name')
            email = form.validate_email()
            username = form.validate_username()
            password = form.validate_password()

            # Check if the email, username, and password are valid
            if not email:
                # If the email is not valid, add an error message
                message.append("Email already registered!")
            elif not password:
                # If the password is not valid, add an error message
                message.append("Passwords don't match!")
            elif not username:
                # If the username is not valid, add an error message
                message.append("Username already registered!")
            else:
                # If all the data is valid, print a success message
                print("SUCCESS!!!!")

                # Save the form data to create a new user
                form.save()

                # Authenticate the user
                user = authenticate(username=username, password=password)

                # Log the user in
                login(request, user)

                # Create a new UserProfile instance
                profile = UserProfile(email=email, name=name, username=username)

                # Save the UserProfile instance
                profile.save()

                # Redirect the user to the home page
                return redirect("/")
    else:
        # If the request method is not POST, instantiate an empty SignUpForm
        form = SignUpForm()

    # Render the sign-up template with the form and error messages
    return render(request, "registration/signup.html", {"form": form, "heading": "Sign Up", "message": message})

