# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from statik.utils import uncapitalize

__all__ = [
    'StatikErrorContext',
    'StatikError',
    'ProjectConfigurationError',
    'ModelError',
    'DataError',
    'ViewError',
    'TemplateError',
    'InternalError',
    'ReservedFieldNameError',
    'InvalidFieldTypeError',
    'MissingProjectFolderError',
    'MissingProjectConfig',
    'MissingParameterError',
    'DuplicateModelInstanceError',
    'InvalidModelCollectionDataError',
    'NoViewsError',
    'SafetyViolationError',
    'MissingTemplateError',
    'NoSupportedTemplateProvidersError',
    'MissingViewFieldError',
    'InvalidViewFieldTypeError',
    'MarkdownSyntaxError'
]


class StatikErrorContext(object):
    """Useful for representing context when exceptions are thrown (e.g. the name of
    the current file being processed, line number, etc.)"""
    
    def __init__(self, filename=None, line_no=None):
        self.filename = filename
        self.line_no = line_no

    def render(self):
        return ("in file \"%s\"%s" % (
            self.filename,
            (", line %d" % self.line_no) if self.line_no is not None else ""
        )) if self.filename else None
    
    def update(self, filename=None, line_no=None):
        self.filename = filename
        self.line_no = line_no
        
        # line number is irrelevant now if no filename
        if filename is None:
            self.filename, self.line_no = None, None
    
    def clear(self):
        self.filename, self.line_no = None, None


class StatikError(Exception):
    """A generic error class."""
    error_kind = "Error"
    error_message = "An exception occurred during processing. Please see the " \
        "debug output for more details."
    exit_code = 1

    def __init__(self, message=None, orig_exc=None, context=None):
        """Constructor.

        Args:
            message: An optional message to override the predefined error message.
            orig_exc: The original exception from which this error was generated.
            context: An optional ErrorContext instance to provide additional information during
                error rendering.
        """
        self.orig_exc = orig_exc
        if message is not None:
            self.error_message = message
        elif orig_exc is not None:
            # derive the error message from the original exception
            self.error_message = "%s" % orig_exc

        self.context = context or StatikErrorContext()
        if not isinstance(self.context, StatikErrorContext):
            raise TypeError("Statik error context must be of type StatikErrorContext")

    def render(self, context=None):
        """Renders the error message, optionally using the given context (which, if specified,
        will override the internal context)."""
        ctx = context.render() if context else self.get_error_context().render()
        return "%s: %s%s%s" % (
            self.get_error_kind(),
            self.get_error_message(),
            (" (%s)." % ctx) if ctx else "",
            self.get_additional_error_detail()
        )

    def __str__(self):
        return self.render()

    def __unicode__(self):
        return self.render()

    def get_error_kind(self):
        return self.error_kind

    def get_error_message(self):
        return self.error_message

    def get_error_context(self):
        return self.context

    def get_additional_error_detail(self):
        return (" Additional error detail: %s" % self.orig_exc) if self.orig_exc else ""


class ProjectConfigurationError(StatikError):
    """For generic project configuration-related errors."""
    error_kind = "Project configuration error"
    exit_code = 2


class ModelError(StatikError):
    error_kind = "Model error"
    exit_code = 3

    def __init__(self, model_name, **kwargs):
        super(ModelError, self).__init__(**kwargs)
        self.model_name = model_name

    def get_error_message(self):
        return "For model \"%s\", %s" % (
            self.model_name,
            self.error_message
        )


class DataError(StatikError):
    error_kind = "Data error"
    exit_code = 4

    def __init__(self, model_name, pk=None, **kwargs):
        super(DataError, self).__init__(**kwargs)
        self.model_name = model_name
        self.pk = pk
    
    def get_error_message(self):
        return "For model \"%s\",%s %s" % (
            self.model_name,
            (" pk=\"%s\", " % self.pk) if self.pk else "",
            self.error_message
        )


class TemplateError(StatikError):
    error_kind = "Template error"
    exit_code = 5


class ViewError(StatikError):
    error_kind = "View error"
    exit_code = 6

    def __init__(self, view_name=None, **kwargs):
        super(ViewError, self).__init__(**kwargs)
        self.view_name = view_name
    
    def get_error_message(self):
        return (
            "In view \"%s\", %s" % (self.view_name, uncapitalize(self.error_message))
        ) if self.view_name else self.error_message.capitalize()


class InternalError(StatikError):
    """In the (hopefully rare case) that an internal error occurs, this kind of error
    will be thrown. Will probably only happen when using Statik as a library."""
    error_kind = "Internal error"
    exit_code = 7


class ReservedFieldNameError(ModelError):
    def __init__(self, model_name, field_name, **kwargs):
        super(ReservedFieldNameError, self).__init__(model_name, **kwargs)
        self.field_name = field_name
        self.error_message = "the field name \"%s\" is reserved." % self.field_name


class InvalidFieldTypeError(ModelError):
    def __init__(self, model_name, field_name, expected_field_type=None, **kwargs):
        super(InvalidFieldTypeError, self).__init__(model_name, **kwargs)
        self.field_name = field_name
        self.expected_field_type = expected_field_type
        self.error_message = "field \"%s\" should be %s." % (
            self.field_name,
            self.expected_field_type
        ) if self.expected_field_type else \
        ("field \"%s\" is of an unrecognised type." % field_name)


class MissingProjectFolderError(ProjectConfigurationError):
    def __init__(self, folder, **kwargs):
        super(MissingProjectFolderError, self).__init__(
            message="The required project folder \"%s\" is missing." % folder,
            **kwargs
        )
        self.folder = folder


class MissingProjectConfig(ProjectConfigurationError):
    error_message = "A project configuration file (config.yml) is required in the root " + \
        "of the project folder."


class MissingParameterError(InternalError):
    def __init__(self, *names, **kwargs):
        super(MissingParameterError, self).__init__(
            message=("The required parameter \"%s\" is missing." % names[0]) if len(names) == 1 \
                else ("One or more of the following parameters is required: %s" % (
                    ", ".join(["\"%s\"" % name for name in names])
                )),
            **kwargs
        )
        self.names = names


class DuplicateModelInstanceError(DataError):
    error_message = "multiple instances were found, where all primary keys for a particular " + \
        "model instance must be unique."


class InvalidModelCollectionDataError(DataError):
    error_message = "invalid collection data has been specified, where it should be a list " + \
        "of instances."


class NoViewsError(ProjectConfigurationError):
    error_message = "Project has no views configured."


class SafetyViolationError(ViewError):
    error_message = "Queries in safe mode must be MLAlchemy-style queries."


class MissingTemplateError(TemplateError):
    def __init__(self, name=None, path=None, kind=None, **kwargs):
        super(MissingTemplateError, self).__init__(**kwargs)
        self.kind = kind
        self.name = name
        self.path = path
        if name is None and path is None:
            raise ValueError("Either one of \"name\" or \"path\" must be specified")

    def get_error_message(self):
        return "Cannot find %stemplate with %s \"%s\"." % (
            ("%s " % self.kind) if self.kind else "",
            "name" if self.name else "path",
            self.name if self.name else self.path
        )


class NoSupportedTemplateProvidersError(ProjectConfigurationError):
    def __init__(self, avail_providers, safe_mode=None, **kwargs):
        super(NoSupportedTemplateProvidersError, self).__init__(**kwargs)
        self.avail_providers = avail_providers
        self.safe_mode = safe_mode
    
    def get_error_message(self):
        return "No supported template providers in project configuration. " + \
            "Available template providers: %s%s" % (
                ", ".join(self.avail_providers),
                (" (safe mode=%s)" % self.safe_mode) if self.safe_mode is not None else ""
            )


class MissingViewFieldError(ViewError):
    def __init__(self, field_name, **kwargs):
        super(MissingViewFieldError, self).__init__(
            message="compulsory field \"%s\" is missing." % field_name,
            **kwargs
        )
        self.field_name = field_name


class InvalidViewFieldTypeError(ViewError):
    def __init__(self, field_name, expected_type, **kwargs):
        super(InvalidViewFieldTypeError, self).__init__(
            message="field \"%s\" is expected to be %s." % (field_name, expected_type),
            **kwargs
        )
        self.field_name = field_name
        self.expected_type = expected_type


class MarkdownSyntaxError(DataError):
    pass
