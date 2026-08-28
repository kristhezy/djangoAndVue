from django.apps import AppConfig  # type: ignore
from django.db.models.signals import post_migrate  # type: ignore


class DjangoPlantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangoPlant'

    def ready(self):
        """Django 启动完成后：数据库性能优化 + Agent 预热"""
        from .ensure_db_performance import ensure_all
        post_migrate.connect(
            lambda sender, **kwargs: ensure_all(),
            weak=True,
        )
        try:
            from .ai_agent import prewarm_agent
            prewarm_agent()
        except Exception:
            pass  # 预热失败不影响启动（懒加载兜底）
