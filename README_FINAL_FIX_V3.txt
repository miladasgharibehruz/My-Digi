My Digi - V3 fixes

1) Update checker:
- Empty update_config.json no longer overrides the built-in GitHub repository.
- Built-in repository is miladasgharibehruz/My-Digi.
- Stable published releases are selected from GitHub Releases.

2) Taskbar icon:
- Removed the fragile pywebview before_show native-icon hook that could throw and force the browser fallback.
- Set a Windows AppUserModelID at process startup before any GUI is created.
- Main window now stays in pywebview EdgeChromium instead of falling back to Edge --app when that hook fails.
- The EXE's embedded My Digi.ico remains the application icon.

No Digikala monitor/parser logic was changed.
