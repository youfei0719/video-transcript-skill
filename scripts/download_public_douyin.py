#!/usr/bin/env python3
"""Download one user-authorized public Douyin video with an anonymous browser session."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
)
MAX_MEDIA_BYTES = 1024 * 1024 * 1024
VIDEO_ID_PATTERN = re.compile(r"/video/(\d+)|[?&]modal_id=(\d+)")


class DownloadError(RuntimeError):
    pass


def douyin_url(value: str) -> str:
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or not (
        host == "douyin.com" or host.endswith(".douyin.com")
    ):
        raise DownloadError("仅支持 user-provided douyin.com 分享链接")
    return value


def aweme_id(url: str) -> str:
    match = VIDEO_ID_PATTERN.search(url)
    if not match:
        raise DownloadError("无法从公开跳转地址识别抖音视频 ID")
    return next(value for value in match.groups() if value)


def media_urls(detail: dict, expected_id: str) -> list[str]:
    aweme = detail.get("aweme_detail")
    if not isinstance(aweme, dict) or str(aweme.get("aweme_id")) != expected_id:
        raise DownloadError("抖音详情响应与请求的视频不一致")
    video = aweme.get("video")
    if not isinstance(video, dict):
        raise DownloadError("抖音详情响应不包含视频信息")

    urls: list[str] = []

    def append(address: object) -> None:
        if not isinstance(address, dict):
            return
        values = address.get("url_list")
        if not isinstance(values, list):
            return
        for value in values:
            if isinstance(value, str) and urlparse(value).scheme == "https" and value not in urls:
                urls.append(value)

    append(video.get("play_addr"))
    append(video.get("download_addr"))
    for rate in video.get("bit_rate", []):
        if isinstance(rate, dict):
            append(rate.get("play_addr"))
    if not urls:
        raise DownloadError("抖音详情响应不包含可验证的 HTTPS 媒体地址")
    return urls


def resolve_detail(source_url: str, use_system_proxy: bool) -> tuple[str, dict]:
    launch_args = ["--disable-blink-features=AutomationControlled"]
    if not use_system_proxy:
        launch_args.append("--no-proxy-server")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=True,
            args=launch_args,
            timeout=30_000,
        )
        context = browser.new_context(user_agent=USER_AGENT)
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = context.new_page()
        try:
            page.goto(source_url, wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_timeout(7_000)
            canonical_url = page.url
            video_id = aweme_id(canonical_url)
            endpoint = (
                "https://www.douyin.com/aweme/v1/web/aweme/detail/"
                f"?aweme_id={video_id}"
            )
            last_error = "详情请求没有返回结果"
            for attempt in range(4):
                if attempt:
                    page.wait_for_timeout(2_000)
                try:
                    raw = page.evaluate(
                        """async ({ endpoint }) => {
                          const controller = new AbortController();
                          const timer = setTimeout(() => controller.abort(), 10000);
                          try {
                            const response = await fetch(endpoint, {
                              credentials: 'include', cache: 'no-store', signal: controller.signal
                            });
                            if (!response.ok) throw new Error(`HTTP ${response.status}`);
                            return await response.text();
                          } finally { clearTimeout(timer); }
                        }""",
                        {"endpoint": endpoint},
                    )
                    payload = json.loads(raw)
                    urls = media_urls(payload, video_id)
                    aweme = payload["aweme_detail"]
                    return canonical_url, {
                        "id": video_id,
                        "title": str(aweme.get("desc") or "抖音公开视频"),
                        "author": (aweme.get("author") or {}).get("nickname"),
                        "duration_ms": ((aweme.get("video") or {}).get("duration")),
                        "media_urls": urls,
                    }
                except (ValueError, DownloadError, PlaywrightTimeoutError) as error:
                    last_error = str(error)
            raise DownloadError(f"匿名抖音详情解析重试后仍失败：{last_error}")
        finally:
            context.close()
            browser.close()


def download_media(urls: list[str], referer: str, destination: Path, use_system_proxy: bool) -> None:
    session = requests.Session()
    session.trust_env = use_system_proxy
    session.headers.update({"User-Agent": USER_AGENT, "Referer": referer})
    last_error = "没有可用的媒体地址"
    for media_url in urls:
        downloaded = 0
        temp = destination.with_suffix(destination.suffix + ".partial")
        try:
            with temp.open("wb") as output:
                while True:
                    response = session.get(
                        media_url,
                        headers={"Range": f"bytes={downloaded}-"},
                        stream=True,
                        timeout=(20, 300),
                    )
                    response.raise_for_status()
                    content_type = response.headers.get("Content-Type", "")
                    if content_type and not (
                        content_type.startswith("video/")
                        or content_type == "application/octet-stream"
                    ):
                        raise DownloadError(f"媒体地址返回非视频内容：{content_type}")
                    length = response.headers.get("Content-Length")
                    if length and downloaded + int(length) > MAX_MEDIA_BYTES:
                        raise DownloadError("公开视频超过 1 GB 安全上限")
                    before = downloaded
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        downloaded += len(chunk)
                        if downloaded > MAX_MEDIA_BYTES:
                            raise DownloadError("公开视频超过 1 GB 安全上限")
                        output.write(chunk)
                    content_range = response.headers.get("Content-Range")
                    if not content_range:
                        break
                    range_match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
                    if not range_match:
                        raise DownloadError("媒体服务器返回无效 Content-Range")
                    start, end, total = map(int, range_match.groups())
                    if start != before or end < start or downloaded != end + 1 or total <= end:
                        raise DownloadError("媒体服务器返回不连续的字节范围")
                    if downloaded >= total:
                        break
            if downloaded == 0:
                raise DownloadError("媒体服务器返回空文件")
            temp.replace(destination)
            return
        except (OSError, requests.RequestException, DownloadError) as error:
            last_error = str(error)
            temp.unlink(missing_ok=True)
    raise DownloadError(f"签名媒体下载失败：{last_error}")


def run(source_url: str, output: Path) -> dict:
    errors: list[str] = []
    for use_system_proxy in (False, True):
        try:
            canonical_url, detail = resolve_detail(source_url, use_system_proxy)
            output.parent.mkdir(parents=True, exist_ok=True)
            download_media(detail.pop("media_urls"), canonical_url, output, use_system_proxy)
            return {
                "status": "ok",
                "source_url": canonical_url,
                "provider": "anonymous_chromium_signed_media",
                "output": str(output),
                **detail,
            }
        except DownloadError as error:
            errors.append(str(error))
    raise DownloadError("；".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="User-authorized public Douyin share URL")
    parser.add_argument("--output", required=True, type=Path, help="MP4 output path")
    args = parser.parse_args()
    try:
        print(json.dumps(run(douyin_url(args.url), args.output), ensure_ascii=False))
        return 0
    except DownloadError as error:
        print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
