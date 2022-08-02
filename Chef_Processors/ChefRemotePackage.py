#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""See docstring for ChefRemotePackage class."""

from __future__ import absolute_import

from autopkglib import Processor

__all__ = ["ChefRemotePackage"]


class ChefRemotePackage(Processor):
    description = "Produces a cpe_remote_package Chef block."
    input_variables = {
        "resource_name": {
            "required": True,
            "description": (
                "Name for the resource. This can be a single "
                "string or an array of strings. If an array is "
                "provided, the first item in the array will be the "
                "resource name and the rest will be turned "
                "into an array."
            ),
        },
        "resource_array": {
            "required": False,
            "description": "Does the resource_name represent an array variable?",
        },
        "app": {"required": False, "description": "Name of the app being installed."},
        "checksum": {"required": True, "description": "SHA256 checksum for package."},
        "cleanup": {
            "required": False,
            "description": (
                "Specify whether we should keep the downloaded package."
            ),
        },
        "pkg_name": {
            "required": False,
            "description": (
                "Name of the package if it is not the same as ",
                "`app`-`version`, or if the name has spaces.",
            ),
        },
        "receipt": {
            "required": True,
            "description": (
                "The package receipt to determine if it's already installed."
            ),
        },
        "remote": {
            "required": False,
            "description": (
                "Specify whether we should try to download the package."
            ),
        },
        "version": {
            "required": True,
            "description": (
                "The version of the package receipt to determine "
                "if it's already installed."
            ),
        },
        "only_if": {"required": False, "description": "only_if guard phrase."},
        "not_if": {"required": False, "description": "not_if guard phrase."},
        "extra_indentation": {
            "required": False,
            "description": "Indent this block. Defaults to empty.",
        },
        "indentation_end": {
            "required": False,
            "description": "Should this end an indented section? Defaults to empty.",
        },
    }
    output_variables = {"chef_block": {"description": "Chef block."}}

    __doc__ = description

    def main(self):
        # chef block variables
        prefix = ""
        block_name = "cpe_remote_pkg"

        # formatting variables
        extra_formatting = ""
        end_text = "end\n"
        self.env["chef_block"] = ""
        each_do_beginning = "[\n"
        each_do_end = ".each do |item|\n"
        self.env["chef_block"] = each_do_beginning
        indent_block = ""

        # Should this block be indented?
        if self.env.get(f"{prefix}extra_indentation"):
            self.output("Adding indentation.")
            indent_block = "  "
            end_text = f"  {end_text}"
            extra_formatting = "  "
        # Should this end an indented block?
        if self.env.get(f"{prefix}indentation_end"):
            end_text += "end\n"

        # Check to see if only one item was passed
        if len(self.env["resource_name"].split(",")) == 1:
            if self.env.get(f"{prefix}resource_array"):
                # it's a node variable representating an array
                self.env["chef_block"] = (
                    indent_block
                    + block_name
                    + " "
                    + self.env["resource_name"]
                    + each_do_end
                )
            else:
                self.env["chef_block"] = (
                    indent_block
                    + block_name
                    + " "
                    + self.env["resource_name"]
                    + " do\n"
                )
        else:
            for resource_name in self.env["resource_name"].split(","):
                self.env["chef_block"] += "  %s,\n" % resource_name
            self.env["chef_block"] += f"]{each_do_end}"
            # Remove trailing comma
            self.env["chef_block"] = self.env["chef_block"].replace(",\n]", "\n]")
            name = "item"
            self.env["chef_block"] += "%s %s do\n" % (block_name, name)
            # Insert an extra tab before everything
            extra_formatting = "  "
            end_text = indent_block + "end\n"

        input_list = sorted(self.input_variables.keys())
        # Start the block
        # Remove the indentation keys
        try:
            input_list.remove(f"{prefix}extra_indentation")
            input_list.remove(f"{prefix}indentation_end")
        except ValueError:
            pass
        # Place not_if guards first
        if self.env.get(f"{prefix}not_if"):
            notif_text = "not_if"
            self.env["chef_block"] += "%s  %s %s\n" % (
                extra_formatting,
                notif_text,
                self.env[f"{prefix}not_if"],
            )

            input_list.remove(f"{prefix}not_if")
        # Place only_if guards next
        if self.env.get(f"{prefix}only_if"):
            onlyif_text = "only_if"
            self.env["chef_block"] += "%s  %s %s\n" % (
                extra_formatting,
                onlyif_text,
                self.env[f"{prefix}only_if"],
            )

            input_list.remove(f"{prefix}only_if")
        # Remove the special keys
        try:
            input_list.remove(f"{prefix}resource_array")
            input_list.remove("resource_name")
        except ValueError:
            pass
        # Loop through all remaining keys
        for key in input_list:
            if self.env.get(key, ""):
                key_text = f'{key.replace(f"{prefix}", "")}'
                self.env["chef_block"] += "%s  %s %s\n" % (
                    extra_formatting,
                    key_text,
                    self.env[key],
                )
            # Clear out the key so it doesn't poison future runs
            self.env[key] = ""
        # end it
        self.env["chef_block"] += end_text
        self.output("Chef block:\n%s" % self.env["chef_block"])
        # Clean up the keys that weren't iterated through
        self.env[f"{prefix}extra_indentation"] = ""
        self.env[f"{prefix}indentation_end"] = ""
        self.env[f"{prefix}not_if"] = ""
        self.env[f"{prefix}only_if"] = ""


if __name__ == "__main__":
    PROCESSOR = ChefRemotePackage()
    PROCESSOR.execute_shell()
