from tethys_sdk.base import TethysAppBase, url_map_maker


class InfiltrationModeling(TethysAppBase):
    """
    Tethys app class for Infiltration Modeling.
    """

    name = 'Infiltration Modeling'
    index = 'infiltration_modeling:home'
    icon = 'infiltration_modeling/images/icon.gif'
    package = 'infiltration_modeling'
    root_url = 'infiltration-modeling'
    color = '#27ae60'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='infiltration-modeling',
                controller='infiltration_modeling.controllers.home'
            ),
        )

        return url_maps