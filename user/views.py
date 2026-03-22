import json

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import NicknameForm
from .models import UserProfile


def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def is_duplicate_nickname(nickname, user):
    nickname = (nickname or "").strip()
    if not nickname:
        return False

    return UserProfile.objects.exclude(user=user).filter(
        nickname__iexact=nickname
    ).exists()


@login_required
def edit_nickname(request):
    profile = get_or_create_profile(request.user)
    next_url = request.GET.get("next") or request.POST.get("next") or "/"

    if request.method == "POST":
        form = NicknameForm(request.POST, instance=profile)

        if form.is_valid():
            new_nickname = (form.cleaned_data.get("nickname") or "").strip()

            if not new_nickname:
                return render(
                    request,
                    "user/edit_nickname.html",
                    {
                        "form": form,
                        "next": next_url,
                        "change_error": "Please enter a nickname.",
                    },
                )

            if profile.has_nickname() and not profile.can_change_nickname():
                return render(
                    request,
                    "user/edit_nickname.html",
                    {
                        "form": form,
                        "next": next_url,
                        "change_error": (
                            f"You can change your nickname only once every 30 days. "
                            f"{profile.days_until_nickname_change()} day(s) left."
                        ),
                    },
                )

            if is_duplicate_nickname(new_nickname, request.user):
                return render(
                    request,
                    "user/edit_nickname.html",
                    {
                        "form": form,
                        "next": next_url,
                        "change_error": "This nickname is already taken. Please choose another one.",
                    },
                )

            profile.nickname = new_nickname
            profile.nickname_changed_at = timezone.now()
            profile.save(update_fields=["nickname", "nickname_changed_at"])
            return redirect(next_url)
    else:
        form = NicknameForm(instance=profile)

    return render(
        request,
        "user/edit_nickname.html",
        {
            "form": form,
            "next": next_url,
        },
    )


@login_required
def save_nickname(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST only"}, status=400)

    profile = get_or_create_profile(request.user)
    form = NicknameForm(request.POST, instance=profile)

    if not form.is_valid():
        return JsonResponse({
            "ok": False,
            "errors": form.errors,
        }, status=400)

    new_nickname = (form.cleaned_data.get("nickname") or "").strip()

    if not new_nickname:
        return JsonResponse({
            "ok": False,
            "error": "Please enter a nickname.",
        }, status=400)

    if profile.has_nickname() and not profile.can_change_nickname():
        return JsonResponse({
            "ok": False,
            "error": "nickname_change_locked",
            "message": (
                f"You can change your nickname only once every 30 days. "
                f"{profile.days_until_nickname_change()} day(s) left."
            ),
            "days_left": profile.days_until_nickname_change(),
        }, status=400)

    if is_duplicate_nickname(new_nickname, request.user):
        return JsonResponse({
            "ok": False,
            "error": "nickname_taken",
            "message": "This nickname is already taken. Please choose another one.",
        }, status=400)

    profile.nickname = new_nickname
    profile.nickname_changed_at = timezone.now()

    try:
        profile.save(update_fields=["nickname", "nickname_changed_at"])
    except IntegrityError:
        return JsonResponse({
            "ok": False,
            "error": "nickname_taken",
            "message": "This nickname is already taken. Please choose another one.",
        }, status=400)

    return JsonResponse({
        "ok": True,
        "nickname": profile.nickname,
        "can_change_nickname": profile.can_change_nickname(),
        "days_left": profile.days_until_nickname_change(),
    })


@login_required
def api_me(request):
    profile = get_or_create_profile(request.user)

    return JsonResponse({
        "ok": True,
        "is_authenticated": True,
        "nickname": profile.nickname or "",
        "has_nickname": profile.has_nickname(),
        "can_change_nickname": profile.can_change_nickname(),
        "days_left": profile.days_until_nickname_change(),
        "next_change_at": (
            profile.next_nickname_change_at().isoformat()
            if profile.next_nickname_change_at()
            else None
        ),
    })


@login_required
def api_set_nickname(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("bad json")

    profile = get_or_create_profile(request.user)

    if profile.has_nickname() and not profile.can_change_nickname():
        return JsonResponse({
            "ok": False,
            "error": "nickname_change_locked",
            "message": (
                f"You can change your nickname only once every 30 days. "
                f"{profile.days_until_nickname_change()} day(s) left."
            ),
            "days_left": profile.days_until_nickname_change(),
        }, status=400)

    new_nickname = (data.get("nickname") or "").strip()

    form = NicknameForm(
        data={"nickname": new_nickname},
        instance=profile,
    )

    if not form.is_valid():
        nickname_errors = form.errors.get("nickname")
        message = nickname_errors[0] if nickname_errors else "Failed to save nickname."

        return JsonResponse({
            "ok": False,
            "error": "invalid_nickname",
            "message": message,
            "errors": form.errors,
        }, status=400)

    if not new_nickname:
        return JsonResponse({
            "ok": False,
            "error": "invalid_nickname",
            "message": "Please enter a nickname.",
        }, status=400)

    if is_duplicate_nickname(new_nickname, request.user):
        return JsonResponse({
            "ok": False,
            "error": "nickname_taken",
            "message": "This nickname is already taken. Please choose another one.",
        }, status=400)

    profile.nickname = new_nickname
    profile.nickname_changed_at = timezone.now()

    try:
        profile.save(update_fields=["nickname", "nickname_changed_at"])
    except IntegrityError:
        return JsonResponse({
            "ok": False,
            "error": "nickname_taken",
            "message": "This nickname is already taken. Please choose another one.",
        }, status=400)

    return JsonResponse({
        "ok": True,
        "nickname": profile.nickname,
        "can_change_nickname": profile.can_change_nickname(),
        "days_left": profile.days_until_nickname_change(),
    })