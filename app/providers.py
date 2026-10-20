
"""Video footage providers for the B-roll engine."""
import requests
from pathlib import Path


class ProviderError(RuntimeError):
    pass


class PixabayProvider:
    name = "pixabay"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(
        self, query: str, avoid: list[str] | None = None, per_page: int = 10
    ) -> list[dict]:
        if not self.api_key:
            raise ProviderError("PIXABAY_API_KEY is not configured")

        response = requests.get(
            "https://pixabay.com/api/videos/",
            params={
                "key": self.api_key,
                "q": query,
                "per_page": min(per_page, 200),
                "safesearch": "true",
                "video_type": "all",
            },
            timeout=20,
        )
        response.raise_for_status()

        results = []
        for video in response.json().get("hits", []):
            video_options = video.get("videos") or {}

            # Prefer large footage, then fall back to smaller formats.
            selected = next(
                (
                    video_options.get(size)
                    for size in ("large", "medium", "small", "tiny")
                    if (video_options.get(size) or {}).get("url")
                ),
                None,
            )
            if not selected:
                continue

            creator = video.get("user", "Unknown")
            page_url = video.get("pageURL", "")

            results.append({
                "id": str(video.get("id", "")),
                "description": f"{video.get('tags', '')} {query}",
                "download_url": selected["url"],
                "source_url": page_url,
                "provider": "Pixabay",
                "creator": creator,
                "license": "Pixabay Content License; verify current terms",
                "attribution": f"Video by {creator} on Pixabay",
                "width": selected.get("width"),
                "height": selected.get("height"),
            })

        return results


class PexelsProvider:
    """Retained for projects that already have a valid Pexels API key."""
    name = "pexels"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(
        self, query: str, avoid: list[str] | None = None, per_page: int = 10
    ) -> list[dict]:
        if not self.api_key:
            raise ProviderError("PEXELS_API_KEY is not configured")

        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": self.api_key},
            params={
                "query": query,
                "per_page": per_page,
                "orientation": "landscape",
            },
            timeout=20,
        )
        response.raise_for_status()

        results = []
        for video in response.json().get("videos", []):
            user = video.get("user") or {}
            for vf in sorted(
                video.get("video_files", []),
                key=lambda x: x.get("width", 0),
                reverse=True,
            ):
                if not vf.get("link"):
                    continue
                results.append({
                    "id": str(video.get("id")),
                    "description": f"{video.get('url', '')} {query}",
                    "download_url": vf["link"],
                    "source_url": video.get("url", ""),
                    "provider": "Pexels",
                    "creator": user.get("name", "Unknown"),
                    "license": "Pexels License; verify current terms",
                    "attribution": f"Video by {user.get('name', 'Unknown')} on Pexels",
                    "width": vf.get("width"),
                    "height": vf.get("height"),
                })
                break
        return results


class MockProvider:
    """Test-only provider; its results must never be used as production footage."""
    name = "mock"

    def search(
        self, query: str, avoid: list[str] | None = None, per_page: int = 10
    ) -> list[dict]:
        return [
            {
                "id": f"mock-{i}-{query[:16]}",
                "description": query,
                "download_url": "",
                "source_url": "https://example.invalid/mock",
                "provider": "MockProvider",
                "creator": "Test fixture",
                "license": "TEST ONLY - not for production",
                "attribution": "Test fixture",
                "mock": True,
            }
            for i in range(per_page)
        ]


def get_provider(settings):
    provider = settings.footage_provider.lower()

    if provider == "mock":
        return MockProvider()
    if provider == "pixabay":
        return PixabayProvider(settings.pixabay_api_key)
    if provider == "pexels":
        return PexelsProvider(settings.pexels_api_key)

    raise ProviderError(f"Unsupported footage provider: {provider}")


def download_clip(candidate: dict, destination: Path) -> Path:
    if candidate.get("mock"):
        raise ProviderError(
            "Mock footage cannot be used to create a production video"
        )

    with requests.get(
        candidate["download_url"], stream=True, timeout=(10, 60)
    ) as response:
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if not (
            content_type.startswith("video/")
            or "octet-stream" in content_type
        ):
            raise ProviderError(
                f"Unexpected video content type: {content_type}"
            )

        with destination.open("wb") as file:
            for chunk in response.iter_content(1024 * 256):
                if chunk:
                    file.write(chunk)

    if destination.stat().st_size < 2048:
        destination.unlink(missing_ok=True)
        raise ProviderError("Downloaded clip is too small or corrupted")

    return destination
