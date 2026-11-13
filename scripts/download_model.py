"""Download the configured YOLO model weights."""

from config import load_settings
from models.model_loader import ModelLoader


def main() -> None:
    settings = load_settings()
    loader = ModelLoader(settings.model.name, settings.model.device)
    loader.load()
    print(f"Loaded {settings.model.name} on {loader.resolved_device}")


if __name__ == "__main__":
    main()
