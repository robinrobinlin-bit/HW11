class WindyService:
    """
    Service class to handle configurations and embed links for Windy.com maps.
    """
    
    @staticmethod
    def get_embed_url(layer_name):
        """
        Returns the appropriate Windy.com embed iframe URL based on the layer name.
        """
        overlay = "wind"
        if layer_name == "雷達":
            overlay = "radar"
        elif layer_name == "天氣":
            overlay = "clouds"
            
        url = (
            f"https://embed.windy.com/embed2.html?"
            f"lat=23.7&lon=120.96&zoom=8&level=surface&overlay={overlay}"
            f"&menu=&message=&marker=&calendar=now&pressure="
            f"&type=map&location=coordinates&detail=&metricWind=default"
            f"&metricTemp=default&radarRange=-1"
        )
        return url
