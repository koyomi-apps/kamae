# Kamae

Kamae is a workout journal built around your training days: plan your split once, then pick a day and tick off your sets. It's free and open source, for iPhone and Android, with no accounts, no ads and no internet access. Its website is [kamae.fromkoyomi.org](https://kamae.fromkoyomi.org).

**Status:** beta. Kamae for iPhone is on TestFlight, and Kamae for Android has test builds.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/readme-dark.png">
  <img src="docs/screenshots/readme-light.png" alt="Four of Kamae's screens on iPhone: today's training day and its exercises, a workout with its sets ticked off and the rest timer running, Deadlift's page with an animated figure and the muscles it works, and the You page with this week's energy and the muscles worked in the last 7 days">
</picture>

More screenshots of the iPhone app, in light and dark mode, are in [docs/screenshots](docs/screenshots).

## Try it

### iPhone

Join the beta at [testflight.apple.com/join/GTKbw4Hg](https://testflight.apple.com/join/GTKbw4Hg) on an iPhone with iOS 26 or newer. The link opens Apple's TestFlight app, which installs Kamae and keeps it up to date. Send feedback from TestFlight, or report bugs and ask for features in [the issues](https://github.com/koyomi-apps/kamae/issues).

To sideload it instead, each iPhone [release](https://github.com/koyomi-apps/kamae/releases) (tagged like `ios-v1.0-5`) has an IPA for AltStore, SideStore or Sideloadly, which sign it with your own Apple Account. With a free account, the app stops opening after seven days until it's refreshed, and it uses two of the account's App IDs, one of them for the rest timer on the Lock Screen. Sideloaded copies don't update by themselves and keep their data apart from the TestFlight one; move between them with a backup. What's new in each build is in the [changelog](ios/CHANGELOG.md).

### Android

Test builds for Android 8.0 or newer are pre-releases on [the releases page](https://github.com/koyomi-apps/kamae/releases) (tagged like `android-v0.9.2`), each with an APK to install. Version 1.0.0 is planned for F-Droid as well.

To bring your plans and workouts from another phone, back up there and restore the backup on Kamae's welcome screen.

## Features

- **Training days first:** named training days, sets planned ahead, plans that keep up with you, empty workouts when you'd rather wing it, a rest timer, exercise pages with animated figures, history and stats
- **A real app on each phone:** on iPhone, iOS's own navigation, sheets and menus, with the rest timer on the Lock Screen and in the Dynamic Island; on Android, Material 3's, with the rest timer in a notification
- **Private:** no accounts and no internet access. Your data stays on your phone
- **Backups that work across platforms:** a backup from either app restores in the other

## The name

構え (*kamae*) is Japanese for a stance: the set, ready position you take before you move, as in kendo or karate. In the gym it's the moment before a lift, feet planted and grip set, when the work begins.

## Building

This repository has Kamae for iPhone, written in SwiftUI, in `ios/`, and Kamae for Android, written with Jetpack Compose, in `android/`. Their data and rules are a Kotlin Multiplatform module the two share, in `shared/`, so both apps store, count and back up the same way. The website is in `docs/`.

**iPhone:** open `ios/Kitae.xcodeproj` in Xcode 27. Xcode builds the shared Kotlin module with Gradle in a build phase, so the Mac needs a JDK 17 or newer as well, such as Temurin 17 (`brew install --cask temurin@17`); Android Studio's works too. The first build downloads Kotlin's iOS tools, so it takes a while.

**Android:** open the repository in Android Studio, or build with Gradle, a JDK 17 and the Android SDK: `./gradlew :android:assembleDebug`.

## Credits

Kamae's design and backup format go back to Kenko, by LooKeR, though Kamae contains none of its code.

## License

```
Kamae
Copyright (C) 2026 Kamae Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

### Additional permission for Apple's App Store

```
Additional permission under GNU GPL version 3 section 7

Apple's App Store and TestFlight place restrictions on the people who
install apps through them that the GPL would not otherwise allow. As an
additional permission, the copyright holders allow you to convey this
program, or a work based on it, through those services anyway, provided
that you comply with the GPL in every other respect, including making the
Corresponding Source available as section 6 requires.
```

Contributions are accepted under these same terms, including this permission.
