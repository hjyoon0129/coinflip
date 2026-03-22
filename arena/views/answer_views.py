from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone

from main.models import LeaderboardEntry
from ..forms import AnswerForm
from ..models import Question, Answer, ArenaProfile


def get_latest_capital_for_user(user):
    latest = LeaderboardEntry.objects.filter(user=user).order_by("-created_at").first()
    if latest:
        return latest.final_capital
    return 1000


def get_tier_by_capital(capital):
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


def sync_arena_profile_tier(user, capital, tier):
    profile, _ = ArenaProfile.objects.get_or_create(user=user)
    profile.tier = tier
    if capital > profile.best_capital:
        profile.best_capital = capital
    profile.save(update_fields=["tier", "best_capital", "updated_at"])


@login_required(login_url='common:login')
def answer_create(request, question_id):
    """
    Create an answer in arena
    """
    question = get_object_or_404(Question, pk=question_id)

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.create_date = timezone.now()
            answer.question = question

            latest_capital = get_latest_capital_for_user(request.user)
            current_tier = get_tier_by_capital(latest_capital)
            sync_arena_profile_tier(request.user, latest_capital, current_tier)
            answer.author_tier = current_tier

            answer.save()

            messages.success(request, "Your answer has been posted.")

            return redirect(
                '{}#answer_{}'.format(
                    resolve_url('arena:detail', question_id=question.id),
                    answer.id
                )
            )
    else:
        form = AnswerForm()

    context = {
        'question': question,
        'form': form,
    }
    return render(request, 'arena/question_detail.html', context)


@login_required(login_url='common:login')
def answer_modify(request, answer_id):
    """
    Modify an existing answer
    """
    answer = get_object_or_404(Answer, pk=answer_id)

    if request.user != answer.author:
        messages.error(request, "You do not have permission to edit this answer.")
        return redirect('arena:detail', question_id=answer.question.id)

    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            edited_answer = form.save(commit=False)
            edited_answer.modify_date = timezone.now()
            edited_answer.save()

            messages.success(request, "Your answer has been updated.")

            return redirect(
                '{}#answer_{}'.format(
                    resolve_url('arena:detail', question_id=answer.question.id),
                    answer.id
                )
            )
    else:
        form = AnswerForm(instance=answer)

    context = {
        'answer': answer,
        'form': form,
    }
    return render(request, 'arena/answer_form.html', context)


@login_required(login_url='common:login')
def answer_delete(request, answer_id):
    """
    Delete an existing answer
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    question_id = answer.question.id

    if request.user != answer.author:
        messages.error(request, "You do not have permission to delete this answer.")
    else:
        answer.delete()
        messages.success(request, "Your answer has been deleted.")

    return redirect('arena:detail', question_id=question_id)


@login_required(login_url='common:login')
def answer_vote(request, answer_id):
    """
    Vote for an answer
    """
    answer = get_object_or_404(Answer, pk=answer_id)

    if request.user == answer.author:
        messages.error(request, "You cannot vote for your own answer.")
    else:
        answer.voter.add(request.user)
        messages.success(request, "Your vote has been recorded.")

    return redirect(
        '{}#answer_{}'.format(
            resolve_url('arena:detail', question_id=answer.question.id),
            answer.id
        )
    )