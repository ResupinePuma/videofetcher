import asyncio, aiohttp
import requests
import re

class PSession(requests.Session):
    def __init__(self) -> None:
        self.results = []
        self.working_proxy_list = []
        self.proxy_list = self.get_proxy_list()
        super().__init__()

    def get_proxy_list(self):
        plist = requests.get("https://spys.me/proxy.txt")
        return [p for p in re.findall("\n([0-9.:]*)",plist.text) if p]

    async def __request(self, name, queue):
        method, url, kwargs = await queue.get()
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, **kwargs) as response:
                    #print(f"{name} Status:", response.status)               
                    response.text = await response.text()
                    response.proxy = kwargs["proxy"]
                    self.working_proxy_list.append(kwargs["proxy"])
                    self.results.append(response)
            except Exception as ex:
                #print(ex)
                pass
        queue.task_done()

    def request(self, method, url, **kwargs) -> requests.Response:
        self.working_proxy_list = []
        async def req(method, url, **kwargs):
            queue = asyncio.Queue()
            for p in self.proxy_list:
                nwargs = dict(kwargs)
                nwargs["proxy"] = f"http://{p}"
                data = (method, url, nwargs)
                queue.put_nowait(data)
            tasks = []
            for i in range(len(self.proxy_list)):
                task = asyncio.create_task(self.__request(i,queue))
                tasks.append(task)
            await queue.join()
            for task in tasks:
                task.cancel()
        asyncio.run(req(method, url, **kwargs))
        return self.results


    def get(self, url, filter=None, **kwargs):
        ress = self.request("GET", url, **kwargs)
        if filter:
            ress = [filter(r) for r in ress if r]
        if len(ress) > 0:
            ress = ress[0]
        return ress

    def post(self, url, filter=None, **kwargs):
        ress = self.request("POST", url, **kwargs)
        if filter:
            ress = [filter(r) for r in ress if r]
        if len(ress) > 0:
            ress = ress[0]
        return ress

if __name__ == "__main__":
    sess = PSession()
    resp = sess.get("https://ident.me/", timeout=5)
    print(resp)