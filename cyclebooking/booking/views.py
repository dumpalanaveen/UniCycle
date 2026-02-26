from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Cycle, Booking, UserProfile
import math


def _generate_qr_svg(data: str) -> str:
    try:
        import qrcode
        import qrcode.image.svg
        import io
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(image_factory=factory)
        buf = io.BytesIO()
        img.save(buf)
        svg = buf.getvalue().decode('utf-8')
        svg = svg.replace("<?xml version='1.0' encoding='UTF-8'?>\n", '')
        return svg
    except Exception:
        pass


    amount = "N/A"
    ref = "N/A"
    for part in data.split('&'):
        if part.startswith("am="):
            amount = "Rs." + part[3:]
        if part.startswith("tn="):
            ref = part[3:]

    dots = ""
    for i in range(63):
        x = 74 + (i % 9) * 8
        y = 74 + (i // 9) * 8
        fill = "#000" if (i * 7 + i // 3) % 3 != 1 else "white"
        dots += f'<rect x="{x}" y="{y}" width="6" height="6" fill="{fill}"/>'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 220" width="220" height="220">
  <rect width="220" height="220" fill="white" rx="8"/>
  <rect x="10" y="10" width="56" height="56" fill="none" stroke="#000" stroke-width="4"/>
  <rect x="18" y="18" width="40" height="40" fill="none" stroke="#000" stroke-width="4"/>
  <rect x="26" y="26" width="24" height="24" fill="#000"/>
  <rect x="154" y="10" width="56" height="56" fill="none" stroke="#000" stroke-width="4"/>
  <rect x="162" y="18" width="40" height="40" fill="none" stroke="#000" stroke-width="4"/>
  <rect x="170" y="26" width="24" height="24" fill="#000"/>
  <rect x="10" y="154" width="56" height="56" fill="none" stroke="#000" stroke-width="4"/>
  <rect x="18" y="162" width="40" height="40" fill="none" stroke="#000" stroke-width="4"/>
  <rect x="26" y="170" width="24" height="24" fill="#000"/>
  {dots}
  <rect x="82" y="82" width="56" height="56" fill="white" rx="6"/>
  <text x="110" y="104" font-size="9" text-anchor="middle" fill="#5f259f" font-weight="bold" font-family="Arial">UPI</text>
  <text x="110" y="118" font-size="8" text-anchor="middle" fill="#333" font-family="Arial">unicycle@upi</text>
  <text x="110" y="131" font-size="9" text-anchor="middle" fill="#2563eb" font-weight="bold" font-family="Arial">{amount}</text>
</svg>"""
    return svg


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'booking/login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'booking/register.html')
        user = User.objects.create_user(
            username=username,
            email=request.POST['email'],
            password=request.POST['password'],
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
        )
        UserProfile.objects.create(
            user=user,
            roll_number=request.POST.get('roll_number', ''),
            department=request.POST.get('department', ''),
            phone=request.POST.get('phone', ''),
        )
        login(request, user)
        messages.success(request, 'Account created! Welcome to UniCycle!')
        return redirect('home')
    return render(request, 'booking/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def home_view(request):
    cycles = Cycle.objects.filter(status='available')
    return render(request, 'booking/home.html', {'cycles': cycles})


def cycle_detail_view(request, pk):
    cycle = get_object_or_404(Cycle, pk=pk)
    return render(request, 'booking/cycle_detail.html', {'cycle': cycle})


@login_required
def book_cycle_view(request, pk):
    cycle = get_object_or_404(Cycle, pk=pk, status='available')
    if request.method == 'POST':
        try:
            duration = int(request.POST.get('duration', 10))
        except ValueError:
            duration = 10
        if duration < 10:
            messages.error(request, 'Minimum booking duration is 10 minutes.')
            return redirect('cycle_detail', pk=pk)
        cost = round((duration / 10) * 3, 2)
        booking = Booking(user=request.user, cycle=cycle, duration_minutes=duration, total_cost=cost)
        booking.save()
        cycle.status = 'booked'
        cycle.save()
        return redirect('payment', booking_id=booking.id)
    return redirect('cycle_detail', pk=pk)


@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        booking.status = 'confirmed'
        booking.start_time = timezone.now()
        booking.save()
        messages.success(request, 'Payment confirmed! Your cycle is ready.')
        return redirect('booking_success', booking_id=booking.id)

    qr_svg = _generate_qr_svg(booking.qr_data)
    return render(request, 'booking/payment.html', {'booking': booking, 'qr_svg': qr_svg})


@login_required
def booking_success_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/booking_success.html', {'booking': booking})


@login_required
def return_cycle_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status not in ('confirmed', 'active'):
        messages.error(request, 'This booking cannot be returned.')
        return redirect('my_bookings')

    if request.method == 'POST':
        now = timezone.now()
        if booking.start_time:
            delta = now - booking.start_time
            actual_mins = max(10, math.ceil(delta.total_seconds() / 60))
        else:
            actual_mins = 10

        actual_mins = min(actual_mins, booking.duration_minutes)
        actual_cost = round((actual_mins / 10) * 3, 2)
        refund = round(max(0, float(booking.total_cost) - actual_cost), 2)

        booking.status = 'completed'
        booking.returned_at = now
        booking.actual_duration_minutes = actual_mins
        booking.refund_amount = refund
        booking.save()

        cycle = booking.cycle
        cycle.status = 'available'
        cycle.save()

        if refund > 0:
            messages.success(request, f'Cycle returned! Refund of Rs.{refund} will be processed to your account.')
        else:
            messages.success(request, 'Cycle returned successfully! Thank you.')
        return redirect('return_summary', booking_id=booking.id)

    if booking.start_time:
        delta = timezone.now() - booking.start_time
        used_mins = max(10, math.ceil(delta.total_seconds() / 60))
        used_mins = min(used_mins, booking.duration_minutes)
    else:
        used_mins = 10

    estimated_cost = round((used_mins / 10) * 3, 2)
    potential_refund = round(max(0, float(booking.total_cost) - estimated_cost), 2)

    return render(request, 'booking/return_cycle.html', {
        'booking': booking,
        'used_mins': used_mins,
        'estimated_cost': estimated_cost,
        'potential_refund': potential_refund,
    })


@login_required
def return_summary_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/return_summary.html', {'booking': booking})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u = request.user
        u.first_name = request.POST.get('first_name', '')
        u.last_name = request.POST.get('last_name', '')
        u.email = request.POST.get('email', '')
        u.save()
        profile.phone = request.POST.get('phone', '')
        profile.roll_number = request.POST.get('roll_number', '')
        profile.department = request.POST.get('department', '')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')
    return render(request, 'booking/profile.html', {'profile': profile})


@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})
