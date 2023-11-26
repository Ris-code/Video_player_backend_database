from api.models import MyUser, Video


class AuthRouter:
    route_app_labels = ['auth', 'contenttypes', 'sessions', 'admin']

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'auth_db'
        
        if model == MyUser:
            return 'auth_db'

        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'auth_db'
        
        if model == MyUser:
            return 'auth_db'

        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
                obj1._meta.app_label in self.route_app_labels or
                obj2._meta.app_label in self.route_app_labels
        ):
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels or model_name == 'MyUser':
            return db == 'auth_db'
        
        return None
    
    
class AcmeAppRouter:
    route_app_labels = ['api']

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'video_db'

        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'video_db'

        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
                obj1._meta.app_label in self.route_app_labels or
                obj2._meta.app_label in self.route_app_labels
        ):
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels and model_name != 'MyUser':
            return db == 'video_db'
        return None