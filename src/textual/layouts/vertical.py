from __future__ import annotations

from fractions import Fraction
from typing import cast, TYPE_CHECKING

from ..geometry import Region, Size
from .._layout import ArrangeResult, Layout, WidgetPlacement

if TYPE_CHECKING:
    from ..widget import Widget


class VerticalLayout(Layout):
    """Used to layout Widgets vertically on screen, from top to bottom."""

    name = "vertical"

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size
    ) -> ArrangeResult:

        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        parent_size = parent.outer_size

        styles = [child.styles for child in children if child.styles.height is not None]
        total_fraction = sum(
            [int(style.height.value) for style in styles if style.height.is_fraction]
        )
        fraction_unit = Fraction(size.height, total_fraction or 1)

        box_models = [
            widget._get_box_model(size, parent_size, fraction_unit)
            for widget in children
        ]

        margins = [
            max((box1.margin.bottom, box2.margin.top))
            for box1, box2 in zip(box_models, box_models[1:])
        ]
        if box_models:
            margins.append(box_models[-1].margin.bottom)

        y = Fraction(box_models[0].margin.top if box_models else 0)

        for widget, box_model, margin in zip(children, box_models, margins):
            content_width, content_height, box_margin = box_model
            offset_x = (
                widget.styles.align_width(
                    int(content_width), size.width - box_margin.width
                )
                + box_model.margin.left
            )
            next_y = y + content_height
            region = Region(offset_x, int(y), int(content_width), int(next_y) - int(y))
            add_placement(WidgetPlacement(region, widget, 0))
            y = next_y + margin

        total_region = Region(0, 0, size.width, int(y))
        add_placement(WidgetPlacement(total_region, None, 0))

        return placements, set(children)
