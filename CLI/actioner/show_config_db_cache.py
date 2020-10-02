###########################################################################
#
# Copyright 2020 Dell, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###########################################################################


_DB_cache = {}


def cache_table(table, response):
    ''' Cache table

    Parameters:
    table(string): table path used as key
    response: response object returned from get api.

    Returns:
    '''
    _DB_cache.update({table: response})
    
    
def is_table_in_cache(table):
    ''' Check for table in cache,

    Parameters:
    table(string): table path used as key

    Returns:
    status(boo):
    '''
    if table in _DB_cache:
        return True
    return False    

def get_cached_table(table):
    ''' Get cached table

    Parameters:
    table(string): table path used as key

    Returns:
    response: table object 
    '''
    return _DB_cache.get(table, None)

def clear_cache():
    ''' Clear DB cache. Apps do not have to clear the cache.
        This is done by infra.
    '''

    return _DB_cache.clear()
