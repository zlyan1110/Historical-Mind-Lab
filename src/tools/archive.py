"""Historical archive search tool for agent knowledge retrieval.

This module provides RAG-lite functionality, allowing agents to query
a local JSON knowledge base for historical context, events, and locations.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HistoricalArchive:
    """Manages the historical knowledge base and provides search capabilities.

    Attributes:
        archive_path: Path to the history_facts.json file.
        data: Loaded historical data dictionary.
    """

    def __init__(self, archive_path: Optional[Path] = None) -> None:
        """Initialize the historical archive.

        Args:
            archive_path: Path to history_facts.json. If None, uses default location.
        """
        if archive_path is None:
            # Default to project root / data / history_facts.json
            project_root = Path(__file__).parent.parent.parent
            archive_path = project_root / "data" / "history_facts.json"

        self.archive_path = archive_path
        self.data: Dict[str, Any] = {}
        self._load_archive()

    def _load_archive(self) -> None:
        """Load historical data from JSON file.

        Logs a warning if file is missing but does not crash (per CLAUDE.md standards).
        """
        try:
            with open(self.archive_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            logger.info(f"Loaded historical archive from {self.archive_path}")
        except FileNotFoundError:
            logger.warning(
                f"Historical archive not found at {self.archive_path}. "
                "Agent will operate without historical context."
            )
            self.data = {"events": [], "locations": [], "figures": [], "survival_tips": []}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse historical archive: {e}")
            self.data = {"events": [], "locations": [], "figures": [], "survival_tips": []}

    def search_historical_context(
        self,
        year: Optional[int] = None,
        location: Optional[str] = None,
        month: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search for relevant historical context based on temporal and spatial filters.

        Args:
            year: Year to filter events (e.g., 548).
            location: Location name (Chinese or English, e.g., "建康" or "Jiankang").
            month: Month to filter events (1-12).
            tags: List of tags to filter by (e.g., ["siege", "military"]).

        Returns:
            Dictionary containing filtered events, locations, figures, and survival tips.

        Example:
            >>> archive = HistoricalArchive()
            >>> context = archive.search_historical_context(year=548, location="建康")
            >>> print(context['events'][0]['title'])
            '侯景叛乱开始'
        """
        results: Dict[str, List[Dict[str, Any]]] = {
            "events": [],
            "locations": [],
            "figures": [],
            "survival_tips": []
        }

        # Filter events
        for event in self.data.get("events", []):
            if year is not None and event.get("year") != year:
                continue
            if month is not None and event.get("month") != month:
                continue
            if location is not None:
                event_loc = event.get("location", "")
                event_loc_en = event.get("location_en", "")
                if location not in event_loc and location.lower() not in event_loc_en.lower():
                    continue
            if tags is not None:
                event_tags = event.get("tags", [])
                if not any(tag in event_tags for tag in tags):
                    continue

            results["events"].append(event)

        # Filter locations
        for loc in self.data.get("locations", []):
            if location is not None:
                ancient_name = loc.get("ancient_name", "")
                modern_name = loc.get("modern_name", "")
                name_en = loc.get("name_en", "")
                if (location in ancient_name or
                    location in modern_name or
                    location.lower() in name_en.lower()):
                    results["locations"].append(loc)
            else:
                results["locations"].append(loc)

        # Include relevant figures (always return all for now)
        results["figures"] = self.data.get("figures", [])

        # Filter survival tips
        for tip in self.data.get("survival_tips", []):
            # Survival tips are situation-based, include all for now
            results["survival_tips"].append(tip)

        logger.info(
            f"Search query [year={year}, location={location}, month={month}, tags={tags}] "
            f"returned {len(results['events'])} events, {len(results['locations'])} locations"
        )

        return results

    def get_location_info(self, location_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific location.

        Args:
            location_name: Ancient or modern name of the location.

        Returns:
            Location dictionary if found, None otherwise.

        Example:
            >>> archive = HistoricalArchive()
            >>> loc = archive.get_location_info("江陵")
            >>> print(loc['danger_level'])
            20
        """
        for loc in self.data.get("locations", []):
            if (location_name in loc.get("ancient_name", "") or
                location_name in loc.get("modern_name", "") or
                location_name.lower() in loc.get("name_en", "").lower()):
                return loc
        return None

    def get_events_by_date(self, year: int, month: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all events for a specific date.

        Args:
            year: Year to query.
            month: Optional month to narrow results.

        Returns:
            List of event dictionaries.
        """
        return self.search_historical_context(year=year, month=month)["events"]

    def get_timeline(self, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """Get chronological timeline of events within a year range.

        Args:
            start_year: Beginning year (inclusive).
            end_year: Ending year (inclusive).

        Returns:
            List of events sorted by date.
        """
        events = []
        for event in self.data.get("events", []):
            event_year = event.get("year")
            if event_year and start_year <= event_year <= end_year:
                events.append(event)

        # Sort by year, then month
        events.sort(key=lambda e: (e.get("year", 0), e.get("month", 0)))
        return events

    def assess_location_danger(
        self,
        location_name: str,
        current_year: int
    ) -> Dict[str, Any]:
        """Assess the danger level of a location at a specific time.

        Args:
            location_name: Name of the location to assess.
            current_year: Year to assess danger for.

        Returns:
            Dictionary with danger assessment and reasoning.

        Example:
            >>> archive = HistoricalArchive()
            >>> danger = archive.assess_location_danger("建康", 548)
            >>> print(danger['level'])
            90
        """
        loc_info = self.get_location_info(location_name)

        if not loc_info:
            logger.warning(f"No data for location: {location_name}")
            return {
                "level": 50,  # Default moderate danger
                "reasoning": "位置信息不详，谨慎行事。",
                "reasoning_en": "Location information unavailable, proceed with caution."
            }

        base_danger = loc_info.get("danger_level", 50)

        # Check if location is in safe period
        safe_start = loc_info.get("safe_period_start")
        safe_end = loc_info.get("safe_period_end")

        if safe_start and safe_end:
            if safe_start <= current_year <= safe_end:
                adjusted_danger = min(base_danger, 30)  # Safer during protected period
                return {
                    "level": adjusted_danger,
                    "reasoning": f"{loc_info['ancient_name']}在此期间相对安全。",
                    "reasoning_en": f"{loc_info['name_en']} is relatively safe during this period.",
                    "location_info": loc_info
                }

        return {
            "level": base_danger,
            "reasoning": loc_info.get("description", ""),
            "reasoning_en": loc_info.get("description_en", ""),
            "location_info": loc_info
        }

    def format_context_for_prompt(
        self,
        search_results: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """Format search results into a readable string for LLM prompts.

        Args:
            search_results: Results from search_historical_context().

        Returns:
            Formatted string with historical context.
        """
        lines = ["## Historical Context\n"]

        # Events
        if search_results["events"]:
            lines.append("### Recent Events:")
            for event in search_results["events"]:
                date_str = f"{event['year']}年"
                if event.get("month"):
                    date_str += f"{event['month']}月"
                lines.append(
                    f"- **{date_str}** ({event['location']}): {event['title']} - {event['description']}"
                )
            lines.append("")

        # Locations
        if search_results["locations"]:
            lines.append("### Relevant Locations:")
            for loc in search_results["locations"]:
                lines.append(
                    f"- **{loc['ancient_name']}** ({loc['name_en']}): "
                    f"危险度 {loc['danger_level']}/100 - {loc['description']}"
                )
            lines.append("")

        # Survival tips
        if search_results["survival_tips"]:
            lines.append("### Survival Guidance:")
            for tip in search_results["survival_tips"]:
                lines.append(f"- {tip['situation']}: {tip['advice']}")
            lines.append("")

        return "\n".join(lines)


# Module-level convenience function
_default_archive: Optional[HistoricalArchive] = None


def search_historical_context(
    year: Optional[int] = None,
    location: Optional[str] = None,
    month: Optional[int] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Convenience function for searching historical context.

    Uses a singleton HistoricalArchive instance.

    Args:
        year: Year to filter events.
        location: Location name to filter.
        month: Month to filter events.
        tags: Tags to filter by.

    Returns:
        Dictionary containing filtered historical data.
    """
    global _default_archive
    if _default_archive is None:
        _default_archive = HistoricalArchive()

    return _default_archive.search_historical_context(
        year=year,
        location=location,
        month=month,
        tags=tags
    )
