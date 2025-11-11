from graphene_file_upload.django import FileUploadGraphQLView
from django.views.decorators.csrf import csrf_exempt


class CustomGraphQLView(FileUploadGraphQLView):
    """Minimal custom GraphQL view with file upload + error formatting."""

    @staticmethod
    def format_error(error):
        formatted = error.formatted
        original = getattr(error, "original_error", None)
        if original is not None:
            formatted.setdefault("extensions", {}).setdefault("exception", {})[
                "type"
            ] = original.__class__.__name__
        return formatted

    @classmethod
    def as_view(cls, *args, **kwargs):
        # Mirror pattern: csrf_exempt(CustomGraphQLView.as_view(graphiql=True))
        view = super().as_view(*args, **kwargs)
        return csrf_exempt(view)
