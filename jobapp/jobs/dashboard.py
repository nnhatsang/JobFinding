from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard

class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        # Thêm các module vào dashboard
        self.children.append(modules.ModelList(
            title='Applications',
            models=('your_app.Application',),
        ))
        self.children.append(modules.ModelList(
            title='Jobs',
            models=('your_app.Job',),
        ))
        self.children.append(modules.ModelList(
            title='Curriculum Vitae',
            models=('your_app.Curriculum_Vitae',),
        ))
        self.children.append(modules.ModelList(
            title='Users',
            models=('your_app.User',),
        ))
# python manage.py sync_jet
