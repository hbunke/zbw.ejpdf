from plone.app.registry.browser import controlpanel
from zbw.ejpdf.interfaces import ICoverSettings


class CoverSettingsForm(controlpanel.RegistryEditForm):
    """
    """
    schema = ICoverSettings
    label = u"PDF Cover Settings"
    description = u"Configures PDF Cover generation"
    
    def updateFields(self):
        super(CoverSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(CoverSettingsForm, self).updateWidgets()

class CoverControlPanel(controlpanel.ControlPanelFormWrapper):
    form = CoverSettingsForm


