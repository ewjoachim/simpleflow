# Copyright (c) 2013, Theo Crevon
# Copyright (c) 2013, Greg Leclercq
#
# See the file LICENSE for copying permission.

from __future__ import annotations

from simpleflow.swf.mapper.models.event.base import Event
from simpleflow.swf.mapper.models.event.compiler import CompiledEvent


class MarkerEvent(Event):
    _type = "Marker"

    marker_name: str
    cause: str


class CompiledMarkerEvent(CompiledEvent):
    _type = "Marker"
    states = ("recorded",)

    transitions = {}
    initial_state = "recorded"
