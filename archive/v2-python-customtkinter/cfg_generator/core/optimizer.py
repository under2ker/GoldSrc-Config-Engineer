from .generator import CfgConfig, get_hardware_data


def get_gpu_vendors() -> list[tuple[str, str]]:
    hw = get_hardware_data()
    return [(k, d.get("name_ru", d.get("name_en", k)))
            for k, d in hw.get("gpu_vendor", {}).items()]


def get_performance_profiles() -> list[tuple[str, str]]:
    hw = get_hardware_data()
    return [(k, d.get("name_ru", d.get("name_en", k)))
            for k, d in hw.get("performance_profiles", {}).items()]


def optimize_config(
    cfg: CfgConfig, gpu_vendor: str, performance_profile: str
) -> tuple[CfgConfig, list[str], str]:
    """Apply hardware optimizations. Returns (config, tips, launch_options)."""
    hw = get_hardware_data()

    tips: list[str] = []
    launch_options = ""

    gpu_data = hw.get("gpu_vendor", {}).get(gpu_vendor)
    if gpu_data:
        cfg.merge(gpu_data.get("optimizations", {}))
        tips = gpu_data.get("tips_ru", gpu_data.get("tips_en", []))

    profile_data = hw.get("performance_profiles", {}).get(performance_profile)
    if profile_data:
        cfg.merge(profile_data.get("settings", {}))
        launch_options = profile_data.get("launch_options", "")

    return cfg, tips, launch_options
