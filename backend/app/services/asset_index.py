from typing import Dict, Optional

class AssetIndex:
    """
    Acts as the index for our 'Cloud Storage' of visual aids.
    Maps recognized intents or keywords to video filenames.
    """
    
    # In a real app, this would be a database or storage bucket listing
    _ASSETS = {
        "replace_filter": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4", # Placeholder for filter video
        "reset_device": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4", # Placeholder for reset video
        "error_e4": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4", # Placeholder
        "wifi_setup": "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4" # Placeholder
    }

    def get_visual_aid(self, intent: str) -> Optional[str]:
        return self._ASSETS.get(intent)
