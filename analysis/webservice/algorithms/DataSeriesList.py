# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json

from webservice.algorithms.NexusCalcHandler import NexusCalcHandler
from webservice.NexusHandler import nexus_handler
from webservice.webmodel import cached

import logging


logger = logging.getLogger(__name__)

@nexus_handler
class DataSeriesListCalcHandlerImpl(NexusCalcHandler):
    name = "Dataset List"
    path = "/list"
    description = "Lists datasets currently available for analysis"
    params = {}

    def __init__(self, tile_service_factory, remote_collections, **kwargs):
        super().__init__(tile_service_factory, **kwargs)
        self._remote_collections = remote_collections


    @cached(ttl=(60 * 60 * 1000))  # 1 hour cached
    def calc(self, computeOptions, **args):
        class SimpleResult(object):
            def __init__(self, result):
                self.result = result

            def toJson(self):
                return json.dumps(self.result)

        collection_list = self._get_tile_service().get_dataseries_list()

        # add remote collections
        for collection in self._remote_collections.values():
            collection_list.append(
                {
                    "shortName": collection["id"],
                    "remoteUrl": collection["path"],
                    "remoteShortName": collection["remote_id"] if 'remote_id' in collection else collection["id"]
                }
            )

        return SimpleResult(collection_list)
