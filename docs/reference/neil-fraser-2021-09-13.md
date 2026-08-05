# Neil Fraser — Meccanoid firmware notes (2021-09-13)

Source: https://neil.fraser.name/news/2021/09/13/

---

Neil Fraser: News: Meccano Firmware Updater
  
  
  
  
  
  
  

Neil's News

&nbsp;2026
&nbsp;2025
&nbsp;2024
&nbsp;2023
&nbsp;2022
&nbsp;2021
&nbsp;Freedom&nbsp;Revisited
&nbsp;Sierra's&nbsp;Graduation
&nbsp;First&nbsp;Dance
&nbsp;Meccano&nbsp;Firmware&nbsp;Updater
&nbsp;Guerrilla&nbsp;Painting
&nbsp;Fixing&nbsp;Code-a-Pillar
&nbsp;Catchment&nbsp;Area
&nbsp;JavaScript&nbsp;Loops
&nbsp;Lego&nbsp;Storage
&nbsp;Five&nbsp;Years
&nbsp;JavaScript&nbsp;Chain&nbsp;Reaction
&nbsp;Play&nbsp;Well
&nbsp;2020
&nbsp;2019
&nbsp;2018
&nbsp;2017
&nbsp;2016
&nbsp;2015
&nbsp;2014
&nbsp;2013
&nbsp;2012
&nbsp;2011
&nbsp;2010
&nbsp;2009
&nbsp;2008
&nbsp;2007
&nbsp;2006
&nbsp;2005
&nbsp;2004
&nbsp;2003
&nbsp;2002

Meccano Firmware Updater

13 September 2021

Meccano released a family of robots that include basic computer modules: Meccanoid, Micronoid, and M.A.X.  The firmware on these computer modules can be flashed with new ROM images in order to change language or change capabilities.  Unfortunately, Spin Master (Meccano's current owner) has abandoned the entire product line.  The software to flash these modules isn't available for download any more.  And even if you do have a copy, it includes hard-coded URLs back to meccano.com for mandatory assets which no longer exist.

I own six Meccanoid robots which I use for teaching young children and coworker activities.  I have to be able to flash the firmware.  Let's fix this.  Here's how to update your Meccano robots:

Download the update tool for Windows (XP through 10 are known good).
Install it.  But don't bother running it, it will fail when it tries to fetch configuration that no longer exists on meccano.com.
Download a replacement MeccanoFirmwareUpdate.exe and overwrite your current version.
Run MeccanoFirmwareUpdate.exe and follow the instructions.

The replacement version has been modified to fetch multi_language123.json and meccano123.json from my server.  I also took copies of all the binary images, since I've got zero confidence that they won't also disappear without warning.  One issue is that https is not supported by whatever library is fetching the files, so I had to spin up an http server just for this.

Sadly the OSX version is no longer viable.  It suffered from the same issue with hard-coded URLs.  But after fixing that issue, it just stops.  It appears that an incompatibility appeared somewhere in OSX version 10.13 (High Sierra), 10.14 (Mojave), or 10.15 (Catalina).  Not much I can do about that without the source code.

Update: Spin Master have deleted their Meccanoid apps from the Android and Apple app stores.  Fortunately I've archived the last version of the Android Meccanoid App.  It still runs as of 2021.  Previous versions are non-functional due to Android API changes and dependencies on a now non-existent login system on the Meccano servers.  Unfortunately I don't have an archived copy of any of the iOS versions for Apple devices.

Note to Spin Master: I own Meccano that's over 100 years old and it still works as well as it did the day it was bought.  Your stuff turns into bricks in less than five years.  If you don't care about your products, open source it so that your customers can maintain it for you.

&lt; Previous | Next &gt;

&nbsp;

Legal yada yada: My views do not necessarily represent those of my employer or my goldfish.

Neil Fraser: News: Meccano Firmware Updater
