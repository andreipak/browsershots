# browsershots.org - Test your web design in different browsers
# Copyright (C) 2007 Johann C. Rocholl <johann@browsershots.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.

"""
Request views.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

from datetime import datetime
from django.shortcuts import render_to_response
from django.db import connection
from shotserver04.requests.models import Request
from shotserver04.platforms.models import Platform
from shotserver04.browsers.models import BrowserGroup


def request_list(http_request):
    """
    Show statistics about pending requests.
    """
    browser_list = []
    cursor = connection.cursor()
    cursor.execute("""
SELECT platform_id, browser_group_id, major, minor,
SUM(browsers_browser.uploads_per_hour) AS uploads_per_hour,
SUM(browsers_browser.uploads_per_day) AS uploads_per_day
FROM browsers_browser
JOIN factories_factory ON factories_factory.id = factory_id
JOIN browsers_browsergroup ON browsers_browsergroup.id = browser_group_id
JOIN platforms_operatingsystem
ON platforms_operatingsystem.id = operating_system_id
GROUP BY platform_id, browser_group_id, major, minor
""")
    for row in cursor.fetchall():
        (platform_id, browser_group_id, major, minor,
         uploads_per_hour, uploads_per_day) = row
        pending_requests = Request.objects.filter(
            platform=platform_id,
            browser_group=browser_group_id,
            major=major,
            minor=minor,
            screenshot__isnull=True,
            request_group__expire__gt=datetime.now(),
            ).count()
        if not pending_requests:
            continue
        browser_list.append({
            'platform': Platform.objects.get(id=platform_id),
            'browser_group': BrowserGroup.objects.get(id=browser_group_id),
            'major': major,
            'minor': minor,
            'uploads_per_hour': uploads_per_hour,
            'uploads_per_day': uploads_per_day,
            'pending_requests': pending_requests,
            })
    return render_to_response('requests/list.html', locals())
