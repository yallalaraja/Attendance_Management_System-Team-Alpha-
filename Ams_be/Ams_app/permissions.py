
class IsNotHoliday(BasePermission):
    message = "Today is a holiday — no need to login or punch in."

    def has_permission(self, request, view):
        return not Holiday.objects.filter(date=date.today()).exists()
