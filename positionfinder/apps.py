import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class PositionfinderConfig(AppConfig):
    """App config: wires cache invalidation signals and the chord search integration."""

    name = "positionfinder"

    def ready(self) -> None:
        """
        Initialize the application and apply any patches.
        This is called when the application is ready during Django startup.
        """
        logger.info("Initializing PositionfinderConfig")

        # Rebuild the Studio catalogue whenever musical content changes (e.g. via the admin)
        from django.db.models.signals import post_delete, post_save

        from .views_studio import clear_catalog_cache

        for model_name in ("Notes", "Root", "ChordNotes"):
            model = self.get_model(model_name)
            post_save.connect(
                clear_catalog_cache, sender=model, dispatch_uid=f"studio_catalog_save_{model_name}"
            )
            post_delete.connect(
                clear_catalog_cache,
                sender=model,
                dispatch_uid=f"studio_catalog_delete_{model_name}",
            )

        try:
            # We import and apply the chord search integration after
            # all apps are loaded to avoid circular import issues
            import importlib

            search_integration = importlib.import_module(".search_integration", package=self.name)
            search_integration.apply_chord_search_integration()
        except Exception as e:
            logger.error(f"Error initializing chord search integration: {e}")
            import traceback

            logger.error(traceback.format_exc())
