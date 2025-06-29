import copy
from typing import Iterable

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
OptionalBoundsType = BoxBounds | Iterable[BoxBounds] | None


def copy_bounds(bounds: OptionalBoundsType) -> OptionalBoundsType:
    if isinstance(bounds, BoxBounds):
        return copy.copy(bounds)
    elif isinstance(bounds, Iterable):
        return [copy_bounds(part) for part in bounds]
    elif bounds is None:
        return None
    else:
        raise RuntimeError(f'Unknown type: {type(bounds)}')


def duplicate_field(field: FormField) -> FormField:
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

        text_regions = None
        if field.text_field.text_regions is not None:
            text_regions = [copy_bounds(x) for x in field.text_field.text_regions]

        new_field = TextField(
            name=field.text_field.name,
            visual_region=copy_bounds(field.text_field.visual_region),
            checkbox_region=copy_bounds(field.text_field.checkbox_region),
            text_regions=text_regions,
            checkbox_text=field.text_field.checkbox_text,
            allow_copy=field.text_field.allow_copy,
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
            visual_region=copy_bounds(field.checkbox_field.visual_region),
            checkbox_region=copy_bounds(field.checkbox_field.checkbox_region),
        )
        return FormField(checkbox_field=new_field)

    elif field.multi_checkbox_field is not None:
        checkboxes = []
        for checkbox in field.multi_checkbox_field.checkboxes:
            checkboxes.append(
                MultiCheckboxOption(
                    name=checkbox.name,
                    region=copy_bounds(checkbox.region),
                    text_region=copy_bounds(checkbox.text_region),
                )
            )

        new_field = MultiCheckboxField(
            name=field.multi_checkbox_field.name,
            visual_region=copy_bounds(field.multi_checkbox_field.visual_region),
            validator=field.multi_checkbox_field.validator,
            checkboxes=checkboxes,
        )
        return FormField(multi_checkbox_field=new_field)

    else:
        raise RuntimeError(f'Field had no sub-fields: {field.id}')


def copy_reference_form(new_form: ReferenceForm, old_form: ReferenceForm, copy_details: bool = False) -> None:
    if copy_details:
        new_form.name = old_form.name
        new_form.path = old_form.path
        new_form.alignment_mark_count = old_form.alignment_mark_count
        new_form.linking_method = old_form.linking_method

    for region in old_form.regions.values():
        new_region = FormRegion(local_id=region.local_id, name=region.name)
        for field in region.fields:
            new_region.fields.append(duplicate_field(field))

        new_form.regions[new_region.local_id] = new_region
