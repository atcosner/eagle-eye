import copy

from src.database.exporters.text_exporter import TextExporter
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.form_field import FormField
from src.database.fields.multi_checkbox_field import MultiCheckboxField
from src.database.fields.multi_checkbox_option import MultiCheckboxOption
from src.database.fields.text_field import TextField
from src.database.form_region import FormRegion
from src.database.reference_form import ReferenceForm
from src.database.validation.text_choice import TextChoice
from src.database.validation.text_validator import TextValidator
from src.util.types import BoxBounds

#
# TODO: THIS WHOLE FILE IS A BIG HACK!!!!
#


def offset_object(item: object, y_offset: int) -> object | None:
    if isinstance(item, BoxBounds):
        new_item = copy.copy(item)
        return new_item._replace(y=item.y + y_offset)
    elif isinstance(item, list):
        return [offset_object(part, y_offset) for part in item if offset_object(part, y_offset) is not None]
    else:
        return None


def create_field_with_offset(field: FormField, y_offset: int) -> FormField:
    if field.text_field is not None:
        new_exporter = None
        if field.text_field.text_exporter is not None:
            exporter = field.text_field.text_exporter
            new_exporter = TextExporter(
                no_export=exporter.no_export,
                export_field_name=exporter.export_field_name,
                prefix=exporter.prefix,
                suffix=exporter.suffix,
                strip_value=exporter.strip_value,
            )

        new_validator = None
        if field.text_field.text_validator is not None:
            validator = field.text_field.text_validator
            new_validator = TextValidator(
                datatype=validator.datatype,
                text_required=validator.text_required,
                text_regex=validator.text_regex,
                reformat_regex=validator.reformat_regex,
                error_tooltip=validator.error_tooltip,
                allow_closest_match_correction=validator.allow_closest_match_correction,
                text_choices=[TextChoice(c.text) for c in validator.text_choices],
            )

        # Remove allow_copy from the previous field
        allow_copy = field.text_field.allow_copy
        if allow_copy:
            field.text_field.allow_copy = False

        text_regions = [offset_object(x, y_offset) for x in field.text_field.text_regions] if field.text_field.text_regions is not None else None

        new_field = TextField(
            name=field.text_field.name,
            visual_region=offset_object(field.text_field.visual_region, y_offset),
            checkbox_region=offset_object(field.text_field.checkbox_region, y_offset),
            text_regions=text_regions,
            checkbox_text=field.text_field.checkbox_text,
            allow_copy=allow_copy,
            text_exporter=new_exporter,
            text_validator=new_validator,
        )
        return FormField(
            identifier=field.identifier,
            identifier_regex=field.identifier_regex,
            text_field=new_field,
        )

    elif field.checkbox_field is not None:
        new_field = CheckboxField(
            name=field.checkbox_field.name,
            visual_region=offset_object(field.checkbox_field.visual_region, y_offset),
            checkbox_region=offset_object(field.checkbox_field.checkbox_region, y_offset),
        )
        return FormField(checkbox_field=new_field)

    elif field.multi_checkbox_field is not None:
        checkboxes = []
        for checkbox in field.multi_checkbox_field.checkboxes:
            checkboxes.append(
                MultiCheckboxOption(
                    name=checkbox.name,
                    region=offset_object(checkbox.region, y_offset),
                    text_region=offset_object(checkbox.text_region, y_offset),
                )
            )

        new_field = MultiCheckboxField(
            name=field.multi_checkbox_field.name,
            visual_region=offset_object(field.multi_checkbox_field.visual_region, y_offset),
            validator=field.multi_checkbox_field.validator,
            checkboxes=checkboxes,
        )
        return FormField(multi_checkbox_field=new_field)

    else:
        return None


def copy_reference_form(new_form: ReferenceForm, old_form: ReferenceForm) -> None:
    for region in old_form.regions.values():
        new_region = FormRegion(local_id=region.local_id, name=region.name)
        for field in region.fields:
            if (new_field := create_field_with_offset(field, 0)) is not None:
                new_region.fields.append(new_field)
        new_form.regions[new_region.local_id] = new_region
