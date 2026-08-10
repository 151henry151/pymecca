# Meccano Firmware Updater

Source: https://neil.fraser.name/news/2021/09/13/

Meccano Firmware Updater

13 September 2021

Meccano released a family of robots that include basic computer modules: Meccanoid, Micronoid, and M.A.X.  The firmware on these computer modules can be flashed with new ROM images in order to change language or change capabilities.  Unfortunately, Spin Master (Meccano's current owner) has abandoned the entire product line.  The software to flash these modules isn't available for download any more.  And even if you do have a copy, it includes hard-coded URLs back to meccano.com for mandatory assets which no longer exist.

I own six Meccanoid robots which I use for [teaching young children](https://neil.fraser.name/news/2016/10/28/) and [coworker activities](https://neil.fraser.name/news/2016/11/14/).  I have to be able to flash the firmware.  Let's fix this.  Here's how to update your Meccano robots:

- Download the [update tool for Windows](https://neil.fraser.name/software/meccanoid/RobotUpdaterSoftwareV1.28.5.zip) (XP through 10 are known good).

- Install it.  But don't bother running it, it will fail when it tries to fetch configuration that no longer exists on meccano.com.

- Download a replacement [MeccanoFirmwareUpdate.exe](https://neil.fraser.name/software/meccanoid/MeccanoFirmwareUpdate.exe) and overwrite your current version.

- Run MeccanoFirmwareUpdate.exe and follow the instructions.

![[Windows XP dialog confirming replacing file]](https://neil.fraser.name/news/2021/copyLoader.png)

The replacement version has been modified to fetch [multi_language123.json](http://http.neil.fraser.name/mcnoid/multi_language123.json) and [meccano123.json](http://http.neil.fraser.name/mcnoid/meccano123.json) from my server.  I also took copies of all the binary images, since I've got zero confidence that they won't also disappear without warning.  One issue is that https is not supported by whatever library is fetching the files, so I had to spin up an http server just for this.

Sadly the [OSX version](https://neil.fraser.name/software/meccanoid/RobotUpdaterSoftware_V1.23.pkg) is no longer viable.  It suffered from the same issue with hard-coded URLs.  But after fixing that issue, it just stops.  It appears that an incompatibility appeared somewhere in OSX version 10.13 (High Sierra), 10.14 (Mojave), or 10.15 (Catalina).  Not much I can do about that without the source code.

Update: Spin Master have deleted their Meccanoid apps from the Android and Apple app stores.  Fortunately I've archived the last version of the [Android Meccanoid App](https://neil.fraser.name/software/meccanoid/Android/Meccanoid_v4.02.48.apk).  It still runs as of 2021.  Previous versions are non-functional due to Android API changes and dependencies on a now non-existent login system on the Meccano servers.  Unfortunately I don't have an archived copy of any of the iOS versions for Apple devices.

Note to Spin Master: I own Meccano that's over 100 years old and it still works as well as it did the day it was bought.  Your stuff turns into bricks in less than five years.  If you don't care about your products, open source it so that your customers can maintain it for you.

[![[Beverly and Meccanoid]](https://neil.fraser.name/news/2021/beverly-meccanoid-small.jpg)](https://neil.fraser.name/news/2021/beverly-meccanoid.jpg)

< [Previous](../../../2021/09/06/) | [Next](../../../2021/12/06/) >
