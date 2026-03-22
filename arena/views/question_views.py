from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import QuestionForm
from ..models import ArenaProfile, Question


def get_tier_by_capital(capital: int) -> str:
    if capital >= 60000:
        return ArenaProfile.TIER_CHALLENGER
    elif capital >= 30000:
        return ArenaProfile.TIER_MASTER
    elif capital >= 15000:
        return ArenaProfile.TIER_DIAMOND
    elif capital >= 7000:
        return ArenaProfile.TIER_PLATINUM
    elif capital >= 3000:
        return ArenaProfile.TIER_GOLD
    elif capital >= 1500:
        return ArenaProfile.TIER_SILVER
    return ArenaProfile.TIER_BRONZE


def get_latest_capital_for_user(user) -> int:
    if not user or not user.is_authenticated:
        return 0

    try:
        from main.models import LeaderboardEntry

        latest_entry = (
            LeaderboardEntry.objects
            .filter(user=user)
            .order_by("-created_at")
            .first()
        )
        if latest_entry and latest_entry.final_capital is not None:
            return int(latest_entry.final_capital)
    except Exception:
        pass

    try:
        arena_profile = getattr(user, "arena_profile", None)
        if arena_profile and arena_profile.best_capital is not None:
            return int(arena_profile.best_capital)
    except Exception:
        pass

    return 0


def ensure_arena_profile(user):
    if not user or not user.is_authenticated:
        return None
    profile, _ = ArenaProfile.objects.get_or_create(user=user)
    return profile


def sync_arena_profile_tier(user, capital: int, tier: str) -> None:
    if not user or not user.is_authenticated:
        return

    profile = ensure_arena_profile(user)
    if not profile:
        return

    profile.tier = tier

    if capital > (profile.best_capital or 0):
        profile.best_capital = capital

    profile.save(update_fields=["tier", "best_capital", "updated_at"])


@login_required(login_url="common:login")
def question_create(request):
    ensure_arena_profile(request.user)

    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.create_date = timezone.now()

            latest_capital = get_latest_capital_for_user(request.user)
            current_tier = get_tier_by_capital(latest_capital)

            sync_arena_profile_tier(request.user, latest_capital, current_tier)

            question.author_tier = current_tier
            question.save()
            form.save_m2m()

            messages.success(request, "Your post has been created.")
            return redirect("arena:index")
    else:
        form = QuestionForm()

    context = {"form": form}
    return render(request, "arena/question_form.html", context)


@login_required(login_url="common:login")
def question_modify(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.user != question.author:
        messages.error(request, "You do not have permission to edit this post.")
        return redirect("arena:detail", question_id=question.id)

    if request.method == "POST":
        old_image = question.image if question.image else None
        form = QuestionForm(request.POST, request.FILES, instance=question)

        if form.is_valid():
            remove_image = request.POST.get("remove_image") == "1"
            new_image_uploaded = bool(request.FILES.get("image"))

            edited_question = form.save(commit=False)

            if remove_image and not new_image_uploaded:
                edited_question.image = None

            edited_question.modify_date = timezone.now()
            edited_question.save()
            form.save_m2m()

            if remove_image and old_image:
                if edited_question.image != old_image:
                    try:
                        old_image.delete(save=False)
                    except Exception:
                        pass

            elif new_image_uploaded and old_image:
                if edited_question.image != old_image:
                    try:
                        old_image.delete(save=False)
                    except Exception:
                        pass

            messages.success(request, "Your post has been updated.")
            return redirect("arena:detail", question_id=edited_question.id)
    else:
        form = QuestionForm(instance=question)

    context = {"form": form, "question": question}
    return render(request, "arena/question_form.html", context)


@login_required(login_url="common:login")
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.user != question.author:
        messages.error(request, "You do not have permission to delete this post.")
        return redirect("arena:detail", question_id=question.id)

    if question.image:
        try:
            question.image.delete(save=False)
        except Exception:
            pass

    question.delete()
    messages.success(request, "Your post has been deleted.")
    return redirect("arena:index")


@login_required(login_url="common:login")
def question_vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.user == question.author:
        messages.error(request, "You cannot vote for your own post.")
    else:
        question.voter.add(request.user)
        messages.success(request, "Your vote has been recorded.")

    return redirect("arena:detail", question_id=question.id)