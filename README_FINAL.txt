My Digi 2.0 — Final Windows Release Package

This package contains the final application source, updater helper, installer definition, official icon, and GitHub Actions release workflow.

Key final-release behavior:
- Clean first-run data: no test products or test suppliers are included.
- User data is stored under %APPDATA%\My Digi and is separate from installed program files.
- Standard Windows installation with selectable installation directory.
- Desktop shortcut is optional; Start Menu shortcut is created.
- Standard Windows uninstall entry.
- In-app update checking with release notes.
- Automatic backup of the installed program before update.
- Rollback to a retained previous program version.
- SHA-256 verification when GitHub exposes the release asset digest.
- GitHub repository is read from update_config.json.

Before the first online release, set the repository in update_config.json to the GitHub owner/repository, e.g.:
  {"repo":"OWNER/My-Digi"}

The included .github/workflows/release.yml builds the Windows EXEs with Python 3.13 and packages the installer with Inno Setup on GitHub Actions.
