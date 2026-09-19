import argparse
import sys
from pathlib import Path


def update_pypi_index(
    package_name: str,
    tag: str,
    whl_url: str,
    tar_url: str,
    root_dir: Path = Path("."),
) -> None:
    version = tag.lstrip("v")

    # -------------------------------------------------------------
    # 1. Update or Create Root index.html
    # -------------------------------------------------------------
    root_index = root_dir / "index.html"
    if not root_index.exists():
        root_index.write_text(
            '<!DOCTYPE html>\n<html>\n  <head>\n    <meta name="pypi:repository-version" content="0.0.0">\n    <title>PyPI Index</title>\n  </head>\n  <body>\n  </body>\n</html>',
            encoding="utf-8",
        )

    root_html = root_index.read_text(encoding="utf-8")
    pkg_link = f'<a href="{package_name}/">{package_name}</a><br>'

    # Add package link to root index.html if not already present
    if f'href="{package_name}/"' not in root_html:
        if "</body>" in root_html:
            root_html = root_html.replace(
                "</body>", f"  {pkg_link}\n  </body>"
            )
        else:
            root_html += f"\n  {pkg_link}"
        root_index.write_text(root_html, encoding="utf-8")
        print(f"Added '{package_name}' to root index.html")
    else:
        print(f"'{package_name}' already exists in root index.html")

    # -------------------------------------------------------------
    # 2. Update or Create Package Subdirectory index.html
    # -------------------------------------------------------------
    pkg_dir = root_dir / package_name
    pkg_dir.mkdir(parents=True, exist_ok=True)
    pkg_index = pkg_dir / "index.html"

    if not pkg_index.exists():
        pkg_index.write_text(
            f"<!DOCTYPE html>\n<html>\n  <head>\n    <title>{package_name}</title>\n  </head>\n  <body>\n  </body>\n</html>",
            encoding="utf-8",
        )

    pkg_html = pkg_index.read_text(encoding="utf-8")

    # Construct standard wheel and tarball release names
    whl_name = f"{package_name}-{version}-py3-none-any.whl"
    tar_name = f"{package_name}-{version}.tar.gz"

    whl_link = f'<a href="{whl_url}">{whl_name}</a><br>'
    tar_link = f'<a href="{tar_url}">{tar_name}</a><br>'

    new_entries = []
    if whl_url not in pkg_html:
        new_entries.append(f"    {whl_link}")
    if tar_url not in pkg_html:
        new_entries.append(f"    {tar_link}")

    if new_entries:
        # Check if previous release links already exist in the file
        has_existing_links = "<a href" in pkg_html

        # Base block of entries
        block = "\n".join(new_entries) + "\n"

        # Prepend a newline only if there are already existing versions
        if has_existing_links:
            block = "\n" + block

        # Insert before closing tag
        if "  </body>" in pkg_html:
            pkg_html = pkg_html.replace("  </body>", f"{block}  </body>")
        elif "</body>" in pkg_html:
            pkg_html = pkg_html.replace("</body>", f"{block}</body>")
        else:
            pkg_html += f"\n{block}"

        pkg_index.write_text(pkg_html, encoding="utf-8")
        print(
            f"Added version {version} links to {package_name}/index.html"
        )
    else:
        print(
            f"Version {version} links are already present in {package_name}/index.html"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Update PEP 503 PyPI static index HTML files."
    )
    parser.add_argument(
        "--package_name",
        required=True,
        help="Package name",
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Release tag name e.g. v0.0.1",
    )
    parser.add_argument(
        "--whl_url",
        required=True,
        help="URL to wheel release",
    )
    parser.add_argument(
        "--tar_url",
        required=True,
        help="URL to tarball release",
    )

    args = parser.parse_args()

    update_pypi_index(
        package_name=args.package_name,
        tag=args.tag,
        whl_url=args.whl_url,
        tar_url=args.tar_url,
    )


if __name__ == "__main__":
    main()