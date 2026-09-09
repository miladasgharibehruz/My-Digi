My Digi V4 - GitHub Release Package

WHAT IS FIXED
- My Digi opens in its own pywebview window and never uses Edge as the main-window fallback.
- The official icon is embedded in the EXE, installed beside it, and assigned to Desktop/Start Menu shortcuts.
- The Desktop shortcut is enabled by default.
- GitHub Release detection uses the official GitHub Releases API.
- If the GitHub API or Windows proxy is blocked, update checks retry directly and use the GitHub Releases page as a fallback.
- The application version and installer version are generated automatically from the release version.
- The installer and its SHA-256 checksum are published together and verified before an update.
- Before installation, both the installed application and user data are backed up.
- The newest three backups are retained and application rollback remains available.
- Settings now includes complete data-backup management: create, list, inspect, restore, delete, and open the backup folder.
- Restoring data first creates an automatic safety snapshot of the current state.
- Update activity and errors are written to: %APPDATA%\My Digi\update.log
- Detailed Inno Setup output is written to: %APPDATA%\My Digi\installer.log
- If silent installation is aborted, the updater retries with a visible installer instead of silently stopping.
- The Settings update panel shows whether the last update succeeded or failed.
- The version badge at the bottom of the main menu is generated dynamically as Vx.y.z from the installed application version.
- Backup restore/delete and update confirmations always appear above the Settings dialog.
- The Settings scrollbar now matches the dark cyan/blue My Digi interface.
- A themed Health Center is available above Settings in the right menu.
- The Health Center tests internet, Digikala, GitHub updates, JSON data integrity, backups, update state, free disk space, monitor activity, and recent errors.
- Health reports can be copied or saved to Downloads; malformed data repair first creates an automatic safety backup and archives the damaged file.
- pywebview startup errors are written to: %APPDATA%\My Digi\startup-error.log

HOW TO PUBLISH AN UPDATE
Option 1 - easiest:
1. Upload/commit the changed project files to GitHub.
2. Open GitHub > Actions > Build and Publish My Digi > Run workflow.
3. Enter a NEW x.y.z version, for example 2.0.1, and run it.
4. Wait for the green completed status. The workflow creates the Release automatically.

Option 2 - Git tag:
1. Push a new tag such as v2.0.1.
2. The workflow builds and publishes the matching Release automatically.

IMPORTANT
- Every update must have a version higher than the version already installed.
- Use x.y.z numeric versions only.
- The GitHub repository must be public for update checking without a private access token.
- The Release must contain My-Digi-Setup.exe and My-Digi-Setup.exe.sha256.
- Do not rename those two Release assets.
- On Windows, Microsoft Edge WebView2 Runtime must be installed. It is normally already included in current Windows 10/11 systems.

USER DATA
Live data remains in %APPDATA%\My Digi.
Backups are stored in %APPDATA%\My Digi\versions.
Rollback restores the older application while keeping current live user data intact.
Each backup also contains a separate data snapshot for manual disaster recovery.
