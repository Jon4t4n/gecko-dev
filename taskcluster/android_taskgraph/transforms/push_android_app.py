# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Apply some defaults and minor modifications to the jobs defined in the build
kind.
"""

from __future__ import absolute_import, print_function, unicode_literals

from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import resolve_keyed_by

transforms = TransformSequence()


@transforms.add
def resolve_keys(config, tasks):
    for task in tasks:
        for key in (
            "worker.channel",
            "worker.dep",
            "worker.certificate-alias",
            "worker.product",
            "routes",
        ):
            resolve_keyed_by(
                task,
                key,
                item_name=task["name"],
                **{
                    "build-type": task["attributes"]["build-type"],
                    "level": config.params["level"],
                }
            )
        yield task


@transforms.add
def add_startup_test(config, tasks):
    for task in tasks:
        if "nightly" not in task["attributes"].get("build-type", ""):
            yield task
            continue
        for dep_label, dep_task in config.kind_dependencies_tasks.items():
            if (
                dep_task.kind == "android-startup-test"
                and dep_task.attributes["shipping-product"]
                == task["attributes"]["shipping-product"]
            ):
                task["dependencies"]["android-startup-test"] = dep_label
        yield task
