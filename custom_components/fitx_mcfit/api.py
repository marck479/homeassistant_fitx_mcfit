import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

FITX_STUDIO_URL = "https://fitx-proxy.daniel-stefan.dev"
MCFIT_STUDIO_URL = "https://rsg-group.api.magicline.com/connect/v1/studio?studioTags=AKTIV-391B8025C1714FB9B15BB02F2F8AC0B2"

class FitnessAPI:
    def __init__(self, provider, username, password):
        self.provider = provider
        self.session = aiohttp.ClientSession(headers={
            "x-tenant": "fitx" if provider == "fitx" else "mcfit"
        })
        self.auth = aiohttp.BasicAuth(username, password)

    async def get_studios(self):
        url = FITX_STUDIO_URL if self.provider == "fitx" else MCFIT_STUDIO_URL
        async with self.session.get(url, auth=self.auth) as resp:
            return await resp.json()

    async def get_occupancy(self, studio_id):
        if self.provider == "fitx":
            url = f"https://mein.fitx.de/nox/public/v1/studios/{studio_id}/utilization"
        else:
            url = f"https://rsg-group.api.magicline.com/connect/v1/studio/{studio_id}/current-occupancy"
        
        async with self.session.get(url, auth=self.auth) as resp:
            data = await resp.json()
            return next((i for i in data["items"] if i["isCurrent"]), {}).get("percentage", 0)
