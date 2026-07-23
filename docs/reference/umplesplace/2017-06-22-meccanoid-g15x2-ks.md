# Meccanoid G15X2-KS

Source: https://umplesplace.wordpress.com/2017/06/22/meccanoid-g15x2-ks/

Archived locally for Meccanoid research (umplesplace).

---

June 22, 2017

Meccanoid G15X2-KS.

Power Dwarf.

Good for pushing over G15KS and XL.

Hah.

X2-KS is for the second G15 that was scavenged for its parts and KS firmware flash to handle four additional servos in KS configuration. Kept short in stature for now.

Stay tuned for G15-X2KS Texan. Which may or may not happen. G15 servos (AKA CAM 03, Blues) aren't as powerful as G15KS( DEV-06 Yellow) and will go Arduino or ESP8266 with an Arduino. Necessary for what I want to do.

I like the KS firmware voice soooooo much better than Lollipod Kid helium huffing Wizard of Oz G15 voice. Anyway... alternative build.

Systems Check

Another firmware is out for G15: English US G15(and KS)-2.8.

Not exactly sure what this adds or fixes.

It does NOT fix "Adjust Volume" voice command. Still stuck in SET ALARM response.

KS and G15 versions.

The only option to adjust volume right now is download the English UK - 1.9 firmware.  Use "Adjust Volume" voice command in settings menu to set where you like and then re-flash 2.8 firmware. Of course you have to suffer horrid British accented Meccanoid fora bit. Was waiting for to go Mary Poppins song step. Didn't happen thank goodness.

I suggest highest volume and just tape over speaker if needed.

Of course if you speak another language can try flashing that.

The 2.8 firmware has more features than the 1.9 firmware for ROBOT Mode.

If you're running in DRONE Mode then probably don't need it.

Sad? Yes. Sadder still: Why is the UK ROM stuck in 1.9 land o the past?  I'm conflicted that it's useful for back-stepping but don't fathom why UK version is neglected.

Then out of curiosity I clicked off the different languages through the Robot Updater

and fOuNd:

Language: Firmware Version G15 / G15KS:

English (UK) 1.9 / 1.9

French 1.7 / 1.8

Spanish EU 1.6 / 1.7

Italian 1.5 / 1.6

German 1.4 / 1.5

Russian 1.2 / 1.3

Japanese 1.10 / 1.11

Dutch 1.3 / 1.4

Spanish Americas 1.0 / 1.0

Danish 1.2 / 1.2

Swedish 1.1 / 1.1

Norwegian 1.0 / 1.0

and hopefully to embarass:

English US 2.8 / 2.8

Wow 1.0. Seriously ugly stuff. For the G15-US-1.0 was horrible because of battery voltage reading was set too high and would shut Meccanoid G15 down within a few minutes (about 10-20 minutes) with there being plenty of life left in batteries..

Programmers dropped the ball or ran away?

Somebody must have spooked them or there's a shortage

of tater chips, popcorn, caffeinated drinks, and coffee in certain places.

Possibly a cheese curls deficiency.

Though reasoning suggests a relatively unknown processor / parts and lack of

documentation in anything other than Chinese is not helping.

Mentioning China and not seeing a Chinese firmware.

Fuse blown there.

NOTE: Flashing new firmware results in Meccabrain doing a diagnostic which must be completed in ROBOT Mode or App will lock out. The completion of startup system check requires all servos for whichever ROBOT (G15 or G15KS) and light bar be in the jacks in accordance with directions. Drone Mode in App will also be locked out.

Meccabrain will operate in Drone mode but not the App.

***No you don't need to build the robot to complete diagnostic. Need servos, Smart LED bar, battery and of course Meccabrain in proper order as if they were installed in Robot. You can leave the foot motors disconnected but that may change with newer firmwares.

I'm sure the hacking community has moved to their own hardware and

only using "smart" servos and Meccanoid pieces. Fairly slow.

I have heard some bitching about parts not being Meccano or Erector style. Only compatible. Pieces aren't what die-hard fans are used to and don't exactly promote free thought open build mentality. Shapes are irregular and not typical Erector / Meccano simple shapes. They also have pinned keys limiting use. Interlocking pins of new parts requiring orientation have more to do with slow build times and aggrevation.

That's my opinion partially based on  evidence.  Half-inch standard still theremostly. Being made of plastic not helping standing with the classic folks.

Poorly documented protocol under the open source' mantra. Not really open source and is only for Arduino program that communicates (protocol) to servos and light bar.

Meccabrain , not the Arduino program "Meccabrain" , locked out. Not OPEN Source.

Well mostly. There's no reason why protocols can't be abused to further capabilities of Meccabrain with other hardware as servos.. Still limited in programming through Application program which really isn't that good. Usable but unpolished and quirky. Is good thing protocol was released with Arduino code. Meccabrain(tm) mostly for starter use. Any reasonable advanced use limited. Voice control is cool but practicality dysfunctional. It is a decent micro but its stuck pedantic cute-ware and BLE comms thru App'. L.I.M. is nice idea but inability to save off line and transfer to other devices makes it barely useful and anti-social. Yes this robot is anti-social but it can joke about it... so it's fine. No driving motors control available through LIM but may be hidden. Inability to shut off sound recording whilst programming

in L.I.M. also sucking useless. Inability to add sounds to Meccabrain without motion equally irritating. Tape to the rescue again. Right over the MICrophone hole. Not100% effective but what-eee-ver you need to do to achieve desired results.

**** Limitation of L.I.M is roughly 3 minutes times up to 15 programs. ****

So technically up to 45 minutes of L.I.M time but only 15 labels..Don't know if that will change.

 

Yes I could go on, and will. Laters.
