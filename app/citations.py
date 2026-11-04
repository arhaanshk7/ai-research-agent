MAX_SOURCES = 12


def build_numbered_sources(results, limit=MAX_SOURCES):
    """Turn raw search results into a clean, numbered source list."""

    sources = []
    seen_urls = set()

    for result in results or []:
        url = str(result.get("url") or "").strip()

        # Skip results without a URL, or URLs we already have
        if not url or url in seen_urls:
            continue

        seen_urls.add(url)

        title = str(result.get("title") or "").strip() or "Untitled source"
        date = str(result.get("published_date") or result.get("date") or "").strip()

        sources.append({
            "n": len(sources) + 1,
            "title": title,
            "url": url,
            "date": date,
        })

        if len(sources) == limit:
            break

    return sources


def format_references(sources):
    """Build the References section, one line per source."""

    if not sources:
        return ""

    lines = ["", "", "## References", ""]

    for source in sources:
        date = f" - {source['date']}" if source["date"] else ""

        lines.append(
            f"{source['n']}. {source['title']}{date} "
            f"- [Read source]({source['url']})"
        )

    return "\n".join(lines) + "\n"


def remove_model_references(report):
    """Remove any References/Sources section the LLM wrote (we add our own)."""

    references_headings = {
        "## references", "## sources",
        "# references", "# sources",
        "### references", "### sources",
        "#### references", "#### sources",
    }

    lines = report.splitlines()

    # Search from the bottom so we remove the last one the model wrote
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().lower() in references_headings:
            return "\n".join(lines[:i])

    return report


def validate_report(report, sources):
    """Clean the report and attach our own References section."""

    report = report or ""

    report = remove_model_references(report)
    report = report.rstrip()

    return report + format_references(sources)
