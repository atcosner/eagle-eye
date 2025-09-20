import copy
from typing import Iterable

from src.database.exporters.text_exporter import TextExporter
from src.database.fields.checkbox_field import CheckboxField
from src.database.fields.field_group import FieldGroup
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


def copy_bounds(bounds: OptionalBoundsType, y_offset: int) -> OptionalBoundsType:
    if isinstance(bounds, BoxBounds):
        new_bounds = copy.copy(bounds)
        return new_bounds._replace(y=bounds.y + y_offset)
    elif isinstance(bounds, Iterable):
        return [copy_bounds(part, y_offset) for part in bounds]
    elif bounds is None:
        return None
    else:
        raise RuntimeError(f'Unknown type: {type(bounds)}')


def duplicate_field(
        field: FormField,
        remove_copy: bool = False,
        y_offset: int = 0,
) -> FormField:
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

        if remove_copy:
            field.text_field.allow_copy = False

        text_regions = None
        if field.text_field.text_regions is not None:
            text_regions = [copy_bounds(x, y_offset) for x in field.text_field.text_regions]

        new_field = TextField(
            name=field.text_field.name,
            visual_region=copy_bounds(field.text_field.visual_region, y_offset),
            checkbox_region=copy_bounds(field.text_field.checkbox_region, y_offset),
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
            visual_region=copy_bounds(field.checkbox_field.visual_region, y_offset),
            checkbox_region=copy_bounds(field.checkbox_field.checkbox_region, y_offset),
        )
        return FormField(checkbox_field=new_field)

    elif field.multi_checkbox_field is not None:
        checkboxes = []
        for checkbox in field.multi_checkbox_field.checkboxes:
            checkboxes.append(
                MultiCheckboxOption(
                    name=checkbox.name,
                    region=copy_bounds(checkbox.region, y_offset),
                    text_region=copy_bounds(checkbox.text_region, y_offset),
                )
            )

        new_field = MultiCheckboxField(
            name=field.multi_checkbox_field.name,
            visual_region=copy_bounds(field.multi_checkbox_field.visual_region, y_offset),
            validator=field.multi_checkbox_field.validator,
            checkboxes=checkboxes,
        )
        return FormField(multi_checkbox_field=new_field)

    else:
        raise RuntimeError(f'Field had no sub-fields: {field.id}')


def copy_region(region: FormRegion, name: str, remove_copy: bool = False, y_offset: int = 0) -> FormRegion:
    new_region = FormRegion(local_id=region.local_id + 1, name=name)
    for group in region.groups:
        new_group = FieldGroup(
            name=group.name,
            visual_region=None if group.visual_region is None else copy_bounds(group.visual_region, y_offset),
            fields=[],
        )

        for field in group.fields:
            new_group.fields.append(duplicate_field(field, remove_copy=remove_copy, y_offset=y_offset))
        new_region.groups.append(new_group)

    return new_region


def copy_reference_form(new_form: ReferenceForm, old_form: ReferenceForm, copy_details: bool = False) -> None:
    if copy_details:
        new_form.name = old_form.name
        new_form.path = old_form.path
        new_form.alignment_method = old_form.alignment_method
        new_form.alignment_mark_count = old_form.alignment_mark_count
        new_form.linking_method = old_form.linking_method

    for region in old_form.regions.values():
        new_region = copy_region(region, region.name)
        new_form.regions[new_region.local_id] = new_region
