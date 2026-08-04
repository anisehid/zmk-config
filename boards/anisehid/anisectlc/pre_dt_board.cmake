# Copyright (c) 2024 The ZMK Contributors
# SPDX-License-Identifier: MIT

# Suppresses duplicate unit-address warning for power, clock, acl and flash-controller
list(APPEND EXTRA_DTC_FLAGS "-Wno-unique_unit_address_if_enabled")
