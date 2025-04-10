from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction, OperationalError
from django.db.models import F, Q
from . import models
from payapp.forms import MoneyTransferForm, MoneyRequestForm
from .models import Money, MoneyTransfer, MoneyRequest
from django.contrib import messages
from django.views.decorators.csrf import requires_csrf_token
from register.forms import RegisterForm
from .utils import get_current_timestamp


# Create your views here.
@login_required(login_url='/')
def dashboard(request):
    default_src_username = request.user.username if request.user.is_authenticated else None
    requests =  MoneyRequest.objects.select_related().filter(Q(enter_destination_username= default_src_username) & Q(transfer_status__in=['Pending']))
    if len(requests) > 0:
        messages.info(request, "You have "+ str(len(requests)) + " money requests")
    return render(request, "payapp/dashboard.html")

@requires_csrf_token
@login_required(login_url='/')
def request_money(request):
    default_src_username = request.user.username if request.user.is_authenticated else None
    if request.method == 'POST':
        form = MoneyRequestForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["enter_destination_username"] == default_src_username:
                messages.error(request, "Can not request point to the same account.")
                return redirect('request_money')
            current_timestamp = get_current_timestamp()
            form.instance.date_time = current_timestamp
            form.instance.enter_your_username = default_src_username  # Set the value before saving
            user_money = Money.objects.select_related().get(name__username=default_src_username)
            form.instance.money_type = user_money.money_type
            form.save()
            messages.success(request, "Successfully sent request for money.")
            return redirect('request_money')
    form = MoneyRequestForm()
    form = MoneyTransferForm(initial={'enter_your_username': default_src_username})
    transfer_detail = MoneyRequest.objects.select_related().filter((Q(enter_your_username= default_src_username)) | Q(enter_destination_username= default_src_username)).order_by('-id')  # Order by most recent first
    return render(request, "payapp/request.html", {"form": form, "point_detail" : transfer_detail, "user" : default_src_username})


@login_required(login_url='/')
def money(request):
    username = request.user.username
    src_money = Money.objects.select_related().get(name__username=username)
    transfer_detail = MoneyTransfer.objects.select_related().filter(Q(enter_your_username=username) | Q(enter_destination_username= username)).order_by('-id')  # Order by most recent first
    return render(request, "payapp/money.html", {"src_money": src_money, "money_detail" : transfer_detail})


@requires_csrf_token
@login_required(login_url='/')
def money_transfer(request):
    if request.method == 'POST':
        form = MoneyTransferForm(request.POST)

        if form.is_valid():
            src_username = request.user.username
            dst_username = form.cleaned_data["enter_destination_username"]
            money_to_transfer = form.cleaned_data["enter_money_to_transfer"]
            current_timestamp = get_current_timestamp()
            print(f"The current timestamp is: {current_timestamp}")
            if src_username == dst_username:
                messages.error(request, "Can not send money to the same account.")
                return redirect('money_transfer')
            try:
                with transaction.atomic():
                    src_money = Money.objects.select_related().get(name__username=src_username)
                    dst_money = Money.objects.select_related().get(name__username=dst_username)

                    # Retrieve currency types for source and destination users
                    src_currency_type = src_money.money_type
                    dst_currency_type = dst_money.money_type

                    # Convert money to transfer based on source user's currency type
                    money_to_transfer_converted = RegisterForm.conversion(src_currency_type, dst_currency_type, money_to_transfer)

                    src_money.money -= money_to_transfer
                    if src_money.money < 0:
                        messages.error(request, "Not enough money to transfer.")
                        return redirect('money_transfer')
                    src_money.save()

                    dst_money.money += money_to_transfer_converted
                    dst_money.save()
                    # Create and save a MoneyTransfer instance
                    MoneyTransfer.objects.create(
                        enter_your_username=src_username,
                        enter_destination_username=dst_username,
                        enter_money_to_transfer=money_to_transfer,
                        money_type = src_currency_type,
                        date_time = current_timestamp
                    )
                    messages.success(request, "Money transferred successfully.")

                    return redirect('money')
            except Money.DoesNotExist:
                messages.error(request, "User does not exist.")
            except OperationalError:
                messages.error(request, "Transfer operation is not possible now.")

        else:
            # If form is not valid, display form errors
            messages.error(request, "Form is not valid.")

    else:
        # Set default source username here
        default_src_username = request.user.username if request.user.is_authenticated else None
        form = MoneyTransferForm(initial={'enter_your_username': default_src_username})

    return render(request, "payapp/moneytransfer.html", {"form": form})

def accept_request(request, request_id):
    money_request = MoneyRequest.objects.get(pk=request_id)
    money_request.transfer_status = 'Approved'
    money_request.save()

    src_username = money_request.enter_destination_username
    dst_username = money_request.enter_your_username
    money_to_transfer = money_request.enter_money_to_transfer

    try:
        with transaction.atomic():
            src_money = Money.objects.select_related().get(name__username=src_username)
            dst_money = Money.objects.select_related().get(name__username=dst_username)

            src_currency_type = src_money.money_type
            dst_currency_type = dst_money.money_type

            money_to_transfer_converted = RegisterForm.conversion(dst_currency_type, src_currency_type,money_to_transfer)

            src_money.money -= money_to_transfer_converted
            if src_money.money < 0:
                messages.error(request, "Not enough money to transfer.")
                return redirect('request_money')
            src_money.save()

            dst_money.money += money_to_transfer
            dst_money.save()
            current_timestamp = get_current_timestamp()
            print(f"The current timestamp is: {current_timestamp}")
            MoneyTransfer.objects.create(
                enter_your_username=dst_username,
                enter_destination_username=src_username,
                enter_money_to_transfer=money_to_transfer,
                money_type = src_currency_type,
                date_time = current_timestamp
            )

            messages.success(request, "Money transferred successfully.")

    except Money.DoesNotExist:
        messages.error(request, "User does not exist.")
    except OperationalError:
        messages.error(request, "Transfer operation is not possible now.")
    return redirect('request_money')

def reject_request(request, request_id):
    money_request = MoneyRequest.objects.get(pk=request_id)
    money_request.transfer_status = 'Rejected'
    money_request.save()
    messages.success(request, "Request rejected Successfully")
    return redirect('request_money')