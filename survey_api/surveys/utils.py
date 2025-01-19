from surveys.models import UserResponse


def has_user_completed_survey(user, survey):

    questions = survey.questions.all()
    user_responses = UserResponse.objects.filter(user=user, survey=survey)
    return user_responses.count() == questions.count()