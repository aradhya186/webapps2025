from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction, OperationalError
from django.db.models import F, Q
from . import models
from payapp.forms import PointsTransferForm, PointsRequestForm
from .models import Points, PointsTransfer, PointsRequest
from django.contrib import messages
from django.views.decorators.csrf import requires_csrf_token
from register.forms import RegisterForm
from .utils import get_current_timestamp


# Create your views here.
@login_required(login_url='/')
def dashboard(request):
    default_src_username = request.user.username if request.user.is_authenticated else None
    requests =  PointsRequest.objects.select_related().filter(Q(enter_destination_username= default_src_username) & Q(transfer_status__in=['Pending']))
    if len(requests) > 0:
        messages.info(request, "You have "+ str(len(requests)) + " points requests")
    return render(request, "payapp/dashboard.html")

@requires_csrf_token
@login_required(login_url='/')
def request_points(request):
    default_src_username = request.user.username if request.user.is_authenticated else None
    if request.method == 'POST':
        form = PointsRequestForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["enter_destination_username"] == default_src_username:
                messages.error(request, "Can not request point to the same account.")
                return redirect('request_points')
            current_timestamp = get_current_timestamp()
            form.instance.date_time = current_timestamp
            form.instance.enter_your_username = default_src_username  # Set the value before saving
            user_points = Points.objects.select_related().get(name__username=default_src_username)
            form.instance.points_type = user_points.points_type
            form.save()
            messages.success(request, "Successfully sent request for points.")
            return redirect('request_points')
    form = PointsRequestForm()
    form = PointsTransferForm(initial={'enter_your_username': default_src_username})
    transfer_detail = PointsRequest.objects.select_related().filter((Q(enter_your_username= default_src_username)) | Q(enter_destination_username= default_src_username)).order_by('-id')  # Order by most recent first
    return render(request, "payapp/request.html", {"form": form, "point_detail" : transfer_detail, "user" : default_src_username})


@login_required(login_url='/')
def points(request):
    username = request.user.username
    src_points = Points.objects.select_related().get(name__username=username)
    transfer_detail = PointsTransfer.objects.select_related().filter(Q(enter_your_username=username) | Q(enter_destination_username= username)).order_by('-id')  # Order by most recent first
    return render(request, "payapp/points.html", {"src_points": src_points, "point_detail" : transfer_detail})


@requires_csrf_token
@login_required(login_url='/')
def points_transfer(request):
    if request.method == 'POST':
        form = PointsTransferForm(request.POST)

        if form.is_valid():
            src_username = request.user.username
            dst_username = form.cleaned_data["enter_destination_username"]
            points_to_transfer = form.cleaned_data["enter_points_to_transfer"]
            current_timestamp = get_current_timestamp()
            print(f"The current timestamp is: {current_timestamp}")
            if src_username == dst_username:
                messages.error(request, "Can not send money to the same account.")
                return redirect('points_transfer')
            try:
                with transaction.atomic():
                    src_points = Points.objects.select_related().get(name__username=src_username)
                    dst_points = Points.objects.select_related().get(name__username=dst_username)

                    # Retrieve currency types for source and destination users
                    src_currency_type = src_points.points_type
                    dst_currency_type = dst_points.points_type

                    # Convert points to transfer based on source user's currency type
                    points_to_transfer_converted = RegisterForm.conversion(src_currency_type, dst_currency_type, points_to_transfer)

                    src_points.points -= points_to_transfer
                    if src_points.points < 0:
                        messages.error(request, "Not enough points to transfer.")
                        return redirect('points_transfer')
                    src_points.save()

                    dst_points.points += points_to_transfer_converted
                    dst_points.save()
                    # Create and save a PointsTransfer instance
                    PointsTransfer.objects.create(
                        enter_your_username=src_username,
                        enter_destination_username=dst_username,
                        enter_points_to_transfer=points_to_transfer,
                        points_type = src_currency_type,
                        date_time = current_timestamp
                    )
                    messages.success(request, "Points transferred successfully.")

                    return redirect('points')
            except Points.DoesNotExist:
                messages.error(request, "User does not exist.")
            except OperationalError:
                messages.error(request, "Transfer operation is not possible now.")

        else:
            # If form is not valid, display form errors
            messages.error(request, "Form is not valid.")

    else:
        # Set default source username here
        default_src_username = request.user.username if request.user.is_authenticated else None
        form = PointsTransferForm(initial={'enter_your_username': default_src_username})

    return render(request, "payapp/pointstransfer.html", {"form": form})

def accept_request(request, request_id):
    points_request = PointsRequest.objects.get(pk=request_id)
    points_request.transfer_status = 'Approved'
    points_request.save()

    src_username = points_request.enter_destination_username
    dst_username = points_request.enter_your_username
    points_to_transfer = points_request.enter_points_to_transfer

    try:
        with transaction.atomic():
            src_points = Points.objects.select_related().get(name__username=src_username)
            dst_points = Points.objects.select_related().get(name__username=dst_username)

            src_currency_type = src_points.points_type
            dst_currency_type = dst_points.points_type

            points_to_transfer_converted = RegisterForm.conversion(dst_currency_type, src_currency_type,points_to_transfer)

            src_points.points -= points_to_transfer_converted
            if src_points.points < 0:
                messages.error(request, "Not enough points to transfer.")
                return redirect('request_points')
            src_points.save()

            dst_points.points += points_to_transfer
            dst_points.save()
            current_timestamp = get_current_timestamp()
            print(f"The current timestamp is: {current_timestamp}")
            PointsTransfer.objects.create(
                enter_your_username=dst_username,
                enter_destination_username=src_username,
                enter_points_to_transfer=points_to_transfer,
                points_type = src_currency_type,
                date_time = current_timestamp
            )

            messages.success(request, "Points transferred successfully.")

    except Points.DoesNotExist:
        messages.error(request, "User does not exist.")
    except OperationalError:
        messages.error(request, "Transfer operation is not possible now.")
    return redirect('request_points')

def reject_request(request, request_id):
    points_request = PointsRequest.objects.get(pk=request_id)
    points_request.transfer_status = 'Rejected'
    points_request.save()
    messages.success(request, "Request rejected Successfully")
    return redirect('request_points')