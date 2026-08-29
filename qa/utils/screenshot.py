from datetime import datetime
from pathlib import Path


def capture_screenshot(driver, directory: Path, test_name: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(character if character.isalnum() or character in "-_" else "_" for character in test_name)
    path = directory / f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    driver.save_screenshot(str(path))
    return path
