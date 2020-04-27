#
# Copyright © 2012 - 2020 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#


from django.utils.translation import gettext_lazy as _

from weblate.addons.base import BaseAddon
from weblate.addons.events import EVENT_COMPONENT_UPDATE, EVENT_UNIT_PRE_CREATE
from weblate.addons.forms import BulkEditAddonForm
from weblate.trans.bulk import bulk_perform
from weblate.trans.models import Unit
from weblate.utils.state import STATE_FUZZY, STATE_TRANSLATED


class FlagBase(BaseAddon):
    events = (EVENT_UNIT_PRE_CREATE,)
    icon = "flag.svg"

    @classmethod
    def can_install(cls, component, user):
        if not component.has_template():
            return False
        # Following formats support fuzzy flag, so avoid messing up with them
        if component.file_format in {"ts", "po", "po-mono"}:
            return False
        return super().can_install(component, user)


class SourceEditAddon(FlagBase):
    name = "weblate.flags.source_edit"
    verbose = _('Flag new source strings as "Needs editing"')
    description = _(
        "Whenever a new source string is imported from the VCS, it is "
        "flagged as needing editing in Weblate. This way you can easily "
        "filter and edit source strings written by the developers."
    )

    def unit_pre_create(self, unit):
        if unit.translation.is_template and unit.state >= STATE_TRANSLATED:
            unit.state = STATE_FUZZY


class TargetEditAddon(FlagBase):
    name = "weblate.flags.target_edit"
    verbose = _('Flag new translations as "Needs editing"')
    description = _(
        "Whenever a new translatable string is imported from the VCS, it is "
        "flagged as needing editing in Weblate. This way you can easily "
        "filter and edit translations created by the developers."
    )

    def unit_pre_create(self, unit):
        if not unit.translation.is_template and unit.state >= STATE_TRANSLATED:
            unit.state = STATE_FUZZY


class SameEditAddon(FlagBase):
    name = "weblate.flags.same_edit"
    verbose = _('Flag unchanged translations as "Needs editing"')
    description = _(
        "Whenever a new translatable string is imported from the VCS and it "
        "matches source strings, it is flagged as needing editing in Weblate. "
        "This is especially useful for file formats that include all strings "
        "even if they are not translated."
    )

    def unit_pre_create(self, unit):
        if (
            not unit.translation.is_template
            and unit.source == unit.target
            and "ignore-same" not in unit.all_flags
            and unit.state >= STATE_TRANSLATED
        ):
            unit.state = STATE_FUZZY


class BulkEditAddon(BaseAddon):
    events = (EVENT_COMPONENT_UPDATE,)
    name = "weblate.flags.bulk"
    verbose = _("Bulk edit")
    description = _("This addon allow to bulk edit flags, labels or state.")
    settings_form = BulkEditAddonForm
    multiple = True

    def component_update(self, component):
        label_set = component.project.label_set
        bulk_perform(
            None,
            Unit.objects.filter(translation__component=component),
            query=self.instance.configuration["q"],
            target_state=self.instance.configuration["state"],
            add_flags=self.instance.configuration["add_flags"],
            remove_flags=self.instance.configuration["remove_flags"],
            add_labels=label_set.filter(
                name__in=self.instance.configuration["add_labels"]
            ),
            remove_labels=label_set.filter(
                name__in=self.instance.configuration["remove_labels"]
            ),
        )
