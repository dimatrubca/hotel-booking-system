import asyncio
import aiohttp

async def fetch(session, url):
    try:
        async with session.get(url, raise_for_status=True) as response:
            print(f"response: {response}\n\n")
            return  response
    except Exception as e:
        print("error...", e)

        return None




async def fetch_all(urls, loop):
    async with aiohttp.ClientSession(loop=loop) as session:
        try:
            results = await asyncio.gather(*[fetch(session, url) for url in urls], return_exceptions=True)
        except aiohttp.client_exceptions.ClientConnectionError as e:
            pass

        return results


def main():
    loop = asyncio.get_event_loop()

    urls = [
        'https://pypi.org/project/aiohttp/',
        'http://localhost:8055/docs'
    ]

    results = loop.run_until_complete(fetch_all(urls, loop))
    print("results: ", results)
    print(type(results[0]))
    print('...')
    print(results[1])

    # for res in results:
    #     print(type(res))
    #     print(res.status)

if __name__ == '__main__':
    main()