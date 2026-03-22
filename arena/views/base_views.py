from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from user.models import UserProfile
from arena.models import Question
from arena.forms import AnswerForm


def get_user_tier(user):
    if not user or not getattr(user, "is_authenticated", False):
        return "Bronze"

    try:
        arena_profile = getattr(user, "arena_profile", None)
        if arena_profile and getattr(arena_profile, "tier", None):
            return arena_profile.tier
    except Exception:
        pass

    return "Bronze"


def get_tier_badge_class(tier_name):
    mapping = {
        "Bronze": "tier-bronze",
        "Silver": "tier-silver",
        "Gold": "tier-gold",
        "Platinum": "tier-platinum",
        "Diamond": "tier-diamond",
        "Master": "tier-master",
        "Challenger": "tier-challenger",
    }
    return mapping.get(tier_name, "tier-bronze")


def get_or_create_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def needs_nickname_setup(user):
    if not user or not getattr(user, "is_authenticated", False):
        return False

    profile = get_or_create_user_profile(user)
    nickname = (profile.nickname or "").strip()
    return nickname == ""


def apply_sorting(question_list, sort_by):
    if sort_by == "recommend":
        return question_list.annotate(num_voter=Count("voter")).order_by("-num_voter", "-create_date")
    elif sort_by == "popular":
        return question_list.order_by("-views", "-create_date")
    return question_list.order_by("-create_date")


def index(request):
    page = request.GET.get("page", "1")
    kw = request.GET.get("kw", "").strip()
    search_option = request.GET.get("search_option", "all")
    sort_by = request.GET.get("sort_by", "recent")

    question_list = Question.objects.select_related(
        "author",
        "author__profile",
        "author__arena_profile",
    ).prefetch_related(
        "voter",
        "answers",
        "answers__author",
        "answers__author__profile",
        "answers__author__arena_profile",
    )

    if kw:
        if search_option == "title":
            question_list = question_list.filter(subject__icontains=kw)

        elif search_option == "content":
            question_list = question_list.filter(content__icontains=kw)

        elif search_option == "comment":
            question_list = question_list.filter(answers__content__icontains=kw)

        elif search_option == "nickname":
            question_list = question_list.filter(
                Q(author__profile__nickname__icontains=kw) |
                Q(author__username__icontains=kw)
            ).distinct()

        else:
            question_list = question_list.filter(
                Q(subject__icontains=kw) |
                Q(content__icontains=kw) |
                Q(answers__content__icontains=kw) |
                Q(author__profile__nickname__icontains=kw) |
                Q(author__username__icontains=kw) |
                Q(answers__author__profile__nickname__icontains=kw) |
                Q(answers__author__username__icontains=kw)
            ).distinct()

    question_list = apply_sorting(question_list, sort_by)

    paginator = Paginator(question_list, 25)
    page_obj = paginator.get_page(page)

    for question in page_obj:
        question.author_tier_class = get_tier_badge_class(question.author_tier)

    context = {
        "question_list": page_obj,
        "page": page,
        "kw": kw,
        "search_option": search_option,
        "sort_by": sort_by,
        "needs_nickname": needs_nickname_setup(request.user),
    }
    return render(request, "arena/question_list.html", context)


def detail(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related(
            "author",
            "author__profile",
            "author__arena_profile",
        ).prefetch_related(
            "voter",
            "answers",
            "answers__author",
            "answers__author__profile",
            "answers__author__arena_profile",
            "answers__voter",
        ),
        pk=question_id
    )

    question.views += 1
    question.save(update_fields=["views"])

    question.author_tier_class = get_tier_badge_class(question.author_tier)

    for answer in question.answers.all():
        answer.author_tier_class = get_tier_badge_class(answer.author_tier)

    form = AnswerForm()

    context = {
        "question": question,
        "form": form,
        "needs_nickname": needs_nickname_setup(request.user),
    }
    return render(request, "arena/question_detail.html", context)


@login_required(login_url="common:login")
@require_POST
def save_nickname(request):
    nickname = (request.POST.get("nickname") or "").strip()

    if not nickname:
        return JsonResponse({
            "ok": False,
            "error": "Please enter a nickname."
        }, status=400)

    if len(nickname) < 2:
        return JsonResponse({
            "ok": False,
            "error": "Nickname must be at least 2 characters."
        }, status=400)

    if len(nickname) > 30:
        return JsonResponse({
            "ok": False,
            "error": "Nickname must be 30 characters or fewer."
        }, status=400)

    profile = get_or_create_user_profile(request.user)

    duplicate = UserProfile.objects.exclude(user=request.user).filter(
        nickname__iexact=nickname
    ).exists()
    if duplicate:
        return JsonResponse({
            "ok": False,
            "error": "This nickname is already taken."
        }, status=400)

    profile.nickname = nickname
    profile.save(update_fields=["nickname", "nickname_changed_at"])

    return JsonResponse({
        "ok": True,
        "nickname": profile.nickname
    })