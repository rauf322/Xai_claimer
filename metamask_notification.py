async def find_metamask_page(context):
        metamask_page = None
        # Iterate through all open pages in the context
        for _page in context.pages:
            url: str = _page.url
            # print(f"Found page URL: {url}")
            # Check if the URL contains 'notification.html' (MetaMask notification page)
            if "notification.html" in url:
                metamask_page = _page
                break

        if metamask_page is None:
            raise RuntimeError("MetaMask notification page not found!")
        
        return metamask_page