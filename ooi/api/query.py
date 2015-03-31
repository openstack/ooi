# -*- coding: utf-8 -*-

# Copyright 2015 Spanish National Research Council
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from ooi.api import base
from ooi.occi.core import entity
from ooi.occi.core import link
from ooi.occi.core import resource
from ooi.occi.infrastructure import compute
from ooi.occi.infrastructure import templates as infra_templates
from ooi.openstack import mixins
from ooi.openstack import templates


class Controller(base.Controller):
    def _resource_tpls(self, req):
        tenant_id = req.environ["keystone.token_auth"].user.project_id
        req = self._get_req(req, path="/%s/flavors/detail" % tenant_id)
        response = req.get_response(self.app)
        flavors = response.json_body.get("flavors", [])
        occi_resource_templates = []
        if flavors:
            for f in flavors:
                tpl = templates.OpenStackResourceTemplate(f["name"],
                                                          f["vcpus"],
                                                          f["ram"],
                                                          f["disk"])
                occi_resource_templates.append(tpl)
        return occi_resource_templates

    def _os_tpls(self, req):
        tenant_id = req.environ["keystone.token_auth"].user.project_id
        req = self._get_req(req, path="/%s/images/detail" % tenant_id)
        response = req.get_response(self.app)
        images = response.json_body.get("images", [])
        occi_os_templates = []
        if images:
            for i in images:
                tpl = templates.OpenStackOSTemplate(i["id"], i["name"])
                occi_os_templates.append(tpl)
        return occi_os_templates

    def index(self, req):
        l = []
        # OCCI Core Kinds:
        l.append(entity.Entity.kind)
        l.append(resource.Resource.kind)
        l.append(link.Link.kind)

        # OCCI infra Compute:
        l.append(compute.ComputeResource.kind)
        l.extend(compute.ComputeResource.actions)

        # OCCI infra mixins
        l.append(infra_templates.os_tpl)
        l.append(infra_templates.resource_tpl)

        # OpenStack flavors & images
        l.extend(self._resource_tpls(req))
        l.extend(self._os_tpls(req))

        # OpenStack mixins (contextualization)
        l.append(mixins.user_data)
        l.append(mixins.public_key)
        return l
