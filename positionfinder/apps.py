from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class PositionfinderConfig(AppConfig):
    name = 'positionfinder'
    
    def ready(self):
        """
        Initialize the application and apply any patches.
        This is called when the application is ready during Django startup.
        """
        logger.info("Initializing PositionfinderConfig")
        
        try:
            # We import and apply the chord search integration after 
            # all apps are loaded to avoid circular import issues
            import importlib
            search_integration = importlib.import_module('.search_integration', package=self.name)
            search_integration.apply_chord_search_integration()
        except Exception as e:
            logger.error(f"Error initializing chord search integration: {e}")
            import traceback
            logger.error(traceback.format_exc())
