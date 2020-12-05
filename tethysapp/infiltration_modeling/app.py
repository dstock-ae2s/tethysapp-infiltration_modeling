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
            UrlMap(
                name='curvenumber',
                url='infiltration-modeling/curvenumber',
                controller='infiltration_modeling.controllers.curvenumber'
            ),
            UrlMap(
                name='greenampt',
                url='infiltration-modeling/greenampt',
                controller='infiltration_modeling.controllers.greenampt'
            ),
            UrlMap(
                name='hortons',
                url='infiltration-modeling/hortons',
                controller='infiltration_modeling.controllers.hortons'
            ),
            UrlMap(
                name='philips',
                url='infiltration-modeling/philips',
                controller='infiltration_modeling.controllers.philips'
            ),
        )

        return url_maps