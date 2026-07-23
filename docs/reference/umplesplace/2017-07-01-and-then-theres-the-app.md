# And then there's the App

Source: https://umplesplace.wordpress.com/2017/07/01/and-then-theres-the-app/

Archived locally for Meccanoid research (umplesplace).

---

MeccaNoid Android Application Version 2.4 (31)

A year waited for and a few waited longer before Application with " Behavior Builder"showed up in Android Market.

Open Source. yaaaaa. Funny. When Meccano / Spin Master declare properly what is and what isn't "Open Source" of what has been released then I will take it more seriously instead of a buzz-word sales tactic.

Copied from the Meccabrain.cpp Arduino IDE library posted on Meccano.com websiteinside a compressed folder named "meccanoid library" as of June 26, 2017:

""

/*

LEGAL NOTICE:

Meccanoâ„¢, MeccaBrainâ„¢, MeccanoTechâ„¢ and Meccanoidâ„¢ are trademarks

of Meccano. All rights reserved.

The information contained in this document is Proprietary to Spin Master Ltd.

This information should not be used in the creation and sale of any commercial

product.â€

*/

""

That bit of text in the header of program Library made freely available to me says: NOT OPEN SOURCE. I guess there's no web resources describing Open Source. NOT.

It is reasonable to assume API is free for use with Meccano hardware. IMO.

********//// The Meccanoid Arduino Library is not complete and has typos,errors.  Meccano_Smart ModuleProtocols_2015.pdf has same. Library does nothing by itself and requires a program written by You or someone else brave enough. It is an Application Programming Interface (API). It implements low level protocols used by Meccano servos and modules made available by inclusion (#include) in user program.

Basically it's a translator so your program can talk to Meccanoid hardware through whatever microcontroller.

******It is not a Meccabrain  control program and as of present

Meccabrain is a closed system.  The use of Meccabrain name in its declaration in Library is misfortunate and adds to confusion. It would be nice if Meccano would release the BLE controls protocols so actual Meccabrain could be used in true Open Source. \\\\*********

It really is disappointing to diminish a perfectly usable 16 bit processor to a singular use when could easily be left open. *sniff* some blue.

*Sigh.*

Perspective:

I've been Building robots and electronics way too long.

I'm a long-time' fan of Meccano and Erector. From the disappointing 70's of Erector to the glory of Meccano up to 90's and A.C. Gilbert Erector Type II sets far Older than me; there will always be a fondness.

So when Spin Master manned up a Meccano(id) Robot I was thrilled. Honestly.

Was almost preschool child like giddiness on Christmas eve night thing.

Robotics and Meccano. My favorite hobby and construction toy. I already had a pictured model in mind with all the elegance of past Meccano gorgeous fine tooth brass gears, and style of Type II Erector, with modern flare for a New Generation and big HONKING hulking powerful motors like yester years. Now with: stand alone semi-autonomous programmable microcontroller, servo control , modern batteries, fancy L.E.D. lighting and color changing, modern voice synthesis, and array of sensors.  Of course there had to be WIFI and Bluetooth. Duuuuhhhh. Another assumption would be odometery on drive wheels or at very least a reliable Navigation of some kind.

Ah sweet fantasy.

*POP* goes the bubble.

Reality sucks.

Got some bit of what fantasized anyhow and usable voice control. Sea Monkeys anyone? Alright not that bad- mostly. No sonar either. Is like: but everybody else has one on their systems. Well if everybody else jumped off a cliff — Yup probably in this instance. Of course without sonar, Infrared, or other way of determining the edge of cliff it can be reasoned that leg motors will continue to push forward til gravity forces ugly termination of program. The original drop down and through programming style.

So with that in mind:

Some of this is me whining and venting.

Some may be constructive criticism.

 

Meccanoid Android Application.

Don't know about that other thing or those Other fruity things.

Overly fat power sucking Unity stuff. Not picking on Unity. Is good portable library on multiple platforms but can be taken to less than good use. Seriously bad processor / battery drain for what appears to be doing little to nothing.

Ummm.... Program audio control? Oh. No. Turn your volume off and on manually on your smart-er device.

Besides bad sound effects are much better than anything else you might need or want to hear.

3D Ragdoll Avatar on 2D display more work than useful.

Would it have been so difficult to put icon on the sides with backward -forward-left-right? I get it. It skid steers like a tank. Differential. Can think of at least a half dozen better ways to do this than having to press two icons to go forward, wait for Avatar to turn around, and then use two other icons.

Ragdoll Slider controls better but lack edit labeling and specific positioning or speed control. They do have labels now but too generalized: Head, Left Arm, Right Arm, Feet and Eyes.   Labels only there in offline not connected to Meccanoid. Needs work.

Color wheel selection of LED lights on servos and LED light bar are fairly simple and allows transition speed for light bar. So one thing I cant really complain about. Wait a bit and some complaint will manifest.

         
 
         
 
  
  

I've seen the LED light bar referred to as Smart LED Servo with other names. Check definition of the word servo'.

It's not a servo mechanism. The official name in the construction manual is "Head LEDs" and "eyes". Elsewhere "Smart LED module"," Programmable LED Eyes". According to Owen Lu it's "Meccanoid Brain - RGB LED". That's hardware and so back to APPlication program.

All is limited by a timer based storage window which must be saved once full or "new"ed out. Needing to start another session. That can be irritating when desiring only to drive bot around. No setting for turning off recording session and run continuous.

No reasonable way to edit what was made either.

>>>Motion Capture was cool but again no editing and it needed it. Shadow gets confused and messes up an otherwise perfect sequence. Motion capture is no longer available sadly. Supposededly replaced by "drag and drop" AKA "Behavior Buider".

Don't know which is worse name. Alternatively I like to call it Crazy ArRoWs. That is excluding a list of derogatory names. <<<.

Shut off App or Blue Tooth and robot returns to dumby. The illusion of autonomy gone.

Not dumby really. Plays a bit. Have L.I.M. to work with.

Who thought using BLE (BlueTooth Low Energy) cutting off large number of available devices was a good idea?

BLE also tends to be on newer more expen$ive devices.

Drag to death and drop in trash programming. "Behavior Programming".

Crazy ArRoWs everywhere and sometimes can't always see where they're going.  Often not to where intended. Drag to point intended. Drop. Goes somewhere near butnot where needed or not at all. Combines several elements together that were never intended. Sure, watch the little red dot pop on and out in modules while program runs.

Ya. Sucks.

Damn it dropped wrong place. Drop in trash working elements so can fix. Redo.

Lack of OOPs or BACK or Undo buttons. What the smeg?

Single step backup at least.... come on- sheeeesh.

Maybe start from SCRATCH' and work upward. Top-downward? Freaking 1980's Turtle language maybe? LOGO, Pilot, Forth with Turtle, anything. I would welcome BASIC here or Micro C'. Ya know like the Arduino but without having to buy an 8bit MCU when a 16 bit is already there and 32/64bit speed demon number cruncher in Smart Device. There's a bad pun and a suggestion there somewhere.

For navigation ... nothing. It has no odometery. Turn driving motor(s) on for  x  seconds at unknown speeds labeled very slow to very fast. 5 seconds minimum at very slow single drive or differential gets about 90 degrees turn. So much for fine control. Can use Ragdoll to make a recording for less run time on motor but still sad. Worse is Ragdoll recordings may not work as entered in Bad "Behavior".

Lack of environment input not helping. Could use some simple switch inputs minimum. Using a servo's feedback silly but it's there. Not great mostly due to losing a servo to do it. Can be worked around.

Dragging four menu buttons out of the chest (Meccabrain) to something and some where more useful comes to mind. More on that laters. maybe. Ha. Assuming Crazy Arrows can handle it.

Has voice control but no method to implement in programming. Yes or No response to question would be nice.

There is no provision in App for saving programs externally. Alternatively snag programs and sounds from Android file structure but will not include  L.I.M. which is on Meccabrain. Have to use a File Manager as there is no provision in program. Assuming access to files not blocked by firmware and permissions on smart device.

***Drone Mode: Another issue with "Behavior" is that it may not let you make a program if less than four servos are attached. If it does it may not work. Nothing happens or only some work. Sliders under Ragdoll may not work either. They go up and down without response on Meccanoid. Especially on channel 1 servo socket. Channel 8 sometimes works. The start star' wont be there with less than four servo in some modes and certain sockets.

More Quarkiness. Configuration that usually has no problems is at least 2 servos on slot 1 and 2 servos on slot 3. Which not surprisingly follows G15 original wiring and it's

Dino variant. Drive motors always seem to work.

True on G15 and G15KS.

Learned intelligent movement (L.I.M) recordings can be included into program.

L.I.M. seems to have no trouble but not reasonable to try all variations of slots and servos. Unlike App, LIM will recognize extra servos and record from them. App Programming and sliders may not.

LIM allows saving up to 15 recordings at about 3 minutes each. Approximately 45 minutes of recordings that can be used in Crazy Arrows and stand alone without App on Meccanoid.

Presently "Behavior" programming has numerous quirks and bugs.

A for instance or e.g.:

Setting any servo to LIMp to get a position may force all servos to LIMp. Once it gets what you asked it for everything goes back to active where last left them.

LIM(p) is the icon element for servo input where can be chosen a condition of less or minus 90 to -90 degrees of servo position. Smart servo disables motor on selected servo. Waits for servo position to match within a range entered.

180 degrees represented by a ~90 degree angle. Technical illustrator was where?

Work around bugs and bad representation to best patience will allow.

Wrapping it up:

Altogether a good toy. Far more of a programmable animatronic than programmable robot in ROBOT mode. Semantics somewhat. Drone mode allows more control and variant builds, but vast majority of capabilities in Robot Mode disappear including voice control. Not a big issue as I see it. Coolness factor 1.0 but noisy environment non functional.

Can and could be more of a learning system. S.T.E.M. worthiness questionable and limited at that. The sparse Maths in programming language particularly dissuades. There's some in there. Look harder. It will inspire a few kids into finding out more. Where inspiration is encouragement then yes it encourages STEM.

Can a child learn to program on one of the smart device compatible with Meccanoid and it's application? ***** Please note the qualifier compatible'.*****

Yes. Programs will have to be simple and will probably require much more thought and planning than should be necessary.

Learned intelligent movement (L.I.M) is cool. It's Meccanoid's programming' feature that doesn't require a smart device. A series of movements by motor servo position can be recorded and played back. Sound is also recorded through microphone. Servos turn off motor allowing them to be positioned within a range of 180 degrees with little resistance. I don't consider programming exactly. It is path mapping. Little more than Recorder with playback. Ragdoll allows re-recording over to a point in time by slider bar , but missing any reasonable definition and inability to edit. LIM doesn't allow stopping, back-track, or re-recording from a point in time so no editing either..

It should be noted that LIM likes to cut off approximately a second to two off the end ofa recording on some firmware. 2.8 firmware doesn't seem to have that problem.

Lack of Drive (foot motor) control in LIM LIMiting. If LIM can be moved to a programming or at least event scheduler environment that would allow editing or conditionals then it would be programming.

LIM recordings can be included in Drag and Drop programs. The programming part of App lists LIMs by number not given audible name. Write down which is what recording in order helps.

Don't remember order or which ones? Ask Meccanoid to list them. It will in order by the name given.

Crazy ArRoWs errr, um,  "Drag and Drop" AKA "Behavior" programming environment is NOT polished and lacks basic editing capabilities. It has quirks that may likely lead to a disdain after a period of time. May be a patience endurance test. I have an evergrowing list of Bugs, Quirks, and various dysfunctions.

Frustration is what is NOT wanted for young folk.

If noticed frustration then it's time to move on to:

*Arduino also Genuino. Uses Meccanoid free Library. The Arduino company has split up a bit. Another topic in itself with the addition that processor manufacturer Atmel (ATMega) and PIC Microchip also are an issue somewhat. A PIC processor can also be used but it has its' own IDE. Online Support communities vary. Arduino in my opinion the greater. Leaning towards cheap *uino knock offs myself lately.

*Other microcontroller control. Like Texas Instruments (TI LaunchPad) or ESP - 8266/32 by Espressif , or ST Thompson ST8 , or ________ . ESPs being popular due to WIFI and 32s' bluetooth and dirt cheap.

Many other MCU manufacturers have adopted the open IDE for programming.

Raspberry Pi (Linux) is a virtual machine' and does best with the help of a microcontroller. It can do some low level but timing gets tricky.

Older model Pi like the B less power then the newer Pi2 (B) but still looking at around 1.5-2 Amps @ 5VDC. Pi2 is faster but likes more power. 2.5A average so far. RPi2 has a little lightnig icon show up on display when power goes brown. Power sucking an issue. AA NiMh not gonna do it for long. Maybe several banks. Probably should check to see how much the little feet motors can handle weight wise.

RPi does have Scratch and other programming languages. Is easily the most supported SOC (system on chip).

********//// The Arduino Library and "Open Source" Protocol are not complete and have errors. Library does nothing by itself and requires a program written by the User to implement the protocols used by Meccano servos and modules made available by its' inclusion' in program. It is not a Meccabrain  control program and as of present Meccabrain is a closed system.  The use of Meccabrain name in its declaration in Library is misfortunate and adds toconfusion. \\\\*********

*one of the other building systems and respective related controllers and software.

They all have strengths and weakness. Meccanoid not only helps build itself when Meccabrain is running, it is also pre-programmed to perform under Robot Mode.

UNFORTUNATELY if u have original G15 it NEEDS the update from 1.0 firmware via USB and Robot Updater program running on PC.

Meccanoid Expansive? No not directly other than buying more servos. Servos addedmay require some experimenting to get to work with Application. LIM does work tho. Meccabrain 2.0 is out for ~50$US to replace G15 Meccabrain. Not feeling it. A good microcontroller with an IDE (Integrated Development Environment) would be far more useful add on. Adding other erector sets with servos and a better APP would be ideal.

Irregular shaped pieces would likely be substituted out for conventional Meccanoand/or Erector pieces.

Home computer free or self sustained it is NOT. Needs firmware updateminimum. Going further with "drag n drop" programming requires an Application programrunning in another computer smart device with BlueTooth LE (BLE) capability. More devices being incompatible then compatible. Cheap tablet thoughts vanish. This will change as BLE comes to be more standardized in newer devices. No Desktop or laptop versions of programming language available yet, and yet requires USB interface for firmware updates.

Been holding back and is good to let out. I was holding out for would had been fixed. Apologies for all the Quotations but needed to make clear that my terminology may notmatch others or the term-name-intention is not mine. Hopefully helps someone.

Yes I could go on, and will. Laters.
