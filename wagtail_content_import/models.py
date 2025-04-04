from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.models import PagePermissionTester

from .mappers import get_default_mapper


class ContentImportMixin:
    """
    Mixin to allow a Page model to import content (currently from Google)
    """

    can_import = True

    mapper_class = get_default_mapper()

    @classmethod
    def create_from_import(cls, parsed_doc, user):
        """
        Factory method to create the Page and populate it from a parsed document.
        """
        page = cls(owner=user)
        page.update_from_import(parsed_doc, user)
        return page

    def update_from_import(self, parsed_doc, user):
        self.title = parsed_doc["title"]
        self.slug = slugify(self.title)
        mapper = self.mapper_class()
        self.body = mapper.map(parsed_doc["elements"], user=user)

    def permissions_for_user(self, user):
        if "content_import" in [p[0] for p in self.Meta.permissions]:
            return ContentImportPagePermissionTester(user, self)
        return super().permissions_for_user()

    class Meta:
        permissions = [
            ("content_import", _("Import")),
        ]


class ContentImportPagePermissionTester(PagePermissionTester):
    def can_import(self):
        if not self.user.is_active:
            return False
        if self.page_is_root:
            return False

        return self.user.is_superuser or ("content_import" in self.permissions)
